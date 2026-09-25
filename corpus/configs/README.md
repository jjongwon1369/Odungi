# Corpus tier declarations

`tiers.json` is the registry for configured tiers, the pinned repository, the data-model directory, and each output root. Tier names are not hardcoded in Python.

`c3.json`, `c6.json`, `c12.json` declare Device Type membership, inheritance, corpus version, and snapshot namespace. Inheritance is resolved before source discovery. `overrides.json` contains explicit cross-device and common-base policies that cannot be inferred safely from a single Device Type XML file.

These declarations do not authorize extraction. Run `scripts/corpus/generate_scope.py --all` to create deterministic drafts for every registered tier, review each draft, and finalize the full `scope.json` and `coverage_matrix.csv` before extraction.
