# Local verification, 2026-11-24

## 2026-11-24: native queries passed; detile optimization built

The 50-patch candidate is `2338001782caab218a5334b3e540ed71f1956135`,
tree `56ea123db872c97d9c15eb3c0af14269dab2265e`. Strict application from the
pinned base and a separate release build passed. The clean public executable
has not run.

Three additional unfinished default-optimized compute shaders reproduced slow
CPU compilation, with byte-identical DXC `-O3` output. Each `-O0` form passed
SPIR-V validation in about 0.2 seconds. The next actual configuration selects
all five affected programs and expands the coherent window from 512 MiB to the
supported maximum below 4 GiB. The isolated launcher had lost the sizing hint
between runs; these are still experimental settings.

The larger-window attempt exposed a query-heap vtable assertion before the intro.
Patch 48 preserves native query-heap identity, following the command-signature
correction. Actual execution with that change passed the assertion and rendered
the local account picker. It remains alive and extremely slow. A live CPU sample
spent about 60% in texture offset calculations and detiling. Patches 49–50 add
upstream's equivalent column/row precomputation and whole-row linear copies;
their actual performance validation is pending. Controllable gameplay remains
unverified. No synthetic game tests were run for these changes.

## 2026-11-24: BVH address-width check passed

The 47-patch candidate is `458a69bb508ca0de1033d52cc4342a28e54d3dfc`,
tree `d27bf499a208c9826a10c52a36be90370f421bd3`. All patches applied strictly
from the pinned base, reproduced that tree, and passed a separate release build.
The clean public executable has not run; actual execution includes private
bounded diagnostics.

An actual run selecting both compiler workarounds passed both earlier shader
assertions, then failed when the console BVH builder rejected a destination
address above 40 bits. With patch 47's allocation option enabled, the next run
made its large overflow graphics reservations below 1 TiB and passed that error.
It later deliberately faulted in its own error path. Three shader compilations
were unfinished at exit and did not complete in bounded CPU-only reproductions;
causality remains unproven. Controllable, rendered gameplay is not verified.

## 2026-11-24: first compiler failure passed; a second isolated

The 46-patch candidate is `7024587dfb6367c2c8fdb3a6192da8bfa3d9106f`,
tree `7d436fa6696ab96b6cc6b7a91a80ed08caf1491b`. Strict application and a
separate release build are recorded with this candidate. The clean public
executable has not run.

The actual title created the first previously failing compute pipeline with
selected DXC `-O0` output. Its dumped DXIL exactly matched the CPU-tested form,
and the native backend produced SPIR-V. Loading then self-exited at a different
structurizer assertion. The second shader was matched to its archive entry
using its HLSL cache key, without another game launch. Default DXC output was
byte-identical to the new failure; `-O0` passed CPU-only SPIR-V validation.
The next actual run selects both shaders. No controllable gameplay is verified.

Patch 45 preserves normal translation caching for nonselected shaders. Patch 46
includes upstream's swizzle-table period correction. The preceding real loading
CPU profile spent substantial time constructing those tables; a speedup has
not yet been measured. The native Vulkan backend remains unchanged, with
assertions enabled.

## 2026-11-24: selective shader compiler workaround

The 44-patch candidate is `3f93d2fab9a7e1a656fee22b143c77af772a1eee`,
tree `35b9abe456a8586f622efcb5180bf918c610bc4c`. All patches applied
strictly from the pinned base and a separate release build passed. The clean
public executable has not run.

The next actual run reproduced the same DXIL-to-SPIR-V control-flow assertion
and captured only the offending console compute program privately. Recompiling
its generated HLSL at DXC `-O1` reproduced the exact failing runtime bytes and
assertion in the pinned CPU-only compiler. `-O0` produced validated SPIR-V in
about 1.2 seconds. Forcing XCL's fallback control flow changed nothing: that
shader already used it.

Patch 44 applies `-O0` only to caller-selected console shader hashes, with a
separate cache namespace and no translated-cache reuse. An actual title run
with that selector is underway; loading success and gameplay are not verified.
A separate experimental structurizer bookkeeping patch failed validation and
is excluded from the runtime and this repository.

## 2026-11-24: native indirect assertion passed; XG copy ABI corrected

