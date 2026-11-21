# Cases

What GitHub does with each case, written before the first run, beside what ADR 0028 of
Meada says the index reads. A run on GitHub settles the second column; the third is what a
smoke of Meada checks against it. A case marked "open" has no expected answer yet.

| Case | Where | GitHub | Meada (ADR 0028) |
|---|---|---|---|
| `pipeline-branch` | app ci.yml by-branch | runs `build.yml` of shared at `main` | link, `@main`, keys `target` and `token` |
| `pipeline-tag` | app ci.yml by-tag | runs `build.yml` at the tag `v1` | link, `@v1`, no flag |
| `pipeline-old-commit` | app ci.yml by-old-commit | runs `build.yml` at the first commit | link, `ref mismatch` |
| `pipeline-head-commit` | app ci.yml by-head-commit | runs `build.yml` at the head commit | link, no flag while shared is indexed at that commit |
| `pipeline-secrets-inherit` | app ci.yml inherit | runs, every secret passed | link, `secrets: inherit` |
| `pipeline-through-wrapper` | app ci.yml through-wrapper | runs `wrapper.yml`, which runs `build.yml` of shared | link to `wrapper.yml`; `trace` reaches `build.yml` |
| `local-pipeline-in-reusable` | shared wrapper.yml inner | the file of shared at the commit of the called pipeline | link inside shared, `own repository` |
| `pipeline-through-lib` | app ci.yml through-lib | runs `check.yml` of lib, which runs `build.yml` of shared | link to lib; `trace` crosses three repositories |
| `chain-lib-to-shared` | lib check.yml shared-build | runs `build.yml` of shared | link, `@main` |
| `pipeline-string-on` | app ci.yml string-on | runs: `on: workflow_call` as a string is reusable | link |
| `pipeline-absent-at-head` | app ci.yml legacy | runs: `legacy.yml` exists at `v1` | consumer marked absent at the indexed commit, no link |
| `pipeline-matrix` | app ci.yml matrix | runs twice | one CI job, one consumer, one link |
| `needs` | app ci.yml after | runs after `by-branch` and `matrix` | references to both CI jobs |
| `pipeline-owner-case` | app owner-case.yml | runs: owner and repository match in any case | link (identity is lower-cased) |
| `pipeline-not-reusable` | app not-reusable.yml | refused: the called file has no `workflow_call` | consumer marked absent, with that reason |
| `pipeline-absent` | app absent-pipeline.yml | refused: no such file at `main` | consumer marked absent at the indexed commit |
| `local-in-reusable` | shared build.yml, step 2 | runs the `local-action` of the **caller**: the runner checked the caller out | unresolved, never a link to shared's folder |
| `action-root` | app ci.yml actions | runs the root action of shared | link to `ci::.../meada-smoke-shared` |
| `action-folder-tag` | app ci.yml actions | runs `setup/` at `v1` | link, `@v1` |
| `action-folder-yaml` | app ci.yml actions | runs `report/action.yaml` | link |
| `action-old-commit` | app ci.yml actions | runs `setup/` at the first commit | link, `ref mismatch` |
| `action-docker-only` | app ci.yml actions | builds and runs `image/Dockerfile` | no side and no absent mark |
| `action-in-action` | shared chain/action.yml; app ci.yml actions | runs `chain`, which runs `setup` | two links; `trace` crosses the composite action |
| `action-local` | app ci.yml actions | runs `local-action` of app | link, `own repository` |
| `action-docker-url` | app ci.yml actions | runs the image | no CI contract |
| `action-local-after-path-checkout` | app ci.yml checkout-path | runs `src/local-action` | unresolved (the checkout names a `path`) |
| `action-absent` | app absent-action.yml | the CI job fails: no action file in `missing/` | consumer marked absent at the indexed commit |
| `action-local-no-checkout` | app no-checkout.yml | the CI job fails: nothing was checked out | unresolved |
| `action-dollar` | app dollar.yml | open: whether GitHub accepts `$/<path>` | link, `own repository` |
| `self-local` | shared self.yml local | runs its own `build.yml` | link, `own repository` |
| `self-full-name` | shared self.yml by-name | runs its own `build.yml` at `main` | link, `@main` |
| `self-old-commit` | shared self.yml by-old-commit | runs its own `build.yml` at the first commit | link, `ref mismatch` |
| `self-local-action` | shared self.yml steps | runs `setup/` | link, `own repository` |
| `self-local-root` | shared self.yml steps | runs the root action (`uses: ./`) | open: ADR 0028 names `./<folder>`, not `./` |
| `lib-local-pipeline` | lib ci.yml own-check | runs `check.yml` of lib | link, `own repository` |
| `lib-action-root` | lib ci.yml test | runs the root action of shared | link |
| `permissions-job-read` | app perms-read.yml | refused: `release.yml` asks `contents: write`, the caller holds `read` | link with `permissions mismatch: contents write against read` |
| `permissions-job-write` | app perms-write.yml | runs | link, no flag |
| `permissions-not-declared` | app perms-default.yml | follows the repository setting, which no file holds | link, `not declared`, never compared |
| `permissions-read-all` | app perms-read-all.yml | refused | link with `permissions mismatch` |
| `permissions-write-all` | app perms-write-all.yml | runs | link, no flag |
| `permissions-empty` | app perms-empty.yml | refused: `build.yml` asks `contents: read`, `{}` holds none | link with `permissions mismatch: contents read against none` |
| `permissions-job-closes-pipeline` | app perms-job-over-pipeline.yml | refused: the CI job's block replaces the pipeline's | link with `permissions mismatch` |
| `install-path` | app run.yml installed | installs the package of `tools/greeter` | no named package side for a path install |
| `program-after-install` | app run.yml installed | runs `smoke-greet` of that package | program link, `inferred` (path install has no named package side) |
| `install-name` | app run.yml by-name | installs the wheel built one step before (`--no-index`) | consumer of the package, by name |
| `program-after-name-install` | app run.yml by-name | runs `smoke-greet` | program link, `inferred`; its named package was installed earlier in the CI job |
| `program-no-install` | app run.yml hidden-install | runs `smoke-greet`: a called script installed it | program link, `inferred` |
| `install-pipx` | app run.yml pipx | installs with pipx | no named package side for this local path |
| `program-after-pipx` | app run.yml pipx | runs `smoke-greet` | program link, `inferred` (local path) |
| `echo-is-no-command` | app run.yml negatives | prints the text | no side |
| `heredoc-not-read` | app run.yml negatives | prints the text | no side |
| `command-after-and` | app run.yml negatives | runs `pip --version` | no side: no install |
| `docker-push` | app run.yml image | pushes to the registry of the CI job | image builder `localhost:5000/smoke/app`, sited on the CI step |
| `docker-build-no-push` | app run.yml image | builds, pushes nothing | no side |
| `lib-install-path` | lib ci.yml test | installs the package of lib | no named package side for `pip install .` |
| `lib-program-after-install` | lib ci.yml test | runs `smoke-cli` | program link to the lib entry point, `inferred` |
| `install-vcs-url` | app run-cross.yml (by hand, corpus public) | installs lib from its Git URL | no named package side for a Git URL |
| `program-of-another-repository` | app run-cross.yml | runs `smoke-cli` of lib | program link across repositories |
| `orphan` | shared orphan.yml | never runs: nobody calls it | `orphan ci::` line in a scope that holds the callers |

