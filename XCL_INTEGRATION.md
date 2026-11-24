# XCL bring-up on Linux

This experimental source recipe reached input-responsive setup, colored startup
frames and loading artwork. Selected compiler workarounds passed two shader
assertions. Constraining graphics overflow allocations to the console builder's
address width passed its next failure; the subsequent actual run ended in the
title's own error path. Earlier GPU resets interrupted GNOME. This recipe is
not stable or playable.
See [STATUS.md](STATUS.md) for the actual-run evidence and remaining blocker.

## Source and license

The [47 XCL patches](patches/xcl/README.md) form an independent GPL-2.0-only
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

The resulting candidate tree must be `d27bf499a208c9826a10c52a36be90370f421bd3`.
The setup baseline is the first 14 patches; current candidate verification is
described in the patch-directory README.
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

## Isolated fullscreen continuation

Shrinking a window does not change the title's internal 4K rendering. The later
actual runs used `XCL_HEADLESS=1` and `XCL_FRAME_DUMP=1`: native rendering and
GPU-to-CPU readback continue, while XCL's HWND/swapchain/presentation are bypassed.
The atomic `logs/headless_latest.bmp` contains actual rendered source pixels;
unsupported formats produce no image. A separate fullscreen viewer displayed
these CPU images, with no game GPU resources shared with GNOME. It was very slow.

A private authenticated CPU-only Xvfb display and a device mount namespace
exposed only the spare GPU's render node. `XCL_ADAPTER_STRICT=1` with
`XCL_ADAPTER=RAPHAEL_MENDOCINO` required the matching native adapter; DXVK and
VKD3D filters agreed. The measured adapter was AMD device 1002:164e, Mesa/RADV
26.1.8. Use the actual name/node of your own spare GPU, not this machine's values.
An adapter-name filter alone does not hide the desktop GPU. A Wine virtual
desktop alone also still shares GPU access.

The game still timed out on the spare GPU. GNOME survived both isolated runs;
this does not establish general isolation from all host failures. The current
headless path synchronously waits for readback and writes a BMP every captured
frame. Asynchronous capture and physical-controller control remain unverified.

`XCL_FRAME_DUMP_STEP=2` produces 1920×1080 captures from the observed 3840×2160
source. Allowed steps are 1, 2 and 4; default is 4. The older
`XCL_FRAME_DUMP_FULL` override selects step 1. Headless images are still produced
every selected frame, while expensive pixel histograms are normally sampled;
`XCL_FRAME_DUMP_STATS=1` restores exhaustive diagnostic statistics.

The fullscreen ffplay viewer has its own keyboard shortcuts: Space or P pauses
video playback while the game continues. A frozen viewer therefore does not
establish a frozen game. The later actual 1080p run used the RX 6900 XT and still
encountered a graphics-queue timeout during heavy loading.

## Sampler-input experiment and synchronization correction

`XCL_BINDLESS_HEAP_INPUTS=1` is the newer graphics experiment. For wholly inline
root arguments, it appends the resource and/or sampler heap shadow addresses
declared by root-signature flags `0x400` and `0x800`, in that order. It checks
register capacity, heap identity and memory-window bounds. Original console
heaps are retained separately from the native shared heap used for PC binding.
Explicitly empty bindings remain empty. Compute and spilled layouts are not
covered by this experiment.

In an actual loading run, this supplied the missing inputs of the fullscreen
material shader and passed the earlier GPU hang. Execution continued through
later shader passes before a native command-signature assertion. The candidate
also preserves that object's native vtable; validation of this last correction
passed that assertion in a later run, which stopped at an independent XG copy
argument mismatch. No controllable scene has been verified.

`XCL_SAMPLER_BASE_SGPR=11` enables the sampler-input experiment used in the actual
setup run. It appends the currently bound sampler heap's runtime address only
when that register is the first unused inline register and the heap is
unambiguous in memory window 0. It does not replace explicit root arguments.
This is default-off and is not a general register-placement rule for every
shader, root signature, stage or spilling combination.
The newer bindless experiment takes precedence when both settings are supplied.

With that input, setup rendered and responded to keyboard input. The final 600
captured setup frames before a user-requested suspension averaged 29.1 FPS;
the intro was about 4 FPS. Resuming that same process and finishing setup exposed
a separate resource-interface assertion during sparse-memory readback. The
native staging-resource correction passed that exact boundary in a later run.

