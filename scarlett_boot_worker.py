"""Adapter for a separately installed AnyXboxX; contains no console implementation."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback
import xml.etree.ElementTree as ET


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("exe", type=Path)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    args = parser.parse_args()
    revision = subprocess.run(["git", "-C", str(args.runtime), "rev-parse", "HEAD"],
                              capture_output=True, text=True)
    result = {"mode": "Unicorn CPU emulation", "phase": "loading",
              "runtime_revision": revision.stdout.strip() or "unknown",
              "entrypoint_attempted": False, "gameplay_verified": False}
    started = time.monotonic()

    def save():
        result["elapsed_seconds"] = round(time.monotonic() - started, 2)
        args.result.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    save()
    machine = None
    try:
        sys.path.insert(0, str(args.runtime / "PrototypeScarlett"))
        from emu.machine import Machine
        from unicorn import UC_HOOK_CODE

        print("Mapping executable and linking supplied libraries…", flush=True)
        config = args.exe.parent / "MicrosoftGame.Config"
        title_id = int(ET.parse(config).getroot().findtext("TitleId", "0"), 16) if config.is_file() else 0
        machine = Machine(args.exe, log=lambda text: print(text, flush=True),
                          search_dirs=(args.exe.parent,), title_id=title_id)

        def reached_entry(cpu, address, size, data):
            if not result["entrypoint_attempted"]:
                result["entrypoint_attempted"] = True
                save()
                print("Guest executable entry point reached.", flush=True)

        machine.cpu.hook_add(UC_HOOK_CODE, reached_entry,
                             begin=machine.image.entry, end=machine.image.entry)
        result["phase"] = "startup"
        result["module_count"] = len(machine.modules.modules)
        result["unimplemented_imports"] = sorted(k for k, v in machine.statuses.items() if v == "absent")
        save()
        print("Beginning module initialization and executable startup…", flush=True)
        # start() initializes DLLs and TLS before the main entrypoint. An early
        # fault therefore must not be reported as successful game execution.
        code = machine.start()
        result["phase"] = "returned"
        result["return_value"] = hex(code & 0xFFFFFFFF)
        status = 0 if code == 0 else 1
    except Exception as error:
        result["phase"] = "failed"
        result["error"] = f"{type(error).__name__}: {error}"
        if machine is not None:
            from unicorn.x86_const import UC_X86_REG_RIP

            rip = machine.cpu.reg_read(UC_X86_REG_RIP)
            result["instruction_address"] = hex(rip)
            module = machine.modules.module_at(rip)
            if module:
                result["fault_module"] = module.name
                result["fault_rva"] = hex(rip - module.image.base)
        traceback.print_exc()
        status = 1
    finally:
        if machine is not None:
            result["unimplemented_calls"] = machine.missing_calls
            result["logs"] = machine.logs
        save()
    print(json.dumps(result, indent=2), flush=True)
    return status


if __name__ == "__main__":
    sys.exit(main())
