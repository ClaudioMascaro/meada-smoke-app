"""Replay Meada's standalone export fixtures inside disposable smoke workspaces."""
from collections import Counter
import json
import os
from pathlib import Path
import shutil
import unittest

from workspace_smoke import CorpusCase


def inventory(export):
    """Keep multiplicity, symbol/call locations and the roles and sites of contracts."""
    counts = Counter()
    prefix = export["repository"] + "::"
    for kind in ("symbols", "calls", "providers", "consumers"):
        for row in export[kind]:
            if kind in ("symbols", "calls"):
                normalized = dict(row)
                for field in ("id", "caller", "target", "decorates"):
                    if normalized.get(field):
                        normalized[field] = normalized[field].removeprefix(prefix)
                if "candidates" in normalized:
                    normalized["candidates"] = [candidate.removeprefix(prefix)
                                                for candidate in normalized["candidates"]]
                counts[kind, json.dumps(normalized, sort_keys=True)] += 1
            else:
                site = "." if row["site"] == export["repository"] else row["site"].removeprefix(prefix)
                counts[kind, site, row.get("contract")] += 1
    for link in export["links"]:
        if link["consumer"].startswith(prefix) and link["provider"].startswith(prefix):
            counts["link", link["consumer"].removeprefix(prefix),
                   link["provider"].removeprefix(prefix), link["contract"], link["level"]] += 1
    return counts


def overlay(source, destination):
    for file in source.rglob("*"):
        if file.is_file():
            target = destination / file.relative_to(source)
            if target.exists():
                raise FileExistsError(target)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(file, target)


class GoldenSmoke(CorpusCase):
    def test_infrastructure_queries(self):
        fixtures = Path(os.environ["MEADA_SOURCE"]) / "tests/fixtures"
        for fixture, symbol, edge in [
            ("serverless-nodes", "functions.createOrder", "OrdersQueue via Ref"),
            ("cloudformation-nodes", "OrdersFunction", "OrdersApi via Ref"),
            ("kubernetes-nodes", "Ingress.networking.k8s.io/shop-dev/dev-edge",
             "Service/shop-dev/dev-api via backend"),
        ]:
            with self.subTest(fixture=fixture):
                destination = self.shared / fixture
                overlay(fixtures / fixture, destination)
                search, context, trace = self.mcp([
                    ("search", {"kind": "iac", "query": symbol}),
                    ("context", {"symbol": symbol}),
                    ("trace", {"from": symbol, "direction": "down"}),
                ])
                self.assertIn(self.shared.name + " " + fixture + "/", search)
                self.assertIn(symbol, context)
                self.assertIn(edge, trace)
                shutil.rmtree(destination)

    def test_gcp_run(self):
        source = Path(os.environ["MEADA_SOURCE"]) / "tests/fixtures/gcp-run"
        shutil.copyfile(source / "main.tf", self.shared / "run.tf")
        shutil.copyfile(source / "worker.ts", self.lib / "worker.ts")
        shutil.copyfile(source / "build.yml", self.lib / ".github/workflows/build.yml")
        export = json.loads(self.cli("export", cwd=self.lib).stdout)
        for method, queue in [("legacy", "tasks-v1"), ("current", "tasks-v2"), ("batch", "tasks-job")]:
            hits = [row for row in export["providers"] if f"::worker.ts::{method}::" in row["site"]]
            self.assertEqual([row["contract"] for row in hits], ["channel::sqs::" + queue])
            self.assertIn(self.shared.name + "::run.tf::google_cloud_run", hits[0]["via"])
        image = [r for r in export["links"] if r["contract"] == "image::ghcr.io/acme/gcp-worker"]
        self.assertEqual(len(image), 3)
        self.assertEqual(sum(r["level"] == "inferred" for r in image), 1)

    def test_asyncapi_code_and_document(self):
        fixtures = Path(os.environ["MEADA_SOURCE"]) / "tests/fixtures"
        shutil.copyfile(fixtures / "asyncapi-events/asyncapi.yaml", self.lib / "asyncapi.yaml")
        (self.lib / "meada.toml").write_text("[serve]\n")
        shutil.copyfile(fixtures / "asyncapi-services/src/kafka.ts", self.app / "kafka.ts")
        export = json.loads(self.cli("export").stdout)
        for topic in ("orders.created", "payments.requested"):
            matching = [r for r in export["links"] if r["contract"] == "channel::kafka::" + topic]
            self.assertTrue(any("asyncapi.yaml" in r["consumer"] + r["provider"]
                                and "kafka.ts" in r["consumer"] + r["provider"] for r in matching), topic)

    def compare_fixture(self, name):
        samples = Path(os.environ["MEADA_SOURCE"]) / "tests"
        fixture = samples / "fixtures" / name
        golden = json.loads((samples / "golden" / (name + ".export.json")).read_text())
        # Overlay onto a real peer without overwriting any tracked corpus files.
        files = [path.relative_to(fixture) for path in fixture.rglob("*") if path.is_file()]
        self.assertTrue(files, name)
        peer = next((repo for repo in (self.shared, self.lib, self.app)
                     if all(not (repo / path).exists() for path in files)), None)
        self.assertIsNotNone(peer, name)
        before = inventory(json.loads(self.cli("export", cwd=peer).stdout))
        if name == "conformance-go":
            overlay(samples / "fixtures/conformance-go-ledger", self.lib)
        if name == "jvm-gradle-client":
            overlay(samples / "fixtures/jvm-gradle", self.lib)
            overlay(samples / "fixtures/jvm-maven", self.app)
        overlay(fixture, peer)
        actual = inventory(json.loads(self.cli("export", cwd=peer).stdout))
        expected = before + inventory(golden)
        self.assertEqual(actual, expected,
                         f"{name}: missing {list((expected-actual).items())[:5]}, "
                         f"unexpected {list((actual-expected).items())[:5]}")


