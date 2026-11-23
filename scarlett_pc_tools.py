"""Inspect local packages and run bounded native or CPU-emulated startup diagnostics."""
import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import signal
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET

RUNTIME_URL = "https://github.com/LooperSalty/AnyXboxX"
RUNTIME_REVISION = "8a29203aaf81196489ed97dcd4ac9f78dfa2f5c0"
LEONIDA_URL = "https://github.com/ItsNotRexed/Leonida"
LEONIDA_REVISION = "1cc6e3c121969761d9dad8fdec99f19928213973"
CONSOLE_DLLS = {"xmem.dll", "d3d12_xs.dll", "xg_xs.dll", "chad.dll",
                "xapu.dll", "acphal.dll", "xcrdapi.dll"}


def outside_git(path):
    path = Path(path).expanduser().resolve()
    if any((p / ".git").exists() for p in (path, *path.parents)):
        raise ValueError("Keep dumps and diagnostic reports outside Git checkouts.")
    return path


def package_exe(target):
    target = outside_git(target)
    if target.is_file():
        return target
    config = target / "MicrosoftGame.Config"
    entries = list(ET.parse(config).getroot().iter("Executable"))
    entries = [e for e in entries if e.get("TargetDeviceFamily") == "Scarlett"]
    if len(entries) != 1:
        raise ValueError("Expected exactly one Scarlett executable in MicrosoftGame.Config.")
    return destination(target, "", entries[0].get("Name", ""))


def destination(root, folder, name):
    if not name:
        raise ValueError("Empty package filename.")
    path = (root / folder.replace("\\", "/").lstrip("/") / name.replace("\\", "/")).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Package path escapes the dump directory.")
    return path


def layout_status(folder):
    reports = []
    for layout in sorted(folder.glob("layout_*.xml")):
        chunks = []
        for chunk in ET.parse(layout).getroot().findall("Chunk"):
            files = []
            for group in chunk.findall("FileGroup"):
                a = group.attrib
                name = a.get("Include", "")
                if any(c in name for c in "*?"):
                    raise ValueError("Wildcard layouts are not supported by this inspector.")
                p = destination(folder, a.get("DestinationPath", ""), name)
                files.append({"path": str(p.relative_to(folder)), "present": p.is_file()})
            chunks.append({"id": chunk.get("Id"), "marker": chunk.get("Marker"), "files": files})
        reports.append({"file": layout.name, "chunks": chunks})
    return reports


