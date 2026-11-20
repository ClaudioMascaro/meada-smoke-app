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