The current 42-patch candidate is `abbae09c88b7606071cd34610b9990e3c4838f0c`,
tree `b6c1bfeba82a07f06ff5e09868a3b32bb7c0de3d`. Strict application and a
separate release build passed. The clean public binary has not itself run.

An actual run with native command signatures passed the previous vtable
assertion and stopped later in XG texture readback. Caller inspection proved an
extra DWORD precedes the source pointer in that caller's CopyFromSubresource
layout. The legacy hook instead consumed pointer bits as a row pitch and wrote
outside the destination. The opt-in wrapper in patch 42 matches the observed
argument order; nonzero extra arguments remain unsupported.

With `XCL_XG_COPY_FLAGS=1`, the next actual run completed two copies with normal
row/slice pitches (2048/262144 and 256/8192). It later exited at a DXIL-to-SPIR-V
control-flow-structurizer assertion. The failing shader has been isolated
privately for investigation. Neither controllable gameplay nor full graphics
stability is verified.

## 2026-11-24: loading passed the earlier GPU hang

The 41-patch source recipe reproduces candidate
`ea1bfec08e28a1b6139323a5e85032e4002f1de6`, tree
`f0357ea75e642be3a6e4bf097efac00e1a74c53b`. Strict patch application and a
separate release build passed; the clean public executable has not itself run.

Actual GPU breadcrumbs narrowed the loading hang to a fullscreen material draw.
The translated pixel shader needed both resource-heap and sampler-heap inputs;
those registers were zero with the earlier sampler-only experiment. With
`XCL_BINDLESS_HEAP_INPUTS=1`, an actual run supplied both declared heap addresses,
passed the previously failing shader family and continued into later passes.
About 9.6 GB of target pages were backed before a different native
command-signature vtable assertion ended the process. That run reported no GPU
device loss. This does not establish general GPU stability or playable output.

Patch 41 preserves native command-signature identity at creation. Its actual-run
validation is in progress. Texture accuracy, intro performance, timing separation
and gyro aiming remain unresolved; controllable gameplay is not verified.

## 2026-11-24: input-responsive setup and later loading failures

The 38-patch source recipe reproduces candidate
`75cee47c8f40d8ffbd73095f035625c74b4cd593`, tree
`6377e9ea4fe75dc91ea4517fc8660900e1efa17b`. Strict application and a separate
release build passed. The clean public executable has not itself been run;
actual runs included additional private diagnostics.

The opt-in sampler input allowed repeated draws beyond the earlier failing
setup path. Navigation, text size, subtitles and brightness screens responded
to input. Actual setup capture averaged about 29 FPS after a slow intro. Later
captures were verified at 1920×1080. No scene with controllable gameplay is
verified.

Completing setup exposed a native CopyBufferRegion resource-vtable assertion.
A diagnostic identified a console proxy passed by sparse-memory readback;
normalizing staging resources at the native boundary passed that call later.
An independently observed Wait64 argument mismatch caused repeated two-second
waits. Correcting the argument layout removed those warnings in the next actual
run, which streamed further before an RX graphics-queue timeout/reset.

GPU-command tracing is the current investigation. Texture accuracy, simulation
timing separation and gyro aiming remain unresolved. All game files, generated
shaders, captures, memory snapshots and traces remain outside this repository.

## 2026-11-24: isolated fullscreen, still no gameplay

The source-only XCL series now contains 33 patches, reproducing candidate
`2e58f54f32a49961f4ba3f376277f4207a13e71d`, tree
`e243c656bde257adff33a56cbb03757e925d216d`. The latest actual executable also
included private, bounded CPU fault diagnostics; those game-specific probes are
not published.

Two actual Linux runs on a spare integrated AMD GPU rendered colored startup
frames and loading artwork through headless CPU readback into a fullscreen
viewer. The game could access only that GPU's render node. Both runs eventually
self-exited with D3D12 device loss; GNOME remained running. Loading was very
slow. The latter run exercised BC1 placeholders as well as BC5/BC7. The
constant-buffer correction and exact DirectStorage reads did not resolve
the GPU timeout. No playable scene or physical-controller control is verified.

No game files, shaders, frames, root data, traces or binaries accompany this
update. Simulation/render timing separation and gyro aiming remain unimplemented.
Earlier entries below describe earlier candidates and their narrower evidence.

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
to match at runtime. The expanded private cache now has 2,642 validated library modules. A ten-minute
actual run still showed no playable scene. Later fixes address programs requested
after that run's early frames, and a longer observation is underway with guest
assertions retained and bounded native-pipeline progress diagnostics.

