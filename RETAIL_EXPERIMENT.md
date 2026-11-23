# Experimental retail startup integration

This source snapshot is for continuing runtime bring-up. It is not a playable
port. All game inputs, translated shaders, runtime binaries and traces remain
outside this repository.

The base is ramenbellic/Leonida `boot/retail-stack` at
`8443d34c14a5ec1e98d2a076d4c10f7bcbfa37e7`. The ten patches in
`patches/leonida/retail/` add console texture accounting, DirectStorage zlib,
command-list CPU handle translation, console list reset slot 139, the measured
APU heap implementation, presentation result tracing, opt-in frame-content statistics, and monitor-fit windows with a separate message pump. These preserve the
upstream authors. This series is separate from the earlier clean integration.

With `TOOLS` set to this checkout, apply it in a new source checkout:

```sh
git clone https://github.com/ItsNotRexed/Leonida.git Leonida-retail
cd Leonida-retail
git fetch https://github.com/ramenbellic/Leonida.git boot/retail-stack
git switch -c local/scarlett-retail 8443d34c14a5ec1e98d2a076d4c10f7bcbfa37e7
git am "$TOOLS"/patches/leonida/retail/*.patch
```

Build the `gta6rt` target using upstream's Windows build or its clang-cl/xwin
cross toolchain. The Linux toolchain and opt-in RADV adapter are described in
[LEONIDA_INTEGRATION.md](LEONIDA_INTEGRATION.md). Run it using `leonida-run` with
an external private shader cache in `LEONIDA_SHADERS`. The launcher disables
networking, keeps writes external, retains guest assertions, and can recover
missing Linux desktop display variables from the user's systemd session.

The seven source patches in `patches/leonida/native-shaders/` apply separately to
shader tools at `07d04de54eb69ea3f485d4f8f0353910d381267e`. They integrate upstream
[PR 6446](https://github.com/ItsNotRexed/Leonida/pull/6446) (compute thread-group SGPR),
[PR 6813](https://github.com/ItsNotRexed/Leonida/pull/6813) (library parsing),
[PR 8448](https://github.com/ItsNotRexed/Leonida/pull/8448) (wave32 compare masks),
[PR 8497](https://github.com/ItsNotRexed/Leonida/pull/8497) (decoder fallback), and
[PR 7529](https://github.com/ItsNotRexed/Leonida/pull/7529) (library compute programs
and their exact dispatch-state sidecars). Conflict resolutions preserve the NONE
field guard and defer output publication until disassembly succeeds.

```sh
git switch -c local/scarlett-shaders 07d04de54eb69ea3f485d4f8f0353910d381267e
git am "$TOOLS"/patches/leonida/native-shaders/*.patch
```

Use a separate checkout from the runtime. Extract the library's compute programs
with `tools/shader_library.py --stages cs --disasm --carve`, then translate with
`tools/rdna2spirv.py`. The `.state` files are required: code-only index entries
cannot match the title's slot-67 descriptions. Keep all outputs outside Git. The
runtime snapshot predates optional `library/` loading; merge validated modules
and their complete metadata into its private `fspx/` cache, using unique names.
LLVM 23.1.0-rc1 was used for native-library disassembly; SPIRV-Tools 1.4.341.0 for
validation. Validation does not establish shader output correctness.

The private cache also includes the executable's 10 embedded shaders and the
52 BVH shaders. The build above does not distribute them. Existing cache work
must include those indices; upstream [PR 8303](https://github.com/ItsNotRexed/Leonida/pull/8303)
automates the executable stage in a separate integration.

Observed here: Wine 11.0, Linux 6.18.48, Mesa/RADV 26.1.8, RX 6900 XT,
clang-cl/LLVM 21.1.8, MSVC 14.44.17.14, Windows SDK 10.0.26100.
An actual executable run remained alive for the full 180-second observation,
with 9,735 successful list resets and 10,360 successful closes. No failed closes
were recorded. Game and presentation windows appeared but remained blank;
there was no verified menu, gameplay, or audio output. Later observation confirmed
thousands of successful `PresentX` calls, while GPU readback showed every sampled
presented pixel black. The oversized title window now fits a 1080p monitor.

The first static-library pass translated and validated 1,860 of 2,684 compute
programs. Restoring their exact dispatch-state keys reduced observed missing
programs to 40 early in the next run; 138 had appeared by its 180-second limit. The expanded translator pass is
still being measured; neither count establishes a playable result.

Limits remain in the public base: several console operations are stand-ins,
textures do not share the title's tiled CPU memory, and the audio hardware object
accepts commands without synthesizing sound. The allocation-size experiment in
the base is not a complete implementation of depth/UAV resources. Do not infer
correct rendering from successful API calls. The runtime target was built and
checked through actual title launches; the full synthetic test suite was not run.

No XCL implementation code is included. XCL's public ABI observations informed
the investigation; the integrated reset implementation is the GPLv3 Leonida
change `ef9d0759d22e9a88515e7f56854c9db2b6ccc13f`.
