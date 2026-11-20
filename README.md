# meada-smoke-app

The consumer of the Meada CI smoke corpus: its pipelines call the reusable pipelines and the
actions of `meada-smoke-shared` and of `meada-smoke-lib` in every form of `uses`, with and
without `permissions` and `secrets`, and its `run` scripts install a package of the repository
and run its console script.

`CASES.md` lists every case and what GitHub does with it, written before the first run. The runs
of these pipelines on GitHub are the record that settles each row: a pipeline that is expected to
be refused is a case, not a broken build. `meada.toml` names the two peers, so the three
repositories index as one workspace when cloned side by side.

## Running the workspace smoke

Clone this repository, meada-smoke-shared and meada-smoke-lib side by side. On a Unix host with Python 3.9 or later and Git, run the following from this repository. Use the CLI built from the commit under review. For the second command, point MEADA_SOURCE to the Meada checkout at that commit.

```sh
MEADA=/absolute/path/to/meada python3 -B scripts/workspace_smoke.py -v
MEADA=/absolute/path/to/meada MEADA_SOURCE=/absolute/path/to/meada-checkout python3 -B scripts/golden_smoke.py -v
```

Each test creates fresh local clones at the checked-out commits and assigns the published GitHub origins. Changes to files, symlinks, manifests and SQLite indexes happen in those disposable clones. Test cases use the CLI binary and its MCP stdio endpoint. The runner does not execute fixture programs or trigger workflows. A failing assertion makes the command exit nonzero. Pass a unittest name such as `WorkspaceSmoke.test_manifest_diagnostic` to isolate one case.

The workspace suite exercises the three-repository CI trace, package resolution, language readers, resource and alert routing, image links, file refresh, orphan scope, decision-file links, Go import handling and partial indexes. The golden suite overlays version-matched Meada fixtures onto the smoke peers. It compares the multiplicity and site of each symbol, call and contract side with the reviewed export plus the peer's original inventory. Separate cases check Cloud Run and AsyncAPI across repository boundaries and query Kubernetes, CloudFormation and Serverless resources over MCP. The Go case resolves an open item interactively, removes its route, checks the stale decision and prunes it. Optional server services, browser UI and deployment need their own integration environment.
