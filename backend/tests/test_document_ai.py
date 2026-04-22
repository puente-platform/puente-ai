"""Tests for the Document AI entity-type -> internal field-key mapping.

This test suite specifically exercises the `field_mapping` loop inside
`extract_invoice_data`, which had a silent PascalCase/snake_case mismatch
against Invoice Parser v2 that caused every real upload to land in
Firestore with `extraction.fields == {}` (KAN-44).

Integration tests elsewhere (test_analyze, test_pipeline_integration,
test_isolation) bypass this loop by writing `fields` directly, so that
mapping had no coverage before this file existed.
"""

from __future__ import annotations

import importlib.util
import logging
import os
import pathlib
import sys
import types
import unittest
from unittest.mock import MagicMock, patch


MODULE_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "app"
    / "services"
    / "document_ai.py"
)


def _build_fake_google_modules() -> dict[str, types.ModuleType]:
    """Build minimal stand-ins for google-cloud-documentai / api-core.

    The real packages are heavy and aren't needed for this unit — we only
    need `documentai.DocumentProcessorServiceClient` and the named
    exception classes to exist when `document_ai.py` is imported.

    Returns a flat mapping from dotted module name -> fake ModuleType that
    callers pass into `patch.dict(sys.modules, ...)`. Using a scoped patch
    (instead of mutating `sys.modules` globally via `setdefault`) means
    the fakes never leak into other test modules — which was a real
    flakiness risk when suites that *do* depend on the real
    `google.cloud.documentai` are collected in the same pytest run.
    """
    google_mod = types.ModuleType("google")
    cloud_mod = types.ModuleType("google.cloud")
    google_mod.cloud = cloud_mod

    documentai_mod = types.ModuleType("google.cloud.documentai")

    class _FakeClient:
        def __init__(self, *_, **__):
            pass

    class _FakeGcsDocument:
        def __init__(self, gcs_uri: str, mime_type: str):
            self.gcs_uri = gcs_uri
            self.mime_type = mime_type

    class _FakeProcessRequest:
        def __init__(self, name: str, gcs_document):
            self.name = name
            self.gcs_document = gcs_document

    documentai_mod.DocumentProcessorServiceClient = _FakeClient
    documentai_mod.GcsDocument = _FakeGcsDocument
    documentai_mod.ProcessRequest = _FakeProcessRequest
    cloud_mod.documentai = documentai_mod

    api_core_mod = types.ModuleType("google.api_core")
    client_options_mod = types.ModuleType("google.api_core.client_options")

    class _ClientOptions:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    client_options_mod.ClientOptions = _ClientOptions
    api_core_mod.client_options = client_options_mod

    exceptions_mod = types.ModuleType("google.api_core.exceptions")

    class _PermissionDenied(Exception):
        pass

    class _NotFound(Exception):
        pass

    class _ResourceExhausted(Exception):
        pass

    class _DeadlineExceeded(Exception):
        pass

    exceptions_mod.PermissionDenied = _PermissionDenied
    exceptions_mod.NotFound = _NotFound
    exceptions_mod.ResourceExhausted = _ResourceExhausted
    exceptions_mod.DeadlineExceeded = _DeadlineExceeded
    api_core_mod.exceptions = exceptions_mod

    return {
        "google": google_mod,
        "google.cloud": cloud_mod,
        "google.cloud.documentai": documentai_mod,
        "google.api_core": api_core_mod,
        "google.api_core.client_options": client_options_mod,
        "google.api_core.exceptions": exceptions_mod,
    }