The XCL upstream comparison has advanced to `956a476` for another local build.
Its README reports a steady frame loop but still a black image for the newer
retail title. Our actual launch still stops at VKD3D shared-fence vtable identity
assertion; the frame-loop claim was not reproduced in our Wine setup.

## Current forge comparison

The maintainers' forge integration at `70bc8a25e` adds native graphics pipeline
handling missing from the earlier runtime. The source recipe and exact patch
series are in [FORGE_INTEGRATION.md](FORGE_INTEGRATION.md).

The first actual forge run exposed a frame-token mismatch and the existing
allocation-size assertion. Sharing device/presentation tokens restored successful
presentation; current upstream descriptor cleaning cleared the measured allocation
stop. The ongoing assertion-enabled run resolves a 25,321-entry private graphics
catalog and has advanced beyond 1,500 native compute completions without a reported
API failure. Every sampled presented frame remains black.

A non-invasive CPU profile of that actual process found 4,541 of 4,703 samples
(96.6%) in RADV compute compilation across eleven workers. Memory pressure and swap
were zero during the profile. The evidence shows active compilation, not a global
deadlock. No synthetic workload was used for this result.

The compute-library toolchain now validates 2,683 of 2,684 programs; the hardware
halt remains unsupported. New session-cache/checkpoint source ports are prepared
for preserving expensive completed work, with actual write/restart verification
still pending. They are not evidence of a faster or playable boot yet.

## Not verified

Audio output, a playable scene, simulation speed at different render rates,
or gyro aiming. Rendered setup UI is verified only in the later XCL run below. The last two remain requirements in
ROADMAP.md. No timing or input patches are applied to the game.

## Current repository follow-up

The forge source series now incorporates `4fe7db213` and actual-run fixes for the
lazy pacing handoff and zero-time frame polls. The actual executable passed the
new wait assertion, exceeded 1,920 native completions, and wrote a 1.05 GiB session
pipeline cache with an explicit 2 GiB file limit. Sampled frames remained black;
the next actual restart successfully merged 1,156,440,368 bytes from the saved cache.

XCL `2abc562` introduced a reported first account menu in upstream commit
`38b05b7`; that is an upstream observation, not a local settings-screen result.
Our actual Wine run reproduced the native shared-fence identity assertion. A
separate local XCL fence proxy cleared it and exposed the next `E_INVALIDARG` at
`exe+0x2478b7b` during command-list creation. The allocator identity fix is being
checked separately. No XCL implementation code is distributed in this repository.

## Graphics phase and descriptor follow-up

The actual compute count stabilized at the last reported 2,688 while three hot
threads continued in RADV graphics creation (893/894 samples). The new runtime
separates compute and graphics progress; a pending count is live, not a fixed
remaining boot total. A serial graphics run exceeded 53,000 successful creations
and persisted graphics checkpoints. Images remain black. Queue wait is excluded
from the slow-compile checkpoint trigger.

Bounded actual slot70 captures established typed R16/R8 and structured buffer
views, plus texture views, beyond the existing raw-only path. The buffer bridge
now validates and preserves exact view ranges/types, but several observed VAs
have no registered resource and remain unresolved. Texture address associations
and CPU-content synchronization remain incomplete. No rendering cause is proved
solely by a discarded view.

Separate XCL bring-up has passed the measured native fence, allocator, resource,
descriptor-heap, root-signature, pipeline-state and memory-heap identity checks.
A later execute-null crash identified allocator Xbox slot9 by exact guest
callsite/PDB; its registration candidate is under actual-run verification.
No XCL implementation source is included in this GPL-3.0 recipe.

## XCL: locally rendered setup UI

Separate local XCL `0cb3173bbc47e3aa05cb288cb462005a0f16fff9` with
Wine 11.0, VKD3D-Proton 3.1, native DXVK 3.1.1 DXGI, Mesa/RADV 26.1.8
and an RX 6900 XT rendered the setup/account-picker UI. Private frame captures
and the user's observation agree. This is not a verified title screen, startup
animation, or playable scene.

