# meada-smoke-app

The consumer of the Meada CI smoke corpus: its pipelines call the reusable pipelines and the
actions of `meada-smoke-shared` and of `meada-smoke-lib` in every form of `uses`, with and
without `permissions` and `secrets`, and its `run` scripts install a package of the repository
and run its console script.

`CASES.md` lists every case and what GitHub does with it, written before the first run. The runs
of these pipelines on GitHub are the record that settles each row: a pipeline that is expected to
be refused is a case, not a broken build. `meada.toml` names the two peers, so the three
repositories index as one workspace when cloned side by side.