def _load_document_ai_module():
    """Load `document_ai.py` under a unique module name.

    Caller must ensure `sys.modules` already contains the fake
    `google.cloud.*` entries (via `patch.dict`), because this function
    executes the module body which imports those packages at top level.
    """
    spec = importlib.util.spec_from_file_location(
        "app.services.document_ai_test_copy", MODULE_PATH
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _make_entity(type_: str, mention_text: str, confidence: float):
    entity = MagicMock()
    entity.type_ = type_
    entity.mention_text = mention_text
    entity.confidence = confidence
    entity.properties = []
    return entity


def _make_line_item(description: str, amount: str, quantity: str = "1"):
    entity = MagicMock()
    entity.type_ = "line_item"
    entity.mention_text = description
    entity.confidence = 1.0
    props = []
    for prop_type, text in (
        ("line_item/description", description),
        ("line_item/amount", amount),
        ("line_item/quantity", quantity),
    ):
        p = MagicMock()
        p.type_ = prop_type
        p.mention_text = text
        props.append(p)
    entity.properties = props
    return entity


def _make_document(entities, raw_text: str = "INVOICE TEXT"):
    doc = MagicMock()
    doc.entities = entities
    doc.text = raw_text
    return doc


def _make_client(entities, raw_text: str = "INVOICE TEXT"):
    """Mock DocumentProcessorServiceClient with the given entities."""
    client = MagicMock()
    client.processor_path.return_value = (
        "projects/p/locations/us/processors/x"
    )
    response = MagicMock()
    response.document = _make_document(entities, raw_text=raw_text)
    client.process_document.return_value = response
    return client


class DocumentAIInvoiceV2MappingTests(unittest.TestCase):
    """The invoice parser v2 ships entity types in snake_case.

    The mapping must translate those to our internal field names
    (invoice_amount, exporter_name, importer_name, ...). These tests pin
    the exact mapping we depend on so a future processor-version swap
    cannot silently empty `fields` again.
    """

    DRIFT_LOGGER = "app.services.document_ai_test_copy"

    def setUp(self):
        self.env_patch = patch.dict(
            os.environ,
            {
                "GCP_PROJECT_ID": "test-project",
                "VERTEX_AI_LOCATION": "us",
                "DOCUMENT_AI_PROCESSOR_ID": "test-processor",
            },
        )
        self.env_patch.start()
        self.addCleanup(self.env_patch.stop)

        # Scoped fake-module install. `patch.dict` restores whatever was
        # in `sys.modules` before the test (including popping keys that
        # didn't exist) on tearDown via addCleanup, so we cannot leak
        # the fakes into other test files even if they import the real
        # `google.cloud.documentai` later in the same pytest run.
        self.modules_patch = patch.dict(
            sys.modules, _build_fake_google_modules()
        )
        self.modules_patch.start()
        self.addCleanup(self.modules_patch.stop)

        self.module = _load_document_ai_module()

    def _run(self, entities, raw_text: str = "INVOICE TEXT"):
        client = _make_client(entities, raw_text=raw_text)
        with patch.object(
            self.module, "get_document_ai_client", return_value=client
        ):
            return self.module.extract_invoice_data(
                "gs://bucket/test.pdf"
            )

    def test_v2_snake_case_entities_map_to_internal_field_keys(self):
        """Common v2 entity types map to the expected internal keys."""
        entities = [
            _make_entity("invoice_id", "INV-2026-04210", 0.974),
            _make_entity("invoice_date", "April 21, 2026", 0.993),
            _make_entity("total_amount", "60,462.00", 0.973),
            _make_entity("net_amount", "58,400.00", 0.853),
            _make_entity("total_tax_amount", "0.00", 0.111),
            _make_entity("currency", "USD", 0.934),
            _make_entity(
                "supplier_name", "Exportaciones Andinas S.A.S.", 0.733),
            _make_entity("supplier_tax_id", "900.123.456-7", 0.146),
            _make_entity(
                "receiver_name", "IMPORTER OF RECORD (U.S.)", 0.271),
            _make_entity(
                "purchase_order", "PO-MIA-2026-0812", 0.354),
            _make_entity("payment_terms", "Net 30 Days", 0.962),
        ]

        result = self._run(entities)

        fields = result["fields"]
        self.assertEqual(fields["invoice_id"]["value"], "INV-2026-04210")
        self.assertEqual(fields["invoice_date"]["value"], "April 21, 2026")
        self.assertEqual(fields["invoice_amount"]["value"], "60,462.00")
        self.assertEqual(fields["net_amount"]["value"], "58,400.00")
        self.assertEqual(fields["tax_amount"]["value"], "0.00")
        self.assertEqual(fields["currency"]["value"], "USD")
        self.assertEqual(
            fields["exporter_name"]["value"],
            "Exportaciones Andinas S.A.S.",
        )
        self.assertEqual(fields["exporter_tax_id"]["value"], "900.123.456-7")
        self.assertEqual(
            fields["importer_name"]["value"], "IMPORTER OF RECORD (U.S.)"
        )
        self.assertEqual(
            fields["purchase_order"]["value"], "PO-MIA-2026-0812"
        )
        self.assertEqual(fields["payment_terms"]["value"], "Net 30 Days")
        self.assertEqual(fields["invoice_amount"]["confidence"], 0.973)

    def test_pascalcase_entities_no_longer_match(self):
        """Old v1 PascalCase types should be ignored (now snake_case only).

        This regression-locks KAN-44 — if someone re-introduces PascalCase
        keys alongside snake_case, the mapping must still require the
        entity type that today's processor actually emits.
        """
        pascalcase_entities = [
            _make_entity("InvoiceId", "INV-1", 0.9),
            _make_entity("InvoiceTotal", "1000.00", 0.9),
            _make_entity("VendorName", "ACME", 0.9),
        ]

        result = self._run(pascalcase_entities)

        self.assertEqual(result["fields"], {})

    def test_line_items_still_extract_with_snake_case_mapping(self):
        """Line items use the `line_item` type regardless of v1/v2."""
        entities = [
            _make_entity("total_amount", "100.00", 0.95),
            _make_line_item("Roses 60cm", "50.00", quantity="100"),
            _make_line_item("Tulips", "50.00", quantity="50"),
        ]

        result = self._run(entities)

        self.assertEqual(result["line_item_count"], 2)
        self.assertEqual(result["line_items"][0]["description"], "Roses 60cm")
        self.assertEqual(result["line_items"][0]["amount"], "50.00")
        self.assertEqual(result["fields"]["invoice_amount"]["value"], "100.00")

    def test_drift_warning_logged_when_no_entities_match(self):
        """If processor ships new types we should warn, not silently drop.

        This is the defensive log that would have caught KAN-44 on day 1.
        """
        drift_entities = [
            _make_entity("SomethingNew", "value-a", 0.9),
            _make_entity("AnotherUnknown", "value-b", 0.9),
        ]

        with self.assertLogs(
            logger=self.DRIFT_LOGGER, level=logging.WARNING
        ) as captured:
            result = self._run(drift_entities)

        self.assertEqual(result["fields"], {})
        drift_logs = [
            r for r in captured.records
            if "processor-version drift" in r.getMessage()
        ]
        self.assertEqual(
            len(drift_logs), 1,
            "Expected exactly one drift-warning log line",
        )
        self.assertIn("AnotherUnknown", drift_logs[0].getMessage())
        self.assertIn("SomethingNew", drift_logs[0].getMessage())

    def test_drift_warning_logged_on_partial_drift(self):
        """Even if *some* fields still map, an unknown type must warn.

        This is the scenario the previous "only warn when fields is
        empty" check missed: Document AI keeps emitting most of our
        mapped entities but renames one (e.g. `total_amount` →
        `totalAmount`). Routing then 422s on missing `invoice_amount`
        with no log to explain why. The partial-aware check surfaces
        the rename immediately.
        """
        entities = [
            _make_entity("invoice_id", "INV-1", 0.9),
            _make_entity("currency", "USD", 0.9),
            _make_entity("totalAmount", "100.00", 0.9),  # <- drift
        ]

        with self.assertLogs(
            logger=self.DRIFT_LOGGER, level=logging.WARNING
        ) as captured:
            result = self._run(entities)

        self.assertEqual(result["fields"]["invoice_id"]["value"], "INV-1")
        self.assertNotIn("invoice_amount", result["fields"])
        drift_logs = [
            r for r in captured.records
            if "processor-version drift" in r.getMessage()
        ]
        self.assertEqual(len(drift_logs), 1)
        self.assertIn("totalAmount", drift_logs[0].getMessage())

    def test_drift_warning_not_logged_on_line_item_only_document(self):
        """Line-item-only response is legitimate (e.g. receipt) — no drift."""
        line_only_entities = [
            _make_line_item("Single item", "9.99"),
        ]

        with self.assertNoLogs(
            logger=self.DRIFT_LOGGER, level=logging.WARNING
        ):
            self._run(line_only_entities)

    def test_drift_warning_not_logged_for_known_but_unmapped_entity(self):
        """Types in `_ignored_entity_types` are silent, not drift.

        `invoice_type` is emitted by v2 but has no downstream consumer,
        so we expect zero warning noise when a document only contains
        it alongside ignored types.
        """
        entities = [
            _make_entity("invoice_type", "commercial", 0.9),
            _make_line_item("Single item", "9.99"),
        ]

        with self.assertNoLogs(
            logger=self.DRIFT_LOGGER, level=logging.WARNING
        ):
            self._run(entities)

    def test_highest_confidence_wins_when_entity_type_duplicated(self):
        """Pre-existing behaviour — preserved by this refactor."""
        entities = [
            _make_entity("total_amount", "100.00", 0.5),
            _make_entity("total_amount", "200.00", 0.9),
            _make_entity("total_amount", "150.00", 0.7),
        ]

        result = self._run(entities)

        self.assertEqual(result["fields"]["invoice_amount"]["value"], "200.00")
        self.assertEqual(
            result["fields"]["invoice_amount"]["confidence"], 0.9
        )


if __name__ == "__main__":
    unittest.main()