def inspect(target):
    import pefile

    exe = package_exe(target)
    digest = hashlib.sha256()
    with exe.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(block)
    print("Reading PE imports (game code is not executed)…", file=sys.stderr, flush=True)
    with pefile.PE(str(exe), fast_load=True) as pe:
        pe.parse_data_directories([pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
        local = {p.name.lower(): p for p in exe.parent.iterdir() if p.is_file()}
        imports = []
        for library in getattr(pe, "DIRECTORY_ENTRY_IMPORT", []):
            name = library.dll.decode("ascii", errors="replace")
            imports.append({"dll": name, "file_present_in_dump": name.lower() in local,
                            "requires_console_runtime": name.lower() in CONSOLE_DLLS,
                            "functions": [x.name.decode("ascii", errors="replace") if x.name
                                          else f"#{x.ordinal}" for x in library.imports]})
        result = {"schema": 1, "executable": exe.name, "size": exe.stat().st_size,
                  "sha256": digest.hexdigest(), "machine": hex(pe.FILE_HEADER.Machine),
                  "entry_rva": hex(pe.OPTIONAL_HEADER.AddressOfEntryPoint),
                  "image_base": hex(pe.OPTIONAL_HEADER.ImageBase),
                  "imports": imports, "layouts": layout_status(exe.parent),
                  "notes": ["File presence does not establish integrity or runtime compatibility.",
                            "This tool does not decrypt, patch, or upload game content."]}
    return result


def write_json(path, value):
    path = outside_git(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def run_worker(command, output, timeout):
    output = outside_git(output)
    output.mkdir(parents=True, exist_ok=True)
    # One directory per attempt avoids mixing previous results with a timeout.
    output = Path(tempfile.mkdtemp(prefix="attempt-", dir=output))
    log = output / "boot.log"
    state = output / "boot.json"
    command = [*command, "--result", str(state)]
    start = time.monotonic()
    print(f"Starting diagnostic; report directory: {output}", file=sys.stderr, flush=True)
    env = {**os.environ, "PYTHONUNBUFFERED": "1", "LOCALAPPDATA": str(output / "state")}
    with log.open("w", encoding="utf-8") as stream:
        child = subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT, env=env)
        status = "finished"
        next_update = start + 5
        try:
            while child.poll() is None:
                elapsed = time.monotonic() - start
                if elapsed >= timeout:
                    child.kill()
                    status = "timeout"
                    break
                if time.monotonic() >= next_update:
                    print(f"Loading/emulating: {elapsed:.0f}s elapsed; see {log}",
                          file=sys.stderr, flush=True)
                    next_update = time.monotonic() + 5
                try:
                    child.wait(timeout=min(0.25, max(0.01, timeout - elapsed)))
                except subprocess.TimeoutExpired:
                    pass
        except KeyboardInterrupt:
            child.kill()
            child.wait()
            raise
        child.wait()
    summary = {"status": status, "exit_code": child.returncode,
               "elapsed_seconds": round(time.monotonic() - start, 2), "log": str(log)}
    if state.is_file():
        summary["diagnostic"] = json.loads(state.read_text())
    write_json(output / "summary.json", summary)
    return summary


def boot(target, runtime, output, timeout):
    if importlib.util.find_spec("unicorn") is None:
        raise ValueError('Install the boot extra: pip install -e ".[boot]"')
    exe = package_exe(target)
    if not exe.is_file():
        raise FileNotFoundError(exe)
    runtime = Path(runtime).expanduser().resolve()
    if not (runtime / "PrototypeScarlett/emu/machine.py").is_file():
        raise ValueError("--runtime must point to an AnyXboxX checkout.")
    worker = Path(__file__).with_name("scarlett_boot_worker.py")
    return run_worker([sys.executable, str(worker), str(exe), "--runtime", str(runtime)], output, timeout)


def positive(value):
    number = float(value)
    if not 0 < number <= 600:
        raise argparse.ArgumentTypeError("Choose a timeout greater than 0 and at most 600 seconds.")
    return number


def leonida_check(target, runtime, output, full_check=False):
    exe = package_exe(target)
    runtime = Path(runtime).expanduser().resolve()
    script = runtime / "make_game.py"
    if not script.is_file():
        raise ValueError("--runtime must point to a Leonida checkout.")
    output = outside_git(output)
    output.mkdir(parents=True, exist_ok=True)
    command = [sys.executable, "-I", str(script), "--game", str(exe.parent),
               "--out", str(output / "port"), "--work", str(output / "work"), "--check"]
    if full_check:
        command.append("--full-check")
    # The upstream checker writes no game content. Building/exporting is separate.
    return subprocess.call(command, cwd=runtime)


def leonida_run(target, loader, output, timeout, wine=None):
    exe = package_exe(target)
    loader = Path(loader).expanduser().resolve(strict=True)
    if not exe.is_file():
        raise FileNotFoundError(exe)
    output = outside_git(output)
    output.mkdir(parents=True, exist_ok=True)
    if output.is_relative_to(exe.parent):
        raise ValueError("Keep native launch output outside the dump directory.")
    attempt = Path(tempfile.mkdtemp(prefix="leonida-", dir=output))
    env = {**os.environ, "LEONIDA_UNIMPLEMENTED": "stop", "LEONIDA_D3D12": "vulkan"}
    env.pop("LEONIDA_SKIP_INT3", None)
    command = [str(loader), "--run", str(exe), "--game-dir", str(exe.parent),
               "--overlay", str(attempt / "overlay"), "--trace", str(attempt / "startup.jsonl"), "--trace-d3d12"]
    if os.name != "nt":
        wine = shutil.which(wine or "wine")
        if not wine or not shutil.which("unshare") or not sys.platform.startswith("linux"):
            raise ValueError("Native launch here requires Linux, Wine and unshare; Windows runs the loader directly.")
        for i in (0, 2, 4, 6, 8):
            command[i] = "Z:" + command[i].replace("/", "\\")
        command = ["unshare", "-Urnpf", "--kill-child", wine, *command]
        env.update(WINEPREFIX=str(attempt / "wineprefix"), WINEARCH="win64", WINEDEBUG="-all",
                   WINEDLLOVERRIDES="mscoree,mshtml=;winedbg.exe=d")
        env["PATH"] = str(Path(wine).parent) + os.pathsep + env.get("PATH", "")
    log = attempt / "run.log"
    print(f"Launching actual executable; private log: {log}", file=sys.stderr, flush=True)
    start = time.monotonic()
    with log.open("w", encoding="utf-8") as stream:
        child = subprocess.Popen(command, cwd=exe.parent, env=env, stdout=stream,
                                 stderr=subprocess.STDOUT, start_new_session=os.name != "nt")
        status = "finished"
        try:
            while True:
                remaining = timeout - (time.monotonic() - start)
                if remaining <= 0:
                    status = "timeout"
                    break
                try:
                    child.wait(timeout=min(5, remaining))
                    break
                except subprocess.TimeoutExpired:
                    print(f"Running: {time.monotonic() - start:.0f}s; see {log}", file=sys.stderr, flush=True)
        finally:
            if child.poll() is None:
                if os.name == "nt":
                    child.kill()
                else:
                    os.killpg(child.pid, signal.SIGKILL)
                child.wait()
    result = {"status": status, "exit_code": child.returncode,
              "elapsed_seconds": round(time.monotonic() - start, 2), "log": str(log),
              "trace": str(attempt / "startup.jsonl"), "gameplay_observed": False}
    write_json(attempt / "summary.json", result)
    print(json.dumps(result, indent=2))
    return 0 if status == "finished" and child.returncode == 0 else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    p = subs.add_parser("inspect", help="Inspect PE imports and layout completeness without execution")
    p.add_argument("target")
    p.add_argument("--output", help="JSON report path outside Git checkouts; otherwise prints JSON")
    p = subs.add_parser("boot", help="Bounded CPU-emulated diagnostic; no native game execution")
    p.add_argument("target")
    p.add_argument("--runtime", required=True, help="Path to a separately obtained AnyXboxX checkout")
    p.add_argument("--output", required=True, help="Report directory outside Git checkouts")
    p.add_argument("--timeout", type=positive, default=120)
    p = subs.add_parser("leonida-check", help="Run Leonida's package check; builds and exports nothing")
    p.add_argument("target")
    p.add_argument("--runtime", required=True, help="Path to a separately obtained Leonida checkout")
    p.add_argument("--output", required=True, help="External work directory")
    p.add_argument("--full-check", action="store_true", help="Also hash all game files; can take minutes")
    p = subs.add_parser("leonida-run", help="Run the actual executable with a built Leonida loader and private trace")
    p.add_argument("target")
    p.add_argument("--loader", required=True, help="Built gta6rt.exe; its TLS helper must be alongside it")
    p.add_argument("--output", required=True, help="External attempt directories, logs and write overlays")
    p.add_argument("--wine", help="Linux: Wine executable (default: wine on PATH)")
    p.add_argument("--timeout", type=positive, default=60)
    args = parser.parse_args(argv)
    print("Inspecting local files…" if args.command != "boot" else "Preparing boot diagnostic…",
          file=sys.stderr, flush=True)
    import pefile

    try:
        if args.command == "leonida-run":
            return leonida_run(args.target, args.loader, args.output, args.timeout, args.wine)
        if args.command == "leonida-check":
            return leonida_check(args.target, args.runtime, args.output, args.full_check)
        if args.command == "inspect":
            if args.output:
                outside_git(args.output)
            result = inspect(args.target)
            if args.output:
                write_json(args.output, result)
                print(f"Report: {Path(args.output).resolve()}")
            else:
                print(json.dumps(result, indent=2))
            return 0
        result = boot(args.target, args.runtime, args.output, args.timeout)
        concise = {k: v for k, v in result.items() if k != "diagnostic"}
        if "diagnostic" in result:
            d = result["diagnostic"]
            concise["diagnostic"] = {k: d[k] for k in ("phase", "error", "entrypoint_attempted",
                                    "fault_module", "fault_rva") if k in d}
        print(json.dumps(concise, indent=2))
        return 0 if result["status"] == "finished" and result["exit_code"] == 0 else 1
    except (OSError, ValueError, ET.ParseError, pefile.PEFormatError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
