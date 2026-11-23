# Working on scarlett-pc-tools

- Keep dumps and every generated game artifact outside Git checkouts. Never add
  game binaries, console libraries, keys, shaders, extracted assets or traces.
- Use synthetic inputs for tests. No excerpts from commercial binaries in fixtures.
- For boot work, prioritize real executable launches and concrete failures. Synthetic
  checks do not establish playability. Run `scripts/check_public_tree.py` before publication.
- Distinguish loader setup, DLL/TLS initialization, executable entry and rendered
  gameplay in reports. Import counts and clean exits do not establish playability.
- Reuse upstream runtime implementations. Keep their licenses and attribution;
  send reusable runtime fixes to the owning upstream when publication is authorized.
- Simulation timing separation and gyro aiming are requirements in ROADMAP.md,
  not implemented features. Verify them against a playable scene before claiming support.
