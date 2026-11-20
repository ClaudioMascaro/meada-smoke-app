"""Run with MEADA=/absolute/path/to/meada python3 scripts/workspace_smoke.py -v."""

import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import tempfile
import unittest


APP = Path(__file__).resolve().parents[1]
OWNER = "github.com/claudiomascaro/"
NAMES = ("meada-smoke-app", "meada-smoke-shared", "meada-smoke-lib")


class CorpusCase(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.root = Path(scratch.name)
        self.app, self.shared, self.lib = (self.root / name for name in NAMES)
        self.binary = shutil.which(os.environ.get("MEADA", "meada"))
        self.assertIsNotNone(self.binary, "Set MEADA to the binary under test")
        self.binary = str(Path(self.binary).resolve())
        for name in NAMES:
            source = APP.parent / name
            dest = self.root / name
            subprocess.run(["git", "clone", "--quiet", "--no-hardlinks", str(source), str(dest)],
                           check=True)
            subprocess.run(["git", "remote", "set-url", "origin", f"https://{OWNER}{name}.git"],
                           cwd=dest, check=True)
        self.manifest = self.root / "meada.workspace.toml"
        self.manifest.write_text('index_dir = "indexes"\n' + "".join(
            f'[[repository]]\nrepo = "{OWNER}{name}"\npath = "{name}"\n' for name in NAMES))

    def cli(self, *args, cwd=None, lang="en_US.UTF-8", code=0, stdin=""):
        env = {k: v for k, v in os.environ.items() if not k.startswith("MEADA_")}
        env.update(LANG=lang, LC_ALL=lang)
        run = subprocess.run([self.binary, *args], cwd=cwd or self.app, env=env, input=stdin,
                             text=True, capture_output=True, timeout=45)
        self.assertEqual(run.returncode, code, (args, run.stdout, run.stderr))
        return run


    def mcp(self, calls):
        messages = [
            {"id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05",
             "capabilities": {}, "clientInfo": {"name": "smoke", "version": "1"}}},
            {"method": "notifications/initialized"},
        ]
        for number, (tool, args) in enumerate(calls, 2):
            messages.append({"id": number, "method": "tools/call",
                             "params": {"name": tool, "arguments": args}})
        wire = "".join(json.dumps(dict(jsonrpc="2.0", **message)) + "\n" for message in messages)
        results = self.cli("mcp", stdin=wire)
        replies = {msg["id"]: msg["result"] for line in results.stdout.splitlines()
                   if "id" in (msg := json.loads(line))}
        self.assertEqual(set(replies), set(range(1, len(calls) + 2)))
        answers = []
        for number in range(2, len(calls) + 2):
            result = replies[number]
            self.assertFalse(result.get("isError"), result)
            answers.append(result["content"][0]["text"])
        return answers