Wait64BitValueX was also decoded with an extra mask argument: actual callers
provide a 32-bit flags argument in that position. The corrected hook retains
full-width comparisons and existing synchronization logic. A subsequent actual
run no longer reported the earlier repeated two-second waits, loaded further,
and eventually lost the graphics device. Wait32 is unchanged pending evidence.
These corrections do not establish gameplay or general GPU stability.

`XCL_XG_COPY_FLAGS=1` selects the observed eight-argument CopyFromSubresource
layout: an extra DWORD precedes the source pointer. Only an extra value of zero
is supported; its other semantics are unknown. The legacy seven-argument layout
remains the default, and CopyIntoSubresource is unchanged. An actual run
completed two corrected copies before encountering a later DXIL-to-SPIR-V
compiler assertion. This setting is a compatibility experiment, not a universal
XG ABI rule.

## Temporary texture placeholders

`XCL_TEXTURE_PLACEHOLDERS=1` opts into valid constant BC1, BC5 and BC7 blocks for
unsupported compressed texture requests. It is default-off, explicitly trades
texture accuracy for loading progress, and does not affect other archive data.
BC1 and BC7 use opaque magenta; BC5 uses two channels with byte value 128. The original
file read, size checks, physical-page writes and failure/status reporting remain.
Hardware swizzle and other BCPack modes are still refused.

This was requested for reaching first gameplay with temporary texture artifacts.
Actual runs exercised BC1, BC5 and BC7 placeholders, advanced through more loading
and then suffered game-context GPU timeouts. Neither this switch nor fullscreen
CPU output proves GPU stability or gameplay.
No assertion, executable instruction, simulation timing, or gyro change is included.

## Selective compiler diagnosis

Patch 43 supports `XCL_DUMP_SHADER_HASHES=<comma-separated console hashes>` for
bounded private capture; leave it unset normally. Captures include copyrighted
shader programs and must stay outside this repository.

Patch 44 supports `XCL_DXC_O0_HASHES=<comma-separated console hashes>`. Only those
console programs use DXC `-O0`. Their DXIL cache lives in a separate `O0`
namespace. The translated fast caches are bypassed for selected programs,
so changing the selector cannot silently reuse an optimized translation.
Normal shader optimization remains the default. Larger unoptimized programs
can compile slowly or use more memory; this is a diagnostic workaround.

One actual captured compute program reproduced the DXIL-to-SPIR-V assertion at
DXC `-O1`, with output byte-identical to the failing runtime shader. Its `-O0`
form compiled with SPIR-V validation enabled using the same pinned compiler
source. Actual execution passed that shader and stopped at a different structurizer
assertion. A second actual shader reproduced its default compiler failure and
passed CPU-only SPIR-V validation at `-O0`; the next actual run selects both.
No shader hashes, shader payloads,
SPIR-V, cache files or captured frames are provided.

Patch 45 retains the normal translation fast caches for programs outside the
selector. Patch 46 includes upstream [a94e151](https://github.com/ivall/xcl/commit/a94e1511e0a5f378ff10e4daf701ebaa9da506eb):
high-coordinate swizzle tables retain only their mathematical period, reducing
construction work and memory while preserving modulo-indexed offsets. A live
loading CPU profile identified table construction as a substantial cost; its
actual performance improvement is not measured yet.

## Graphics allocation address width

Patch 47 adds the default-off `XCL_GRAPHICS_40BIT=1` option. Graphics allocations
that overflow XCL's unified-memory windows use Windows
[VirtualAlloc2 address requirements](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualalloc2)
within 64 GiB through 1 TiB, keeping their complete address ranges below the
console BVH builder's 40-bit limit. Allocation failure is propagated instead of
retrying at an incompatible high address. Requested fixed addresses retain
their existing behavior.

The actual title made its large overflow reservations in that range, reported
no constrained-allocation failure, and passed the prior BVH address-width error.
It later deliberately faulted in its own error path. Three unfinished shader
compilations did not complete within bounded CPU-only reproductions; whether
that caused the title's later failure is under investigation. Low addresses
alone do not make external buffers visible through the translated shader ABI.
No ray-tracing correctness or playable output is claimed.
