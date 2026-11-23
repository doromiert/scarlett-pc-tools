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

## Not verified

Rendered output, translated game shaders, a playable scene, simulation speed at
different render rates, or gyro aiming. The last two remain requirements in
ROADMAP.md. No timing or input patches are applied to the game.
