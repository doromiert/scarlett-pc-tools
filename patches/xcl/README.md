# Separate XCL patch series

Upstream: https://github.com/ivall/xcl

This directory is an independent GPL-2.0-only component. Its patches are not
licensed under the original tools' GPL-3.0-or-later license and must not be
combined into the Leonida implementation. See [LICENSE](LICENSE) and upstream
attribution/third-party notices. Mail patches preserve commit authorship.

Base: `eaa36b62768fe1eedb87d010a19148854c9a3952`.
Current build candidate: `4b4f706dcd06568d663af5abc58acdf7df8093d0`.
Expected resulting Git tree: `7a0240d69b9929ee86448b3e86baf6bf21984913`.

Apply all 19 patches in `series.txt` order. The applied series reproduced that
exact tree in a private worktree. The first 14 reproduce the earlier setup-tested
source `0cb3173bbc47e3aa05cb288cb462005a0f16fff9` (tree
`347aecd3e4b04a8d3b7b1c55ea6bce0a39cce78d`).

Patches 15–19 add default-off register-only diagnostics, source names for refused
storage requests, an upstream physical-page timing correction, and explicit
opt-in BC7/BC5 texture placeholders. The BC7 path was observed in the real game;
the BC5 extension is build-checked only. No playable scene is verified.

No game files, translated shaders, captured payloads or binary artifacts are
distributed here. See [XCL_INTEGRATION.md](../../XCL_INTEGRATION.md) for exact
dependencies, settings, failure evidence and limitations.