Native DXVK DXGI cleared the measured Wine builtin-DXGI crash. The actual game
subsequently presented at approximately 30 frames per second and issued draws,
compute dispatches and DirectStorage reads. It then stopped on its own bounded
stream assertion: a 96 KiB channel had 80 bytes remaining for a 1,728-byte write.
Why the channel fails to drain remains under investigation; no assertion or
capacity check was disabled. Repeating with register-only diagnostic XCL
`1c59a0c2542c1bf99693cf5504cb4cf12ac33b30` reproduced the same stop.

These runs have no automatic stop timer. The dump remains private, with writes
redirected to an external overlay and networking disabled. The XCL implementation
remains a separate GPL-2.0-only component; the later source recipe distributes
only attributed patches, with no game files, frame captures, or private runtime logs. Leonida's sampled output
remains black.

The independent [XCL source recipe](XCL_INTEGRATION.md) now reproduces the
setup-tested source tree from 14 attributed patches. Its GPL-2.0-only licensing
is explicit and separate from the Leonida implementation.

## Account-picker input and subsequent device loss

A further actual run of the same setup-tested binary captured the account picker
at host time 43.708 seconds, registered A at 45.000 seconds, then changed to a
uniform green frame at 45.941 seconds and continued loading data. It did not
reproduce the earlier stream assertion before its later failure. This establishes
a reaction to input, not a working menu or gameplay scene.

The run reported 135 failed DirectStorage requests after rejecting BCPack mode 7
(51,012 compressed bytes to 65,536 BC7 block bytes), plus a separate destination
access violation. That latter input file exists; the code is not a missing-file
error. The blank source name on format refusal is a diagnostic metadata gap.

The run subsequently lost its D3D12 device during a shared AMD GPU reset, which
interrupted the desktop session. The kernel names the compositor's timed-out
queue, while RADV calls Wine's context innocent; the ultimate trigger remains
unproved. The runtime terminated itself on device loss. No agent-issued stop
was used.

XCL's presenter is already windowed. Its separate title popup requests DWM
cloaking, but the installed Wine 11 implementation returns success without
cloaking. A separate private 1600x900 Wine virtual desktop is prepared to contain
both windows. It has not been launched or established GPU stability; it still
shares the GPU and does not reduce the title's internal 4K rendering. Further
work is currently offline analysis/builds.

Offline inspection uniquely matched the rejected 51,012-byte request to an
immutable local file range. All 16 BC7 entropy lanes validated to 8,192 symbols
each and consumed exactly the source length. Strict reconstruction refused an
unknown built-in endpoint-history entry (17). No provisional table entries or
zero-filled substitutes were accepted. This narrows a real loading blocker;
it does not establish correct texture output or rule out unrelated failures.

## Contained continuation with temporary textures

The user prioritized first gameplay and explicitly accepted temporary texture
artifacts. Source `09b089b4be9cae04c8a9c8669f32d1deec84dad8` includes the upstream
late physical-page correction and an opt-in valid BC7 placeholder. Its first
contained run still hit the stream assertion at 47.059 seconds without a logged
controller button. Both title and presenter were children of a named Wine desktop;
Wine enlarged it beyond the requested 1600x900 size.

A retry with scripted A reached the placeholder path and exposed unsupported BC5
requests. It then failed with D3D12 device loss `0x887a0005`. The kernel named the
game's timed-out graphics queue and RADV identified its context as guilty. The
existing GNOME process survived this reset. Window containment therefore did not
fix the GPU execution problem. No agent-issued stop was used.

Source `4b4f706dcd06568d663af5abc58acdf7df8093d0` extends the same opt-in path to
valid BC5 blocks. Its release build passed; actual loading efficacy is unverified.
The 19-patch source recipe reproduces this exact candidate tree.

A separate community BC7 decoder covered the identified chunk's required presets
and emitted 65,536 bytes with no missing-history, invalid-block or normalization
counters. An independent parser accepted all 4,096 blocks, and Linux/Windows
console helper outputs matched. This is structural evidence, not verified texture
accuracy; the helper is private and has not been integrated into the game runtime.

World rendering remains unverified. Source inspection found two-pass shader
metadata without a corresponding game draw-path executor. The current trace does
not prove that such a pipeline was bound or caused the GPU hang. Further work is
bounded draw/pipeline metadata and an instrumented GPU backend before another run.
