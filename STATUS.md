# Local verification, 2026-11-23

These observations establish startup progress, not a working port. Private input
files, traces, memory and code excerpts are not included.

## Package

All 104 paths declared in the supplied layout exist. Leonida's fast checker
recognizes the Xbox Series 1.0.2.1 package and finds its executable. This was a
presence/size check, not a full hash verification of the package.

## CPU-emulated diagnostic

AnyXboxX `8a29203aaf81196489ed97dcd4ac9f78dfa2f5c0`, Python 3.13.15,
pefile 2024.8.26 and Unicorn 2.1.4 on Linux x86-64:

- Main executable entry was observed with an instruction hook.
- Startup then stopped on an AVX instruction rejected by this Unicorn setup.
- No rendered frame or gameplay was observed.

The adapter's entry-point hook was also checked against a separately generated
synthetic PE that returned successfully.

## Leonida native loader

Official `main` artifact `d0835dd9f9ec0a88faee510126436f2427854c2e`, from
[Runtime run 45099521287](https://github.com/ItsNotRexed/Leonida/actions/runs/45099521287),
under Wine 11.0 on Linux x86-64, with networking disabled in a user/network/PID
namespace, a private Wine prefix and an external write overlay:

- `--dry-run`: exit 0, five modules mapped, 31 unimplemented imports reported.
- `--init`: exit 0, DLL/TLS initialization completed.
- `--run`, with `LEONIDA_UNIMPLEMENTED=stop`: entered the title and stopped at
  `d3d12_xs.dll!D3D12ConfigureVirtualMemoryX`, exit 3.

Upstream already has proposed implementations:
[PR 6792](https://github.com/ItsNotRexed/Leonida/pull/6792) and
[PR 7017](https://github.com/ItsNotRexed/Leonida/pull/7017).
The subsequent memory-reservation work is tracked in
[PR 6709](https://github.com/ItsNotRexed/Leonida/pull/6709).
Do not duplicate claimed work or confuse an unimplemented thunk's default return
with an implemented API. Consult upstream's current boot-chain notes before
selecting integration patches.

Source review advanced to `4ce16cd58e7ada451088d978d96320cb27881bcb`.
The tested artifact above is a separate,
explicitly identified revision, not a build of that newer checkout.

## Locally built native integration

The source recipe and exact revisions are in [LEONIDA_INTEGRATION.md](LEONIDA_INTEGRATION.md).
On Wine 11.0, Mesa 26.1.8 / RADV, Linux 6.18.48 and an RX 6900 XT,
launching the actual supplied executable with the opt-in shared-memory adapter:

- Entered the executable, initialized GameInput, and opened a file through DirectStorage.
- Allocated physical pages and created a Vulkan device on the RX 6900 XT.
- Created five queues, five fences, and 581 command lists that were then closed.
- Reserved placeholder ranges and imported the title's physical memory as a GPU buffer.
- Created descriptor heaps through the title's allocation hooks and reached view creation.
- Stopped in device slot 70, where an Xbox raw shader-resource-view call is incorrectly
  forwarded to PC `CreatePlacedResource1`, causing an access violation.

The last real run did not reach a draw, present, menu or playable scene. Upstream
[PR 7066](https://github.com/ItsNotRexed/Leonida/pull/7066) identifies the same slot,
but currently substitutes a null SRV without implementing its raw GPU-address
semantics. It is not included in this snapshot. Assertions were not skipped.

## XCL comparison

Also built and launched the actual executable with
[XCL](https://github.com/ivall/xcl) at `66e8e974601791dee66bb60adfbeb4852ba88a25`,
Rust 1.100.0, Wine 11.0, VKD3D-Proton 3.1 and DXC 1.9.2609.
The release dependencies matched their GitHub asset SHA-256 digests.

The unmodified build entered the title and opened game archives, but the initial
Wine configuration had no working D3D12 backend or DXC. Adding the private runtime
DLLs enabled the real backend. That run then blocked in a CRT assertion dialog.
A local diagnostic directed assertions to stderr and exposed VKD3D's heap-vtable
identity check. Keeping objects created for XCL's own PC-side work on their native
vtables cleared that heap stop. The next real stop was VKD3D's shared-fence-vtable
identity assertion. No draws or presents were observed. The timed observation
exit is not a successful game exit.

Those two XCL diagnostic changes remain in the separate local checkout. No XCL
code is mixed into the Leonida patch series. XCL is GPL-2.0-only; Leonida is GPLv3.

## Experimental frontier comparison

A separate local worktree of Pipodi's public `boot-integration` fork at
`b2e6066202bd684e74963ae761863804f687da75` was built and launched with additional
upstream startup fixes. This experiment is **not** the 33-patch integration above.
The fork contains explicit local stand-ins, including raw-SRV and placed-resource
paths. It does not establish correct GPU memory sharing.

The actual package supplied the private shader cache: all 26,503 programs carved
from the shader pack translated and passed SPIR-V validation. All 52 embedded BVH
programs and all 10 executable-embedded programs also translated. Of 42 native
payloads captured during execution, 38 translated; four are refused for the
unimplemented compute thread-group-size SGPR. Separately, 18 of 29 FidelityFX
upscaler programs translated; 11 hit undecodable fall-through words. These game
derivatives remain outside this repository.

On the same Wine/RADV machine, the title reached render-target creation and
command-signature creation with guest assertion skipping disabled. The resource
accounting lease needed the console tile footprint, rather than RADV's larger
native allocation size, to fit the title's fixed arena. Full native GPU backing
was retained. This adapts the bookkeeping of
[PR 7235](https://github.com/ItsNotRexed/Leonida/pull/7235) and the console footprint
of [PR 7078](https://github.com/ItsNotRexed/Leonida/pull/7078); it does not verify
rendering or the assumed console metadata accounting.

The next unsupported call was Xbox device slot 74, incorrectly forwarded to PC
ShaderCacheControl. An explicitly enabled, token-only diagnostic matching the
upstream boot report allowed later failures to be inspected. It does **not**
implement GPU page-pool registration. With that diagnostic and the full private
shader cache, one run reached 1,734 graphics calls, then a guest assertion after
36 seconds. A later run with all 38 supported native payloads translated and
command-list unwrapping restored still reached 1,734 calls, including successful
pipeline-state creation, and stopped on a resource-allocation-size assertion
after 31 seconds. The four remaining native payloads were still refused.
The next allocation diagnostic identified a 2560 x 1440, single-sample
`R32G8X24_TYPELESS` texture with both `ALLOW_DEPTH_STENCIL` and
`ALLOW_UNORDERED_ACCESS`. The PC allocation query returns `UINT64_MAX`; the title
asserts that the returned size fits in 32 bits. Supporting that console usage
requires a real texture compatibility path. Dropping the requested UAV capability
would not establish correct behavior.

No presented frame or audible output was verified here.

The Discord screenshot's black-screen/brief-audio claim contains no build revision.
It has not been reproduced locally. The normal launcher clears both known guest
assertion-skip environment variables; a diagnostic bypass is not a successful boot.

## Latest retail runtime experiment

The separate source recipe is [RETAIL_EXPERIMENT.md](RETAIL_EXPERIMENT.md).
The measured audio allocation ABI and console command-list reset cleared the
previous startup crashes and failed closes. Actual assertion-enabled Wine/RADV
runs now stay alive throughout 180-second observations, repeatedly submit draws
and report successful presentation. GPU readback confirms that sampled frames
are entirely black; no menu or controllable scene has appeared. A successful
present is not evidence of useful rendered content.

All 42 initially captured native compute payloads translated and validated after
the upstream thread-group SGPR change. The title subsequently requests hundreds
of additional pipeline-library compute programs. The first library pass produced
1,860 validated modules; they need the library's exact kind-0 dispatch-state keys
to match at runtime. Further translation and actual launch work continues.

The XCL upstream comparison has advanced to `956a476` for another local build.
Its README reports a steady frame loop but still a black image for the newer
retail title. Our actual launch still stops at VKD3D shared-fence vtable identity
assertion; the frame-loop claim was not reproduced in our Wine setup.

## Not verified

Rendered output, audio output, a playable scene, simulation speed at
different render rates, or gyro aiming. The last two remain requirements in
ROADMAP.md. No timing or input patches are applied to the game.