class WorkspaceSmoke(CorpusCase):
    def test_workspace_and_solo_scope(self):
        self.cli("index")
        for lang, header, scope in [
            ("en_US", "workspace: 3 repositories", "no consumer in the workspace"),
            ("pt_BR", "workspace: 3 repositórios", "nenhum consumidor no workspace"),
            ("es_ES", "workspace: 3 repositorios", "ningún consumidor en el workspace"),
        ]:
            with self.subTest(lang=lang):
                lines = self.cli("status", lang=lang + ".UTF-8").stdout.splitlines()
                self.assertEqual(lines.count(header), 1)
                orphan = [line for line in lines if "/orphan.yml:" in line]
                self.assertEqual(len(orphan), 1, lines)
                self.assertIn(scope + ";", orphan[0])
        isolated = self.root / "solo" / self.shared.name
        isolated.parent.mkdir()
        self.shared.rename(isolated)
        solo = self.cli("status", cwd=isolated).stdout
        self.assertIn("workspace: 1 repository\n", solo)
        self.assertRegex(solo, r"/orphan\.yml: no consumer in github\.com/claudiomascaro/meada-smoke-shared;")

    def test_decisions_link(self):
        target = self.root / "decisions.toml"
        link = self.app / "meada.decisions.toml"
        link.write_text("decision = []\n")
        regular = self.cli("decide", "--list").stdout
        link.rename(target)
        link.symlink_to(target)
        self.assertEqual(self.cli("decide", "--list").stdout, regular)
        for dangling in (False, True):
            if dangling:
                target.unlink()
            for args in [(), ("--item", "missing"), ("--prune",), ("--decider",)]:
                with self.subTest(args=args, dangling=dangling):
                    run = self.cli("decide", *args, code=1)
                    self.assertEqual(run.stdout, "")
                    self.assertIn("a symbolic link", run.stderr)
                    self.assertEqual(link.readlink(), target)
                    self.assertFalse((self.app / "meada.decisions.toml.tmp").exists())
                    if dangling:
                        self.assertFalse(target.exists())
                    else:
                        self.assertEqual(target.read_bytes(), b"decision = []\n")

    def test_invalid_link_diagnostic(self):
        target = self.root / "bad.toml"
        target.write_text("items = [")
        (self.app / "meada.decisions.toml").symlink_to(target)
        reader = self.cli("decide", "--list", code=1)
        self.assertIn("unclosed array", reader.stderr)
        run = self.cli("decide", "--prune", code=1)
        self.assertIn("a symbolic link", run.stderr)
        self.assertEqual(target.read_bytes(), b"items = [")

    def test_go_keys_across_repositories(self):
        with (self.app / "meada.toml").open("a") as config:
            config.write('base_url_env = ["SMOKE_API_URL"]\n')  # last peer is lib
        route = self.lib / "app/orders/route.ts"
        route.parent.mkdir(parents=True)
        route.write_text('export function POST() { return new Response("{}"); }\n')
        for pkg, field, extra in [
            ("control", "label", ""), ("httpkey", "http", ""), ("oskey", "os", ""),
            ("shadow", "os", 'func ignore(os string) string { return os }'),
        ]:
            package = self.app / pkg
            package.mkdir()
            (package / "client.go").write_text(f'''package {pkg}
import ("net/http"; "os")
type Settings struct {{ {field} string }}
var cfg = Settings{{{field}: "test"}}
{extra}
func order() (*http.Request, error) {{
    return http.NewRequest(http.MethodPost, os.Getenv("SMOKE_API_URL") + "/orders", nil)
}}
''')
        self.cli("index")
        export = json.loads(self.cli("export").stdout)
        links = [link for link in export["links"] if link["contract"] == "http::POST::/orders"]
        items = self.cli("decide", "--list").stdout.splitlines()
        pending = [row.split("::")[1] for row in items
                   if row.startswith(OWNER + self.app.name + "::") and "/client.go::" in row]
        self.assertEqual(pending, ["shadow/client.go"])
        actual = sorted(link["consumer"].split("::")[1].split("/")[0] for link in links)
        self.assertEqual(actual, ["control", "httpkey", "oskey"])
        for link in links:
            self.assertEqual(link["level"], "inferred")
            self.assertIn("a base_url_env of peer " + OWNER + self.lib.name, link["reason"])
            self.assertTrue(link["provider"].startswith(OWNER + self.lib.name + "::"), link)

        # Exercise the open item's real CLI path. Select the one provider, first as a preview.
        site = OWNER + self.app.name + "::shadow/client.go::order::http.NewRequest#0"
        decisions = self.app / "meada.decisions.toml"
        preview = self.cli("decide", "--item", site, "--dry-run", stdin="1\n").stdout
        self.assertIn(site, preview)
        self.assertFalse(decisions.exists())
        self.cli("decide", "--item", site, stdin="1\n")
        self.assertIn(site, decisions.read_text())
        self.assertNotIn(site, self.cli("decide", "--list").stdout)
        route.unlink()
        self.assertIn("stale decision", self.cli("status").stdout)
        self.cli("decide", "--prune")
        self.assertNotIn(site, decisions.read_text() if decisions.exists() else "")

    def test_local_refresh_failure(self):
        self.cli("index")
        index = self.lib / ".meada/index.db"
        self.assertTrue(index.is_file())
        with sqlite3.connect(index) as db:
            db.execute("DROP TABLE symbols")
        source = self.lib / "src/smoke_cli/main.py"
        with source.open("a") as f:
            f.write("\n# changed after indexing\n")
        line = self.cli("status").stdout.splitlines()[-1]
        self.assertIn(OWNER + self.lib.name + ": no such table: symbols", line)

    def test_language_packs_and_incremental_refresh(self):
        samples = {
            "demo.cs": "class Demo { static int marker() => 1; }",
            "demo.go": "package demo\nfunc marker() int { return 1 }",
            "Demo.java": "class Demo { static int marker() { return 1; } }",
            "Demo.kt": "fun marker(): Int = 1",
            "demo.py": "def marker():\n    return 1",
            "src/lib.rs": "fn marker() -> i32 { 1 }",
            "demo.swift": "func marker() -> Int { return 1 }",
            "demo.ts": "export function marker(): number { return 1; }",
            "demo.js": "export function marker() { return 1; }",
        }
        (self.lib / "Cargo.toml").write_text('[package]\nname = "smoke"\nversion = "0.1.0"\n')
        for path, sample in samples.items():
            (self.lib / path).write_text(sample + "\n")
        self.cli("index")
        def markers():
            export = json.loads(self.cli("export", cwd=self.lib).stdout)
            return {row["span"]["path"]: row["id"] for row in export["symbols"]
                    if row["span"]["path"] in samples and "marker" in row["id"]}
        initial = markers()
        self.assertEqual(set(initial), set(samples))
        (self.lib / "demo.py").unlink()
        (self.lib / "src/lib.rs").write_text("fn renamed() -> i32 { 1 }\n")
        self.assertEqual(markers(), {k: v for k, v in initial.items() if k not in ("demo.py", "src/lib.rs")})
        for path in ("demo.py", "src/lib.rs"):
            (self.lib / path).write_text(samples[path] + "\n")
        self.assertEqual(markers(), initial)

    def test_mcp_three_repository_trace(self):
        site = OWNER + self.app.name + '::.github/workflows/ci.yml::jobs["through-lib"]'
        answers = self.mcp([
            ("search", {"kind": "ci", "query": "through-lib"}),
            ("context", {"symbol": site}),
            ("trace", {"from": site, "direction": "down"}),
        ])
        self.assertIn('jobs["through-lib"]', answers[0])
        self.assertIn(OWNER + self.lib.name + " .github/workflows/check.yml", answers[1])
        trace = answers[2]
        positions = [trace.index(OWNER + name + " .github/workflows/" + workflow)
                     for name, workflow in [(self.app.name, "ci.yml"), (self.lib.name, "check.yml"),
                                            (self.shared.name, "build.yml")]]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("2 hops", trace)

    def test_ci_and_package_contracts(self):
        self.cli("index")
        app = json.loads(self.cli("export").stdout)
        lib = json.loads(self.cli("export", cwd=self.lib).stdout)
        outputs = (app, lib)
        links = [row for graph in outputs for row in graph["links"]
                 if row["consumer"].startswith(graph["repository"] + "::")]
        mismatches = sorted(row["consumer"].split("/")[-1] for row in links
                            if "permissions mismatch" in row["reason"])
        self.assertEqual(mismatches, [
            "perms-empty.yml::jobs.call", "perms-job-over-pipeline.yml::jobs.call",
            "perms-read-all.yml::jobs.call", "perms-read.yml::jobs.call"])
        for graph, caller, target in [
            (app, 'ci.yml::jobs["through-lib"]', self.lib.name + "::.github/workflows/check.yml::."),
            (lib, 'check.yml::jobs["shared-build"]', self.shared.name + "::.github/workflows/build.yml::."),
        ]:
            hits = [row for row in graph["links"] if row["consumer"].endswith(caller)]
            self.assertEqual([(r["provider"], r["level"]) for r in hits], [(OWNER + target, "exact")])
        absent = {r["site"] for r in app["consumers"] if r.get("absent")}
        legacy = OWNER + self.app.name + "::.github/workflows/ci.yml::jobs.legacy"
        self.assertIn(legacy, absent)
        self.assertFalse(any(r["consumer"] == legacy for r in links))
        packages = [row for row in links if row["contract"].startswith("package::")]
        installs = [r for r in packages if r["provider"].endswith("pyproject.toml")]
        programs = [r for r in packages if r["provider"].endswith(".py::run")]
        self.assertEqual(len(installs), 1)
        self.assertIn('jobs["by-name"]', installs[0]["consumer"])
        prefix = OWNER + self.lib.name + "::.github/workflows/ci.yml::jobs.test.steps"
        self.assertFalse(any(r["consumer"] == prefix + "[2]" for r in packages))
        self.assertEqual([(r["provider"], r["level"]) for r in programs
                          if r["consumer"] == prefix + "[3]"],
                         [(OWNER + self.lib.name + "::src/smoke_cli/main.py::run", "inferred")])
        self.assertEqual(len(programs), 6)
        self.assertEqual({r["level"] for r in packages}, {"inferred"})
        self.assertTrue(any("run-cross.yml" in r["consumer"] and
                            r["provider"].startswith(OWNER + self.lib.name + "::") for r in programs))

    def test_cross_repo_orphan_kinds_and_refresh(self):
        (self.shared / "smoke.tf").write_text('resource "aws_sqs_queue" "idle" { name = "smoke-idle" }\n')
        (self.lib / "queue.yaml").write_text(
            "target: arn:aws:sqs:us-east-1:111111111111:smoke-missing\n")
        (self.shared / "rules.yaml").write_text(
            "groups:\n- name: smoke\n  rules:\n  - alert: SmokeDown\n    expr: up == 0\n"
            "    labels: {support: red}\n")
        receiver = self.lib / "alertmanager.yaml"
        receiver.write_text("route:\n  receiver: ops\n  match: {support: blue}\nreceivers: [{name: ops}]\n")
        compose = self.lib / "compose.yaml"
        compose.write_text("services:\n  worker:\n    image: localhost:5000/smoke/worker:1\n")
        self.cli("index")
        expected = {
            "channel::sqs::smoke-idle": "use", "channel::sqs::smoke-missing": "provisioner",
            "alert::support::red": "matcher", "alert::support::blue": "emitter",
            "image::localhost:5000/smoke/app": "runner", "image::localhost:5000/smoke/worker": "builder",
            "ci::" + OWNER + self.shared.name + "/.github/workflows/orphan.yml": "consumer",
        }
        status = self.cli("status").stdout
        for contract, side in expected.items():
            with self.subTest(contract=contract):
                self.assertIn(f"orphan {contract}: no {side} in the workspace;", status)
        receiver.write_text(receiver.read_text().replace("blue", "red"))
        compose.write_text(compose.read_text().replace("/worker:", "/app:"))
        refreshed = self.cli("status").stdout
        for contract in ("alert::support::red", "image::localhost:5000/smoke/app"):
            self.assertNotIn("orphan " + contract + ":", refreshed)
        lib = json.loads(self.cli("export", cwd=self.lib).stdout)
        contracts = {link["contract"] for link in lib["links"]}
        self.assertIn("alert::support::red", contracts)
        self.assertIn("image::localhost:5000/smoke/app", contracts)

    def test_partial_workspace(self):
        notice = "decisions and other workspace lines not evaluated"
        self.assertIn(notice, self.cli("status").stdout)
        self.assertFalse((self.shared / ".meada").exists())
        self.cli("index")
        self.assertNotIn(notice, self.cli("status").stdout)
        index = self.shared / ".meada/index.db"
        with sqlite3.connect(index) as db:
            db.execute("PRAGMA user_version = 1")
        self.assertIn(notice, self.cli("status").stdout)
        with sqlite3.connect(index) as db:
            self.assertEqual(db.execute("PRAGMA user_version").fetchone(), (1,))

    def test_manifest_diagnostic(self):
        args = ("--workspace", str(self.manifest))
        self.cli("index", *args)
        status = self.cli("status", *args).stdout
        self.assertIn("workspace: 3 repositories", status)
        index = self.root / "indexes" / (OWNER + self.lib.name) / "index.db"
        self.assertTrue(index.is_file())
        with sqlite3.connect(index) as db:
            db.execute("DROP TABLE symbols")
        status = self.cli("status", *args).stdout
        notice = [line for line in status.splitlines() if "not evaluated" in line]
        self.assertEqual(len(notice), 1, status)
        self.assertIn("no such table: symbols", notice[0])
        self.assertIn(OWNER + self.lib.name, notice[0])


if __name__ == "__main__":
    unittest.main()
