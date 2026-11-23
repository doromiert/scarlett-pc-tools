# Separate XCL patch series

Upstream: https://github.com/ivall/xcl

This directory is an independent GPL-2.0-only component. Its patches are not
licensed under the original tools' GPL-3.0-or-later license and must not be
combined into the Leonida implementation. See [LICENSE](LICENSE) and the upstream
source's attribution and third-party notices. Mail patches preserve commit
authorship, including the upstream crash-report fix.

Base: `eaa36b62768fe1eedb87d010a19148854c9a3952`.
Setup-tested source: `0cb3173bbc47e3aa05cb288cb462005a0f16fff9`.
Expected resulting Git tree: `347aecd3e4b04a8d3b7b1c55ea6bce0a39cce78d`.

Apply the 14 patches in `series.txt` order. The sequence was applied to a fresh
private worktree and reproduced that exact tree. Register-only crash probes are
not part of this setup-tested series. No game files, translated shaders or binary
artifacts are distributed here.

See [XCL_INTEGRATION.md](../../XCL_INTEGRATION.md) for the tested dependencies,
launch settings, actual result and remaining limitations.
