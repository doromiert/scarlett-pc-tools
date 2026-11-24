# Separate XCL patch series

Upstream: https://github.com/ivall/xcl

This directory is an independent GPL-2.0-only component. Its patches are not
licensed under the original tools' GPL-3.0-or-later license and must not be
combined into the Leonida implementation. See [LICENSE](LICENSE) and upstream
attribution/third-party notices. Mail patches preserve commit authorship.

Base: `eaa36b62768fe1eedb87d010a19148854c9a3952`.
Current build candidate: `73bbf6d69e4ea82f4dca7a922fa51721f320acb4`.
Expected resulting Git tree: `f9aa02de3d0d1860fdea1b2701f596e37797b071`.

Apply all 53 patches in `series.txt` order. The applied series reproduced that
exact tree in a private worktree. The first 14 reproduce the earlier setup-tested
source `0cb3173bbc47e3aa05cb288cb462005a0f16fff9` (tree
`347aecd3e4b04a8d3b7b1c55ea6bce0a39cce78d`).

Patches 15–19 add default-off register-only diagnostics, source names for refused
storage requests, an upstream physical-page timing correction, and explicit
opt-in BC7/BC5 texture placeholders. The BC7 path was observed in the real game;
the BC5 extension was subsequently exercised in a real run. No playable scene is verified.

Patches 20–33 add bounded draw diagnostics, strict explicit GPU selection,
headless CPU frame capture, upstream texture/memory corrections, native objects
at shared-page operations, opt-in BC1 placeholders, float4 constant-buffer
descriptors, and exact bounded DirectStorage memory reads. Upstream authorship is
preserved. Private game-specific fault instrumentation is excluded.

An earlier actual Linux integration plus private CPU diagnostics rendered
colored startup frames and loading artwork on a spare integrated GPU, then
self-exited after a GPU timeout/device loss. The desktop GPU was inaccessible to
the game; GNOME survived. This is failure isolation, not a stability or gameplay
claim. Fullscreen CPU output was very slow.

No game files, translated shaders, captured payloads or binary artifacts are
distributed here. See [XCL_INTEGRATION.md](../../XCL_INTEGRATION.md) for exact
dependencies, settings, failure evidence and limitations.

Patches 34–38 add an explicitly configured sampler-heap input experiment,
display-resolution CPU capture, sampled live-capture diagnostics, native staging
resource identity at sparse-copy boundaries, and the observed five-argument
Wait64BitValueX ABI. The clean source tree builds and strict patch application
reproduces the expected tree. Actual execution used this logic with additional
private diagnostics; the clean public build has not been run against the title.
Setup is rendered and responds to input, but heavy loading still causes a GPU
queue timeout/reset. No playable scene is verified.

Patches 39–41 add a root-flag-directed graphics heap-input experiment, preserve
the original console heap bindings including explicit unbinding, and retain
native command-signature identity for ExecuteIndirect. Actual execution with
additional private diagnostics passed the earlier fullscreen-draw hang and
later passed the command-signature assertion after the identity correction.

Patch 42 adds the opt-in observed eight-argument XG CopyFromSubresource layout.
Actual execution passed the command-signature assertion and, with this setting,
completed two texture copies before a later DXIL-to-SPIR-V compiler assertion.
The current 50-patch tree builds and matches the expected tree above. No playable
scene is verified; actual runs include additional private diagnostics.

Patches 43–44 add caller-selected private shader capture and a caller-selected
DXC `-O0` workaround. Optimized and unoptimized DXIL use separate disk namespaces;
the translated fast caches are bypassed only for selected programs.
The actual captured failing shader passed CPU-only SPIR-V validation at `-O0`;
actual title validation passed the first offending shader and reached a later
shader compiler assertion. A second captured shader passes CPU-only validation
at `-O0`; a run selecting both is in progress. All 53 patches apply strictly from the pinned
base and reproduce the tree above; a separate release build passed. The clean
public binary has not run. No game-derived shader hashes or data are included.

Patch 45 limits the translated-cache bypass to the selected shaders. Patch 46
preserves upstream authorship for the swizzle-table period correction, merged
upstream after a live loading profile identified table construction as a major
CPU cost. Its runtime performance effect remains unmeasured.

Patch 47 adds opt-in 40-bit graphics-overflow reservations using VirtualAlloc2
address requirements. Actual allocations fit the bound and the previous BVH
address-width failure disappeared; a later title error remains under
investigation. It does not extend translated GPU visibility beyond UMA.
All 53 patches apply strictly to the pinned base and the resulting source builds.

Patch 48 retains native query-heap identity, clearing an assertion exposed by the
larger coherent-memory configuration in an actual run. That run rendered the
local account picker but advanced extremely slowly. Patches 49–50 preserve
upstream's detile column/row precomputation and whole-row linear copy paths,
matching a leading live CPU hotspot. They have since run in the private
integration. All 53 patches apply strictly and the source builds; an isolated
speedup from patches 49–50 and controllable gameplay remain unverified.

Patch 51 lets keyboard movement use a foreground window owned by the title's
process when the headless renderer has not created XCL's presentation window.
The existing keyboard/mouse configuration gate and normal attached-window path
remain in force. Raw mouse capture still requires an attached window and message
handler. Source inspection identified the missing movement-window binding; the
live run independently accepted a D-pad keyboard press, and a longer A press was
followed by intro frames. The fallback has since accepted the mapped Y key in an
actual headless run; controllable WASD gameplay remains unverified.

Patch 52 incorporates upstream's unchanged-content check before texture detiling
and upload. Patch 53 discards remembered content after upload failures. They
apply strictly and build in the separate clean candidate. An actual private
integration improved median captured intro output from 6.41 to 3.83 seconds per
frame in successive samples, still far too slow for use. Gameplay and visual
correctness remain unverified. `XCL_TEXTURE_SKIP_UNCHANGED=0` disables the
optimization.
