# Chronicle Build Charter

When implementing Chronicle (engine, personal source graph, vault, specimens):

1. Read `rosetta_docs/process/chronicle-build-charter.md`.
2. Read `~/.local/share/rosetta/chronicle-build/CURRENT-STATE.md` if present.
3. Build the smallest usable V1. Architectural forks that are cheap to
   revert are GREEN — pick a default and continue. YELLOW is not an
   automatic stop. RED is irreversible blast radius (privacy, only-copy
   deletion, keys, unauthorized capture).
4. Protect vault evidence and irreversible boundaries. Experiment with
   replaceable code. Do not create a new primitive because a prompt named
   one.

The charter is the decision store. Ready Room chat is not.
