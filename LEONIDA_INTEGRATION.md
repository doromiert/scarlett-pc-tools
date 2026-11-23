# Leonida startup integration

This source-only patch series reproduces a local runtime experiment. It does not
produce a playable port. No game binary, asset, shader, SDK file or private trace
is included. Runtime output must stay outside Git and outside the dump.

Base: `4ce16cd58e7ada451088d978d96320cb27881bcb`.
Final local source revision: `8a06c50ec6f009224344c33078b2f91a0ef6b474`.
The patches preserve upstream commit authors. Local conflict resolutions and
integration changes are marked as separate commits. All retain Leonida's GPLv3
license; this repository includes its license text.

## Sources

The series integrates existing work from these upstream pull requests:

- [7017](https://github.com/ItsNotRexed/Leonida/pull/7017): virtual-memory configuration.
- [4531](https://github.com/ItsNotRexed/Leonida/pull/4531): aligned console page sizes.
- [4313](https://github.com/ItsNotRexed/Leonida/pull/4313): executable TLS slot zero.
- [6582](https://github.com/ItsNotRexed/Leonida/pull/6582): XErrorReport.
- [3410](https://github.com/ItsNotRexed/Leonida/pull/3410): GameInput ordinal one.
- [4348](https://github.com/ItsNotRexed/Leonida/pull/4348): DirectStorage.
- [6995](https://github.com/ItsNotRexed/Leonida/pull/6995): shared physical-page storage.
- [6964](https://github.com/ItsNotRexed/Leonida/pull/6964): device slot 26 calling convention.
- [6954](https://github.com/ItsNotRexed/Leonida/pull/6954): Xbox queue descriptions.
- [2490](https://github.com/ItsNotRexed/Leonida/pull/2490) and
  [7076](https://github.com/ItsNotRexed/Leonida/pull/7076): console command lists.
- [6919](https://github.com/ItsNotRexed/Leonida/pull/6919), commit `36936f3b`:
  placeholder and default-allocator behavior adapted to the separate #6995 store.
- [6953](https://github.com/ItsNotRexed/Leonida/pull/6953) and
  [7218](https://github.com/ItsNotRexed/Leonida/pull/7218): larger proxy table and GPU buffers on title memory.
- [7021](https://github.com/ItsNotRexed/Leonida/pull/7021): descriptor allocation hooks.

Local changes include conflict resolution, the standalone device's placed-buffer
handler registration, a clang enum-mask correction, and concrete import-failure
logging. Synthetic fixtures accompanying upstream changes remain source fixtures;
the final integration was evaluated by launching the supplied executable. The
complete upstream test matrix was not run on this final stack.

## Reproduce the source and build

Use a separate checkout, then apply these patches in filename order:

```sh
git clone https://github.com/ItsNotRexed/Leonida /external/tools/Leonida
git -C /external/tools/Leonida checkout 4ce16cd58e7ada451088d978d96320cb27881bcb
git -C /external/tools/Leonida am /path/to/scarlett-pc-tools/patches/leonida/*.patch
```

Use Leonida's Windows build instructions, or its
`runtime/cmake/clang-cl-xwin.cmake` toolchain on Linux. The measured Linux build used
clang-cl/LLVM/lld 21.1.8, CMake 4.1.6, Ninja 1.13.2, xwin 0.10.0,
Windows SDK 10.0.26100 and CRT 14.44.17.14. SDK files are obtained separately.

For the cross build, configure with `-DXWIN_DIR=/external/sdk`,
`-DLEONIDA_SDL3_FETCH=ON -DLEONIDA_VULKAN_HEADERS_FETCH=ON
-DLEONIDA_REQUIRE_VULKAN=ON -DCMAKE_BUILD_TYPE=RelWithDebInfo`, using the toolchain
above and an external build folder. Then build the `gta6rt` target. Keep
`gta6rt_tls_host.dll` beside `gta6rt.exe`. No shader or asset export was performed
for this startup experiment; later graphics execution will need those steps.

## Launch the actual executable

```sh
scarlett-pc-tools leonida-run /path/to/dump   --loader /external/build/gta6rt.exe --output /external/runs   --wine /path/to/wine --timeout 60
```

On Windows omit `--wine`. On Linux the launcher uses a fresh private Wine prefix
and a network/PID namespace. It writes a private log, startup trace and overlay
for each attempt, prints progress while waiting, and kills the attempt at its
timeout. Assertions are left enabled. Read the log for the actual failure; a
loader exit or import count does not establish rendering or playability.

## Optional RADV file-backed memory import adapter

The real run under Wine 11.0, Mesa 26.1.8, libdrm 2.4.133, Linux 6.18.48 and an
RX 6900 XT reached `VK_ERROR_OUT_OF_HOST_MEMORY` while importing the title's
pagefile-backed physical-page views. An ioctl trace showed
`DRM_IOCTL_AMDGPU_GEM_USERPTR` returning `EPERM`. libdrm requests `ANONONLY` by
default; the kernel rejects file-backed views for that optional flag.
See the [libdrm implementation](https://chromium.googlesource.com/chromiumos/third_party/libdrm/+/refs/heads/master/amdgpu/amdgpu_bo.c)
and [kernel implementation](https://github.com/torvalds/linux/blob/v6.18/drivers/gpu/drm/amd/amdgpu/amdgpu_ttm.c).

`native/radv_file_userptr.c` retries only that specific failure without the
optional anonymous-only restriction. Kernel range validation and registration
remain in effect. The real title then imported its buffer successfully and went
on to descriptor setup. This adapter is process-local and opt-in, and was checked
only on the versions/hardware above. It is not installed into the system driver.

Compile with a Linux C compiler and libdrm development headers:

```sh
cc -shared -fPIC -O2 -Wall -Wextra -Werror $(pkg-config --cflags libdrm)   native/radv_file_userptr.c -ldl -pthread -o /external/tools/libscarlett_userptr.so
LD_PRELOAD=/external/tools/libscarlett_userptr.so   scarlett-pc-tools leonida-run /path/to/dump   --loader /external/build/gta6rt.exe --output /external/runs --wine /path/to/wine
```

The latest real stop and remaining limitations are in [STATUS.md](STATUS.md).