# The comparison assumes a standalone export at the fixture root with no injected peers.
CASES = """
asyncapi-events chain-catalog channels-api channels-jobs-api channels-queues-api documents-shapes
gateway-billing http-api http-express iac-http-sam iac-http-serverless iac-http-terraform
aws-sdk-alias-env aws-sdk-batches aws-sdk-csharp aws-sdk-go aws-sdk-java aws-sdk-origins
azure-sdk-arrow-bindings azure-sdk-csharp azure-sdk-env azure-sdk-go azure-sdk-java
azure-sdk-mutations azure-sdk-origins azure-sdk-overloads azure-sdk-python azure-sdk-same-handler
azure-sdk-ts azure-sdk-typed-env azure-sdk-values-env azure-sdk-variants
cargo-lib conformance-csharp conformance-go conformance-java conformance-kotlin conformance-python
conformance-rust conformance-swift-alias conformance-swift-app conformance-swift-capitalized
conformance-swift-implicit conformance-swift-packages conformance-swift conformance-ts-js
dotnet-lib gcp-sdk-await gcp-sdk-controls gcp-sdk-csharp gcp-sdk-env gcp-sdk-go
gcp-sdk-helper-kinds gcp-sdk-java gcp-sdk-memo-mutations gcp-sdk-mutations gcp-sdk-python
gcp-sdk-resource-sites gcp-sdk-ts gopkg-lib jvm-gradle-client jvm-gradle jvm-maven
kotlin-pkg-lib pkg-pylib pkg-shared pkg-uv-sources rust-item-macros swift-pkg-kit swift-pkg-lib
""".split()

for case in CASES:
    setattr(GoldenSmoke, "test_" + case.replace("-", "_"),
            lambda self, name=case: self.compare_fixture(name))

if __name__ == "__main__":
    if "MEADA_SOURCE" not in os.environ:
        raise SystemExit("Set MEADA_SOURCE to a Meada source checkout containing tests/golden")
    unittest.main()