## Cross-repository index

Use the three checkouts in the README. Each source and counterpart below is tracked in Git. The expected answers identify both ends so that a link to the wrong peer fails the case.

| Case | Source | Expected index |
|---|---|---|
| Go neutral field (#933) | app `orders/neutral/client.go` | `Client.CreateOrder` links to lib `openapi.yaml::POST /orders` at `inferred` through `SMOKE_ORDERS_URL`. |
| Go keys named like imports (#933) | app `orders/httpkey/client.go`, `orders/oskey/client.go` | Both calls have the same provider, reason and level as the neutral control. |
| Go parameter shadows an import (#933) | app `orders/shadow/client.go` | One open Go call, with lib's route as its candidate. |
| Persisted Go extraction ([meada#946](https://github.com/ClaudioMascaro/meada/issues/946)) | Same app and lib commits, index first built by the CLI before the Go fix | Upgrading the CLI and indexing again should resolve the same three clients as a cold index. On #943 the warm index still resolves only the neutral client. |
| Alert routing | app `monitoring/rules.yaml`, lib `alertmanager.yaml` | The `team=orders` emitter matches the lib receiver at `exact`. The app's `team=retired` has no matcher and the lib's `team=inventory` has no emitter. |
| Queue provisioning | app `config/queues.yaml`, lib `queues.tf` | The `orders` ARN has an `exact` provision from lib's `aws_sqs_queue.orders`. The `legacy` ARN has no provisioner and the `idle` queue has no use. |
| Container image | app `.github/workflows/run.yml`, lib `compose.yaml` | The lib service `orders` links to the app's pushed `localhost:5000/smoke/app` at `exact`. The `preview` image has no runner and `retired` has no builder. |
| CI chain and orphan scope (#855) | app `ci.yml` through-lib, lib `check.yml`, shared `build.yml` and `orphan.yml` | Trace crosses app → lib → shared. In the three-repository status, shared's orphan has no consumer in the workspace. With shared cloned alone the line names shared. |
| Partial manifest (#934) | app `meada.workspace.toml` | Before indexing, status reports three repositories and the pending evaluation. After indexing, all three are indexed and the warning clears. |
| Linked decision (#932) | app branch `case/932-linked-decision`, lib `orders/decisions.toml` | Reading the link resolves the shadowed Go call to the lib route. A saving mode refuses the link and preserves it and its target. |
| Malformed linked target (#932) | app branch `case/932-malformed-target`, link to lib `openapi.yaml` | A read reports the decisions parsing error. A saving mode should identify the symlink before attempting that parse. |

## Resolution controls

Use the `validate/index-and-resolution-stability` branches of app, lib and shared together.
Lib's `openapi.yaml` and shared's `openapi.yaml` both declare `POST /orders`. The app
declares `SMOKE_ORDERS_URL` only for lib. These expected answers are derived from source before
running Meada.

| Source under `orders/` | Expected |
|---|---|
| `evidence/client.go`, `Client.ViaMethod` and `ViaParameter` | Both send `POST /orders` to the base named by `SMOKE_ORDERS_URL`. Lib alone is the peer declared for that variable. Both links are inferred. |
| `evidence/client.go`, `Relative` | There is no authority in `/orders`. Both lib and shared serve the verb and path, so the link is ambiguous. |
| `evidence/client.go`, `ViaUnknownParameter` | The argument is not known from source. The base stays unreadable and neither provider is chosen. |
| `evidence/client.go`, `QueryAppend` and `QuerySuffix` | Only the query varies. Both link at inferred to lib's `POST /orders`. |
| `evidence/client.go`, `PathSuffix` | The suffix can change the path. Lib's `POST /orders` is not uniquely established. |
| `evidence/recursive.go`, `PlainA` and `PlainB` | The independently called wrapper sends GET to `/plain-a` and `/plain-b`. Neither uses the recursive wrapper. |
| `mutation/store.go`, `Archive`, `Choose` and `Current` | `Archive` writes `orders-archive`. `Choose` may write either table. Neither can be an exact write to `orders` alone. `Current` writes `orders` exactly. Both tables are defined by lib's `archive.tf`. |
| `overloads/Formats.java`, `textOrder` and `countOrders` | The two `encode` overloads each take one unlabeled argument. Java chooses by argument type. Meada's existing rule leaves both calls ambiguous. |

## HTTP clients that return the base URL

Use this app branch together with lib at `cb746acf3fef864145d4cedad8a21977414b3309`
and shared at `0aabcee48fe9d2d2e401a514bcfd0f4af8984501`. Both peers serve
`POST /orders`. Only lib owns `SMOKE_ORDERS_URL` in this app's peer configuration.
Shared declares the host `shared.smoke.example`.

| Source under `orders/clients/` | Expected result from the source |
|---|---|
| C#, Rust, Swift and TypeScript order clients | The helper returns the configured base. Each POST links to lib at `inferred` through `SMOKE_ORDERS_URL`. |
| Go `SendConfigured` and Python `send_configured` | Each uses the environment reader's return value and links to lib with the same reason. |
| Go `SendShared` | The deferred function overwrites the named result with shared's host before the caller receives it. A link from this caller to lib is a false positive. |
| Python `send_shared` | The decorator factory installs a replacement callable returning shared's host. A link from this caller to lib is a false positive. |
| Java and Kotlin `sendOrder` | Each calls its own class's private `ordersBase()`. Both POSTs should link to lib. Renaming one private helper and its call should preserve both answers. |

From app, run `meada export`. Filter `calls` by `id`, `consumers` by `site` and
`links` by `consumer` for the path `orders/clients/`. For the Go and Python
overrides, a reader that cannot establish the replacement host may leave the
endpoint unresolved. The original function body's environment read cannot
justify selecting lib.

### Class decorator replacing the URL method

The separate [Meada #962](https://github.com/ClaudioMascaro/meada/issues/962)
probe is `orders/clients/python/class_probe.py`. From the app run
`SMOKE_ORDERS_URL=https://lib.smoke.example python3 scripts/record-class-authority.py`.
The recorder substitutes the transport in-process and prints each caller, verb and URL.
Both peers still declare `POST /orders`, with the environment key belonging to lib.

| Source state | Changed.send | Ordinary.send |
|---|---|---|
| As committed | POST to `https://shared.smoke.example/orders` | POST to `https://lib.smoke.example/orders` |
| Remove only `@install` | POST to `https://lib.smoke.example/orders` | POST to `https://lib.smoke.example/orders` |
| Restore `@install` | POST to `https://shared.smoke.example/orders` | POST to `https://lib.smoke.example/orders` |

At each `requests.post#0` site that uses the original method, the environment
authority selects lib at `inferred`. With the decorator present, a reader that
cannot establish the replacement host leaves Changed's request open with both
compatible POST candidates and a limit naming its origin method. Keep these
observations separate from the ten other HTTP sites and the three SQS cases.

### SQS provisioning through a returned URL

The three senders in `orders/events/publisher.ts` use the SQS SDK. Both
`publishOrder` (a returned queue URL) and `publishLiteral` target
`smoke-orders`. Each should have one exact provisioning link to
lib's `queues.tf::aws_sqs_queue.orders`. The third sender, `publishSelected`,
chooses between `smoke-legacy` and `smoke-orders` at runtime. It cannot
unconditionally name lib's `orders` queue. Check the `provisions` array for
each sender separately.
