# XCL setup bring-up on Linux

This experimental source recipe reached the setup/account-picker UI and then
self-crashed on a guest bounded-stream assertion. Continuing with A reached
loading failures and a shared GPU reset that interrupted the desktop session.
This recipe is not stable or playable.
See [STATUS.md](STATUS.md) for the actual-run evidence and remaining blocker.

## Source and license

The [14 XCL patches](patches/xcl/README.md) form an independent GPL-2.0-only
component, separate from the GPL-3.0-or-later original tools and Leonida series.
Keep XCL's license and third-party notices with derived source/builds.

From the tools repository, with an external source destination:

```sh
git clone https://github.com/ivall/xcl /external/tools/xcl
git -C /external/tools/xcl checkout eaa36b62768fe1eedb87d010a19148854c9a3952
while IFS= read -r patch; do
  git -C /external/tools/xcl am "$PWD/patches/xcl/$patch" || break
done < patches/xcl/series.txt
git -C /external/tools/xcl rev-parse 'HEAD^{tree}'
```

The resulting tree must be `347aecd3e4b04a8d3b7b1c55ea6bce0a39cce78d`.
These are native-object identity/ABI fixes, not executable patches. The allocator
command-memory callback registration retains the supplied callback and context;
invoking custom allocator policy remains unimplemented. Assertions remain enabled.

## Build

Tested cross-build: Rust 1.100.0, LLVM/Clang/LLD 21.1.8, Windows SDK
10.0.26100 and MSVC 14.44.17.14 headers/libraries in an xwin-style SDK root.
Install the `x86_64-pc-windows-msvc` Rust target and configure Cargo's target
linker to invoke `lld-link /winsysroot:<absolute-sdk-root>`. Configure
`CC_x86_64_pc_windows_msvc` to invoke `clang-cl` with
`--target=x86_64-pc-windows-msvc /winsysroot <absolute-sdk-root>` and set
`AR_x86_64_pc_windows_msvc=llvm-lib`. Our compiler wrapper also rewrites a joined
`-include<path>` argument to `/FI<path>` for the native dependency build.

```sh
cargo build --release --locked --target x86_64-pc-windows-msvc -p xcl
```

Run this inside the external XCL source checkout with a separate target directory.
The binary is `target/x86_64-pc-windows-msvc/release/xcl.exe`. For native Windows
builds, follow the pinned upstream README; that platform was not tested locally.

## Private runtime dependencies

The actual Linux run used Wine 11.0, VKD3D-Proton 3.1, native DXVK 3.1.1
`dxgi.dll`, DXC 1.9.2609, Mesa/RADV 26.1.8 and an RX 6900 XT. Keep all
runtime DLLs outside this repository in a private runtime directory beside
`xcl.exe`: `d3d12.dll`, `d3d12core.dll`, `dxgi.dll`, `dxcompiler.dll`, `dxil.dll`.
Obtain them from their official releases; do not copy Xbox OS DLLs into Wine.

Native DXGI is material: the builtin Wine DXGI path crashed before the setup UI.
The tested DXVK archive was `dxvk-3.1.1.tar.gz` with SHA-256
`40565b4a724aadc4433fa4e010b4b23916d9b1f1baeee64e17186db94f54e608`;
its x64 `dxgi.dll` SHA-256 was
`e3c1178eb7f0dd59f91bcfcc257549e5b9cfdb5e8508719293de7f8704f53160`.
See [DXVK releases](https://github.com/doitsujin/dxvk/releases/tag/v3.1.1) and
[VKD3D-Proton's shared-DXGI requirements](https://github.com/HansKristian-Work/vkd3d-proton#readme).

## Launch settings

Use a dedicated private Wine prefix and external data/output directory. Set:

```text
WINEARCH=win64
WINEDEBUG=-all
WINEDLLOVERRIDES=dxgi=n;d3d12,d3d12core=n;mscoree,mshtml=;winedbg.exe=d
XCL_NETWORK=0
XCL_ACTIVITY=1
XCL_DXC_DIR=<Wine path to private runtime directory>
XCL_DATA_ROOT=<Wine path to private external data directory>
```

Remove `XCL_RUN_SECONDS` from the launch environment. Launch directly with
`wine <Wine-path-to-xcl.exe> run <Wine-path-to-game.exe>`, inside a separate
network/PID/user namespace such as `unshare -Urnpf --kill-child` where supported.
The tested launch used both that network namespace and XCL's network-disable
setting, plus its external write overlay. There is no automatic stop timer.
Do not replace runtime files or caches while that process is running.

The Linux run still reports missing system XGameRuntime functionality; existing
XCL HLE parts do not establish full task-queue, dialog, or networking support.
No Xbox firmware was used. The guest overflow is unresolved; this recipe contains
no capacity increase, assertion bypass, frame-rate unlock, or gyro implementation.
Keep dumps, overlay data, shader caches, captures and logs private.

## Presentation limitation discovered during continuation

The tested Wine 11 DWM cloaking call is a no-op, so XCL's separate title popup
is not hidden by that API. Its visible presenter already runs windowed; shrinking
that window does not change internal 4K rendering. A private Wine virtual desktop
can contain both windows, but it still shares the GPU. That configuration is
prepared locally and has not yet been run or verified to prevent the reset.
Do not interpret it as a proven stability fix. See the latest STATUS entry.
