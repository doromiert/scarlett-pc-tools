# Current forge integration experiment

This is the preferred source snapshot for continuing native startup work. No
menu, controllable scene, or gameplay has been verified locally. Every game input
and generated file remains outside this repository.

The maintainers' integration is on their
[forge](https://git.notrexed.dev/enx/leonida), ahead of the GitHub branch used by
the earlier experiments. This recipe pins
`70bc8a25e1c69c3f058cf550a8db9397c6a89d0c` as the patch base and incorporates
forge changes through `4fe7db213`, retaining their commit provenance. It includes native graphics pipeline
handling at Xbox device slot 57 and requires its private shader-digest catalog.

With `TOOLS` pointing at this tools checkout:

```sh
git clone https://git.notrexed.dev/enx/leonida.git /external/tools/Leonida-forge
cd /external/tools/Leonida-forge
git switch -c local/scarlett-forge 70bc8a25e1c69c3f058cf550a8db9397c6a89d0c
git am "$TOOLS"/patches/leonida/forge/*.patch
```

The twenty-five attributed source patches add the CPU descriptor-handle fix,
presentation diagnostics, visible windows with an independent message pump,
monitor fitting, loading captions, console stream-stage mapping, shared frame
tokens, the current descriptor-cleaning experiment, optional local native-shader
capture, session pipeline-cache persistence/checkpoints, newer title-memory
buffer handling, shared shader modules, and frame-poll compatibility. The current
series builds and has been exercised with the actual executable. The local
slot-67 capture and a 1.05 GiB session-cache checkpoint have been verified;
a restart successfully merged 1,156,440,368 bytes from that cache.

Build the `gta6rt` target. Linux cross-toolchain details and the opt-in RADV
file-backed host-memory adapter are in
[LEONIDA_INTEGRATION.md](LEONIDA_INTEGRATION.md). Reuse external SDL3 and Vulkan
header sources when building several integrations. The runtime's executable and
TLS helper must stay together.

## Private shader work

The separate translator series now has fifteen patches, applied to
`07d04de54eb69ea3f485d4f8f0353910d381267e` as described in
[RETAIL_EXPERIMENT.md](RETAIL_EXPERIMENT.md). All output paths below must be
external to Git and the original game folder.

The cache needs the ordinary shader pack, executable-embedded programs, BVH
programs, native compute programs, and their complete metadata. Native compute
lookup requires both code and dispatch-state hashes. The compute library goes
in the supported `library/` subfolder; FSPX outputs go in `fspx/`, BVH in `bvh/`.
Do not copy only SPIR-V binaries and discard their indices.

Using the current shader tools, extract and translate the compute library:

```sh
python -I tools/shader_library.py /private/game/shaders.rpf \
  --out /private/work/library --stages cs --disasm \
  --carve /private/work/shaders/dxbc --jobs 8
python -I tools/rdna2spirv.py /private/work/library/disasm \
  --out /private/work/shaders/spirv/library --no-asm
```

Use the forge checkout's catalog generator after carving the containers:

```sh
python -I tools/native_pso_hashes.py /private/work/shaders/dxbc \
  /private/work/shaders/spirv
```

It writes `native_hashes.txt` beside the shader index. It contains private paths
and game-derived digests; it is not distributed here. Without it, the native
graphics handler cannot resolve the title's containers.

The runtime can optionally capture slot-67 payloads for local analysis through
`LEONIDA_DUMP_SLOT67`, pointing to an existing external directory (a Windows path
when running through Wine). This is off by default. The resulting `.fspx` files
contain game code: keep them private, unpack with `tools/fspx_unpack.py`, and
translate with the same tools and flags used for the rest of the cache. The
earlier local implementation captured 42 requested payloads successfully; the
forge port is included so this step can be reproduced without distributing them.

## Actual launch

Set `LEONIDA_SHADERS` to the private cache, using a Windows path through Wine,
and run `scarlett-pc-tools leonida-run` with the built loader, Wine and an
external report directory. The default observation remains 60 seconds; native
observations can explicitly select up to 3,600 seconds. The launcher retains
guest assertions and disables networking on Linux.

`LEONIDA_CAPTURE_STATS=1` records actual presented-pixel statistics, with no image
files. Native-pipeline completion counts also update the compatibility window's
caption through its independent UI thread. A successful present is not proof
that the frame contains useful content.

For the checkpoint-enabled build, `LEONIDA_STARTUP_CACHE_CHECKPOINTS=1` requests
session-cache writes after slow successful compiles. The opaque cache remains
beside the external runtime binary. It is also private game-derived output.
The actual game exceeded the default 256 MiB save limit. A local run with
`LEONIDA_PIPELINE_CACHE_BYTES=2147483648` successfully wrote 1,126,351,504 bytes.
This raises only the external cache-file limit. The next actual launch successfully
merged a later 1,156,440,368-byte checkpoint and passed 1,920 native completions.
This verifies reload, not a measured cache-hit rate or gameplay.

## Observed limits

On Wine 11.0, Linux 6.18.48, Mesa/RADV 26.1.8 and an RX 6900 XT, the forge
integration has passed the previous allocation assertion, resolved its graphics
catalog, created native graphics pipelines, and presented black frames. An
actual-run CPU profile found 96.6% of sampled work in RADV compute compilation;
progress advanced beyond 1,920 native completions without a reported API failure.
This is ongoing startup work, not gameplay. The current frame-pacing handoff
replays configuration made before the first presentation; zero-time frame polls
return a nonfailing timeout and honor the observed token-on-timeout flag. This
cleared a newly observed assertion at `exe+0x2482452`. It does not detach simulation
speed from the frame rate.

The private compute-library build now has 2,683 validated modules out of 2,684.
The hardware-halt program remains refused. Validation establishes module
structure, not output equivalence.

The depth/stencil-plus-UAV compatibility path is an upstream stand-in: it drops
the unsupported UAV capability. It does not implement shader writes into depth
textures. Other console operations and texture-memory sharing also remain
incomplete. Audio output, timing separation and gyro aiming are unverified.

All source attribution is retained in the patches. No XCL implementation code
is included; its GPL-2.0-only code remains in a separate research checkout.
