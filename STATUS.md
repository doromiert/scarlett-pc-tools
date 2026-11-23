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

## Not verified

Native graphics, translated shader output, a playable scene, simulation speed at
different render rates, or gyro aiming. The last two remain requirements in
ROADMAP.md. No timing or input patches are applied to the game.
