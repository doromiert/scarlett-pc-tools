# Windows PC preparation and Proton target

The target is a Windows PC executable running through Proton, with conversion
performed ahead of time where possible. There is no verified standalone port or
playable scene yet. The current experimental runtime runs the supplied x86-64
CPU instructions directly; its Xbox services, graphics interfaces and memory
behavior still need compatibility implementations. This is not CPU emulation.

## Verified first preparation step

One privately supplied console compute program was compiled offline by the same
XCL integration executable used for the actual run, with four memory windows,
unsplit compute waves and the caller-selected optimization workaround. It
produced PC DXIL. A second invocation reused the file without changing its bytes
or modification time. The matching native DXIL-to-SPIR-V compiler also converted
that DXIL and passed SPIR-V validation. These were real program inputs, not
synthetic game tests.

This establishes one offline GPU conversion, not whole-corpus coverage, correct
rendering, native driver pipeline creation or gameplay. The prepared cache has
not yet been consumed by an actual game launch. The standalone SPIR-V validation
output is not automatically a replacement for a runtime pipeline: bindings,
root signatures, stage combinations and the backend ABI must agree.

## Reproduce the compute preparation stage

Use the XCL source recipe in [XCL_INTEGRATION.md](XCL_INTEGRATION.md). Keep the
runtime, shader inputs and every generated file outside Git checkouts. The
following PowerShell example uses caller-owned paths:

```powershell
$env:XCL_DXC_DIR = 'D:\private\runtime'
$env:XCL_DXIL_CACHE = 'D:\private\prepared-pc\dxil'
$env:XCL_DXC_THREADS = '1'
& 'D:\private\runtime\xcl.exe' shaders 'D:\private\shader-input' --precompile --only cs --windows 4 --split 0
```

The input must be a folder or a supported shader package. In the inspected
runtime, a single-file input takes the inspection branch before `--precompile`
is handled and does not populate the preparation cache.

Use the same cache and DXC binaries for preparation and launch. DXC cache
identity currently includes DLL sizes and modification times; identical bytes
copied with different timestamps can miss the cache. If an optimization
workaround is required, supply the same caller-selected `XCL_DXC_O0_HASHES` for
both phases. No game-derived identifiers are included here.

The example explicitly selects compute-wave behavior and avoids GPU probing or
pipeline creation. Its settings were used for the local compute experiment;
they are not universal defaults for other hardware or graphics stages. Graphics
preparation must match the runtime's separate wave and sampler settings, and
geometry-stage pairs need their actual pipeline partners.

## Remaining work

Expand preparation to the actual shader variants requested by the title and
verify cache consumption during a real launch. Static textures can also be
converted and cached, with content and layout determining reuse; render targets
and CPU/GPU-modified resources must retain coherent runtime behavior. Baking
static assets does not replace the Xbox service and memory implementations.

The current launch was performed with Wine 11.0. A Proton launch has not been
validated. Generated PC assets, bytecode, shader caches and any eventual prepared
game folder remain private; this repository publishes source and instructions.
