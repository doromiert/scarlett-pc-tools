# scarlett-pc-tools

Local inspection and experimental boot diagnostics for user-supplied Xbox Series
packages. **This is not a playable port or a complete Xbox compatibility layer.**

The repository contains tooling, attributed runtime source patches and synthetic test inputs. No game
executables, DLLs, archives, keys, extracted assets, shaders, or private test logs
are included. Keep your dump, runtime checkouts, work files and reports outside
this repository. Nothing here uploads game content or retrieves a dump.

## Install

Python 3.11 or newer (tested locally with Python 3.13.15):

```sh
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e ".[boot]"
```

Inspection uses pefile 2024.8.26; the optional CPU-emulated diagnostic uses
Unicorn 2.1.4. It does not launch native game code on the host CPU.

## Inspect a dump

```sh
scarlett-pc-tools inspect /path/to/dump --output /external/work/inspection.json
```

Accepts the dump folder or its executable. Reports SHA-256, PE headers, direct
imports, supplied-library presence, console-runtime dependencies, and missing
layout destinations. Relative source paths in layout files describe the original
build; destination paths are used for completeness checks. File presence alone
does not establish integrity, export coverage, or compatibility.

## Leonida: preferred native-runtime research path

[Leonida](https://github.com/ItsNotRexed/Leonida) targets the Xbox Series 1.0.2.1
build with a Windows PE loader, console API shims, shader translation and a Vulkan
backend. At the revision reviewed here it explicitly reports that the real game
does not boot. Its Windows runtime can be tested under Wine on Linux; see its
build and platform documentation. [LEONIDA_INTEGRATION.md](LEONIDA_INTEGRATION.md)
contains the pinned source patch series, build details and actual-executable launcher.

[FORGE_INTEGRATION.md](FORGE_INTEGRATION.md) is the current, more advanced source
recipe. It includes native graphics pipelines, private shader-catalog generation,
and actual loading diagnostics. Locally sampled frames are still black.

The initial reference checkout below is for inspection. Use the pinned integration
guide for the more advanced native startup experiment.

```sh
git clone https://github.com/ItsNotRexed/Leonida /external/tools/Leonida
git -C /external/tools/Leonida checkout 1cc6e3c121969761d9dad8fdec99f19928213973
scarlett-pc-tools leonida-check /path/to/dump --runtime /external/tools/Leonida --output /external/work
```

Add `--full-check` to verify upstream's per-file hashes; that reads the entire
dump. The default checks sizes and presence. This command builds and exports
nothing. Follow Leonida's own instructions for a native runtime build and first
boot trace; generated outputs and traces stay outside every Git checkout.

## CPU-emulated boot diagnostic

An alternative bounded diagnostic uses a separate
[AnyXboxX](https://github.com/LooperSalty/AnyXboxX) checkout. Its prototype also
does not claim a playable game. This adapter skips its duplicate pre-launch
assessment, distinguishes loading from startup, and records whether execution
actually reached the main executable's entry point. Import resolution counts
are not percentages of game compatibility.

[STATUS.md](STATUS.md) records the actual local package and boot checks, including
the distinct source and binary revisions used. It contains no game bytes or traces.

Reference revision tested: `8a29203aaf81196489ed97dcd4ac9f78dfa2f5c0`.

```sh
git clone https://github.com/LooperSalty/AnyXboxX /external/tools/AnyXboxX
git -C /external/tools/AnyXboxX checkout 8a29203aaf81196489ed97dcd4ac9f78dfa2f5c0
scarlett-pc-tools boot /path/to/dump --runtime /external/tools/AnyXboxX --output /external/work/boot --timeout 120
```

Each attempt gets its own directory: `boot.log`, `boot.json` (phase and failure
details), and `summary.json` (completion or timeout). Failure returns a nonzero
status. A clean return does not establish gameplay. The external runtime and its
handlers are trusted host software; CPU emulation is not an OS security boundary.

## Requested gameplay work

[ROADMAP.md](ROADMAP.md) records simulation/render timing separation and gyro
aiming, including verification criteria. Neither feature is implemented yet.
There are no pretend FPS-unlock or gyro-enable switches.

## Development

```sh
python -m unittest discover -s tests -v
python scripts/check_public_tree.py
```

Tests generate a tiny PE structure from source in temporary directories; they
never require game files. The tracked-tree check rejects binary/oversized files
and unapproved extensions, including force-added dumps and reports. Run it before
every push. Do not paste private traces or extracted content into issues or PRs.

Original tools: GPL-3.0-or-later. External projects retain their own licenses;
attributed source patches are included; external build artifacts are obtained separately.
