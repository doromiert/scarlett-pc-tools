# Separate XCL patch series

Upstream: https://github.com/ivall/xcl

This directory is an independent GPL-2.0-only component. Its patches are not
licensed under the original tools' GPL-3.0-or-later license and must not be
combined into the Leonida implementation. See [LICENSE](LICENSE) and upstream
attribution/third-party notices. Mail patches preserve commit authorship.

Base: `eaa36b62768fe1eedb87d010a19148854c9a3952`.
Current build candidate: `2e58f54f32a49961f4ba3f376277f4207a13e71d`.
Expected resulting Git tree: `e243c656bde257adff33a56cbb03757e925d216d`.

Apply all 33 patches in `series.txt` order. The applied series reproduced that
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

An actual Linux run with this candidate plus private CPU diagnostics rendered
colored startup frames and loading artwork on a spare integrated GPU, then
self-exited after a GPU timeout/device loss. The desktop GPU was inaccessible to
the game; GNOME survived. This is failure isolation, not a stability or gameplay
claim. Fullscreen CPU output was very slow.

No game files, translated shaders, captured payloads or binary artifacts are
distributed here. See [XCL_INTEGRATION.md](../../XCL_INTEGRATION.md) for exact
dependencies, settings, failure evidence and limitations.
