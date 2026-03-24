# backend/tests/test_routing_route.py
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# ── Test loader ───────────────────────────────────────────────────────────────


def load_routing_module():
    import importlib
    import sys

    # Stub heavy dependencies before importing, scoped to this import only
    stub_modules = {}
    for mod in [
        "google.cloud.firestore",
        "google.cloud",
        "google",
    ]:
        if mod not in sys.modules:
            stub_modules[mod] = MagicMock()

    with patch.dict(sys.modules, stub_modules, clear=False):
        if "test_target_routing" in sys.modules:
            del sys.modules["test_target_routing"]

        import app.routes.routing as module
    return module


# ── Tests ─────────────────────────────────────────────────────────────────────

class RoutingRouteTests(unittest.IsolatedAsyncioTestCase):

    def _make_analyzed_transaction(self, overrides: dict | None = None) -> dict:
        """Base transaction in analyzed state with extraction fields."""
        base = {
            "status": "analyzed",
            "extraction": {
                "fields": {
                    "invoice_amount": {"value": "47500"},
                    "currency": {"value": "USD"},
                    "buyer_country": {"value": "US"},
                    "seller_country": {"value": "CO"},
                }
            },
        }
        if overrides:
            base.update(overrides)
        return base

    async def test_missing_document_returns_404(self):
        module = load_routing_module()

        with patch.object(module, "get_transaction", AsyncMock(return_value=None)):
            with self.assertRaises(module.HTTPException) as ctx:
                await module.get_routing_recommendation(
                    module.RoutingRequest(document_id="missing-doc")
                )
        self.assertEqual(ctx.exception.status_code, 404)

    async def test_unanalyzed_document_returns_422(self):
        module = load_routing_module()

        with patch.object(
            module,
            "get_transaction",
            AsyncMock(return_value={"status": "uploaded", "extraction": None}),
        ):
            with self.assertRaises(module.HTTPException) as ctx:
                await module.get_routing_recommendation(
                    module.RoutingRequest(document_id="doc-1")
                )
        self.assertEqual(ctx.exception.status_code, 422)
        self.assertIn("uploaded", ctx.exception.detail)

    async def test_processing_status_returns_422(self):
        module = load_routing_module()

        with patch.object(
            module,
            "get_transaction",
            AsyncMock(return_value={"status": "processing"}),
        ):
            with self.assertRaises(module.HTTPException) as ctx:
                await module.get_routing_recommendation(
                    module.RoutingRequest(document_id="doc-2")
                )
        self.assertEqual(ctx.exception.status_code, 422)

    async def test_success_returns_routing_result(self):
        module = load_routing_module()

        with patch.object(
            module,
            "get_transaction",
            AsyncMock(return_value=self._make_analyzed_transaction()),
        ), patch.object(
            module,
            "save_routing_result",
            AsyncMock(),
        ):
            response = await module.get_routing_recommendation(
                module.RoutingRequest(document_id="doc-3")
            )

        self.assertEqual(response["document_id"], "doc-3")
        self.assertEqual(response["status"], "routed")
        self.assertIn("routing", response)
        self.assertIn("recommended_method", response["routing"])
        self.assertTrue(response["routing_saved"])

    async def test_persistence_failure_still_returns_result(self):
        """
        If Firestore save fails, the route should still return the
        routing result with routing_saved=False rather than 500.
        """
        module = load_routing_module()

        with patch.object(
            module,
            "get_transaction",
            AsyncMock(return_value=self._make_analyzed_transaction()),
        ), patch.object(
            module,
            "save_routing_result",
            AsyncMock(side_effect=Exception("Firestore timeout")),
        ):
            response = await module.get_routing_recommendation(
                module.RoutingRequest(document_id="doc-4")
            )

        self.assertEqual(response["status"], "routed")
        self.assertFalse(response["routing_saved"])
        self.assertIn("routing", response)

    async def test_missing_extraction_fields_returns_422(self):
        """
        Document is analyzed but extraction has no usable fields.
        The routing engine should raise ValueError → 422.
        """
        module = load_routing_module()

        with patch.object(
            module,
            "get_transaction",
            AsyncMock(return_value={
                "status": "analyzed",
                "extraction": {"fields": {}},
            }),
        ), patch.object(
            module,
            "save_routing_result",
            AsyncMock(),
        ):
            with self.assertRaises(module.HTTPException) as ctx:
                await module.get_routing_recommendation(
                    module.RoutingRequest(document_id="doc-5")
                )
        self.assertEqual(ctx.exception.status_code, 422)

    async def test_compliance_checked_status_is_accepted(self):
        """
        Documents with status 'compliance_checked' should also be
        eligible for routing — compliance runs after analyze.
        """
        module = load_routing_module()

        transaction = self._make_analyzed_transaction(
            {"status": "compliance_checked"}
        )
        with patch.object(
            module,
            "get_transaction",
            AsyncMock(return_value=transaction),
        ), patch.object(
            module,
            "save_routing_result",
            AsyncMock(),
        ):
            response = await module.get_routing_recommendation(
                module.RoutingRequest(document_id="doc-6")
            )

        self.assertEqual(response["status"], "routed")

    async def test_already_routed_document_is_accepted(self):
        """
        Repeated /routing calls on already-routed documents
        should succeed — idempotent behavior.
        """
        module = load_routing_module()

        transaction = self._make_analyzed_transaction({"status": "routed"})
        with patch.object(
            module,
            "get_transaction",
            AsyncMock(return_value=transaction),
        ), patch.object(
            module,
            "save_routing_result",
            AsyncMock(),
        ):
            response = await module.get_routing_recommendation(
                module.RoutingRequest(document_id="doc-7")
            )

        self.assertEqual(response["status"], "routed")


if __name__ == "__main__":
    unittest.main()
