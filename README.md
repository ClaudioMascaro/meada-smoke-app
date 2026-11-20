# meada-smoke-app

The consumer of the Meada CI smoke corpus: its pipelines call the reusable pipelines and the
actions of `meada-smoke-shared` and of `meada-smoke-lib` in every form of `uses`, with and
without `permissions` and `secrets`, and its `run` scripts install a package of the repository
and run its console script.

`CASES.md` lists every case and what GitHub does with it, written before the first run. The runs
of these pipelines on GitHub are the record that settles each row: a pipeline that is expected to
be refused is a case, not a broken build. `meada.toml` names the two peers, so the three
repositories index as one workspace when cloned side by side.

## Indexing the Orders workspace

The Go clients in this repository call the Orders API declared in the lib repository. The app publishes an image and emits alerts. Lib deploys the image, routes the alerts and provisions an SQS queue used by the app. The existing app → lib → shared workflow chain exercises a third repository.

To reproduce the corpus while the companion PRs are open, start from a fresh directory:

```sh
git clone -b validate/workspace-contracts https://github.com/ClaudioMascaro/meada-smoke-app
git clone -b validate/workspace-contracts https://github.com/ClaudioMascaro/meada-smoke-lib
git clone https://github.com/ClaudioMascaro/meada-smoke-shared
git -C meada-smoke-shared checkout 51703923bd1f76c0b948db8afb1fa52fe86300c1
cd meada-smoke-app
meada index
meada export
meada decide --list
meada status
```

The cross-repository table in `CASES.md` names the expected providers, levels, open calls and unmatched counterparts. To exercise server-mode indexing, run `meada status --workspace meada.workspace.toml` before and after `meada index --workspace meada.workspace.toml`. That manifest stores its indexes beside the three checkouts in `../.smoke-indexes/`.

Two scenario branches preserve the filesystem states for issue #932. Switch the app checkout to `case/932-linked-decision` or `case/932-malformed-target`, keep lib and shared at the same revisions, and compare `meada decide --list` with `meada decide --prune`.

To reproduce the Go upgrade case, use two fresh sets of sibling checkouts at identical corpus commits. In the first app checkout run the #941 binary's `index`, then the #943 binary's `export`, `index` and `export`. In the second app checkout run #943's `index` and `export`. Compare the `consumer` and `provider` fields of the `http::POST::/orders` links. The expected caller set and the observed discrepancy are recorded in [meada#946](https://github.com/ClaudioMascaro/meada/issues/946).

The [returned-base cases](CASES.md#http-clients-that-return-the-base-url) use
the eight HTTP language packs. To index them, clone the three repositories as
siblings, check this app out at `validate/returned-order-authority`, lib at
`cb746acf3fef864145d4cedad8a21977414b3309` and shared at
`0aabcee48fe9d2d2e401a514bcfd0f4af8984501`. Run `meada export` from app.
