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
                await module.create_routing_recommendation(
                    module.RoutingRequest(document_id="missing-doc"),
                    current_user={"uid": "test-user-1"},
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
                await module.create_routing_recommendation(
                    module.RoutingRequest(document_id="doc-1"),
                    current_user={"uid": "test-user-1"},
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
                await module.create_routing_recommendation(
                    module.RoutingRequest(document_id="doc-2"),
                    current_user={"uid": "test-user-1"},
                )
        self.assertEqual(ctx.exception.status_code, 422)

    async def test_success_returns_routing_result(self):
        module = load_routing_module()

        with patch.object(
            module,
            "get_transaction",
            AsyncMock(return_value=self._make_analyzed_transaction()),
        ) as get_transaction, patch.object(
            module,
            "save_routing_result",
            AsyncMock(),
        ) as save_routing_result:
            response = await module.create_routing_recommendation(
                module.RoutingRequest(document_id="doc-3"),
                current_user={"uid": "test-user-1"},
            )

        self.assertEqual(response["document_id"], "doc-3")
        self.assertEqual(response["status"], "routed")
        self.assertIn("routing", response)
        self.assertIn("recommended_method", response["routing"])
        self.assertTrue(response["routing_saved"])
        # Read-side isolation: the initial get_transaction lookup must
        # carry user_id so the Firestore read is path-scoped to the
        # authenticated user (post-KAN-16 subcollection layout).
        get_transaction.assert_awaited_once_with("doc-3", user_id="test-user-1")
        self.assertEqual(
            get_transaction.call_args.kwargs["user_id"], "test-user-1"
        )
        # Explicit propagation assertion — user_id must reach save_routing_result
        self.assertEqual(
            save_routing_result.call_args.kwargs["user_id"], "test-user-1"
        )

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
            response = await module.create_routing_recommendation(
                module.RoutingRequest(document_id="doc-4"),
                current_user={"uid": "test-user-1"},
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
                await module.create_routing_recommendation(
                    module.RoutingRequest(document_id="doc-5"),
                    current_user={"uid": "test-user-1"},
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
            response = await module.create_routing_recommendation(
                module.RoutingRequest(document_id="doc-6"),
                current_user={"uid": "test-user-1"},
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
            response = await module.create_routing_recommendation(
                module.RoutingRequest(document_id="doc-7"),
                current_user={"uid": "test-user-1"},
            )

        self.assertEqual(response["status"], "routed")

    # ── KAN-46: required-field contract tests ─────────────────────────────────

    async def test_routing_returns_422_with_missing_fields_detail_when_amount_missing(self):
        """Preflight 422 when extraction produced no amount.

        The route checks for a missing amount BEFORE calling the routing
        engine, so the error response includes a `missing_fields` list in
        the detail body — giving the caller an actionable diagnosis rather
        than a generic 'Could not generate routing recommendation' message.
        """
        module = load_routing_module()

        transaction = {
            "status": "analyzed",
            "extraction": {
                "fields": {
                    # currency and country codes present — only amount missing
                    "currency": {"value": "USD"},
                    "buyer_country": {"value": "US"},
                    "seller_country": {"value": "CO"},
                }
            },
        }

        with patch.object(
            module,
            "get_transaction",
            AsyncMock(return_value=transaction),
        ), patch.object(
            module,
            "save_routing_result",
            AsyncMock(),
        ):
            with self.assertRaises(module.HTTPException) as ctx:
                await module.create_routing_recommendation(
                    module.RoutingRequest(document_id="doc-8"),
                    current_user={"uid": "test-user-1"},
                )

        exc = ctx.exception
        self.assertEqual(exc.status_code, 422)
        # detail must be a dict with a missing_fields key
        self.assertIsInstance(exc.detail, dict)
        self.assertIn("missing_fields", exc.detail)
        self.assertIn("amount", exc.detail["missing_fields"])

    async def test_routing_succeeds_when_amount_present_country_codes_missing(self):
        """Routing succeeds with US/US defaults when country codes are absent.

        buyer_country and seller_country default to 'US' with a warning
        (per _normalize_extraction in payment_routing.py). The route must
        NOT 422 just because country codes are missing — only a missing
        amount is a hard error at the preflight stage.
        """
        module = load_routing_module()

        transaction = {
            "status": "analyzed",
            "extraction": {
                "fields": {
                    # amount present; country codes intentionally omitted
                    "invoice_amount": {"value": "12500"},
                    "currency": {"value": "USD"},
                }
            },
        }

        with patch.object(
            module,
            "get_transaction",
            AsyncMock(return_value=transaction),
        ), patch.object(
            module,
            "save_routing_result",
            AsyncMock(),
        ):
            response = await module.create_routing_recommendation(
                module.RoutingRequest(document_id="doc-9"),
                current_user={"uid": "test-user-1"},
            )

        self.assertEqual(response["status"], "routed")
        self.assertIn("routing", response)

    async def test_routing_returns_422_with_missing_fields_detail_when_amount_is_blank_string(self):
        """
        If the stored extraction has invoice_amount: "" or "   " (blank/whitespace),
        the preflight should catch it before reaching the threadpool and return 422
        with detail {"missing_fields": ["amount"], ...} rather than the generic
        'Could not generate routing recommendation' message from _safe_decimal.
        """
        module = load_routing_module()

        for blank_value in ("", "   "):
            with self.subTest(invoice_amount=repr(blank_value)):
                transaction = {
                    "status": "analyzed",
                    "extraction": {
                        "fields": {
                            "invoice_amount": {"value": blank_value},
                            "currency": {"value": "USD"},
                            "buyer_country": {"value": "US"},
                            "seller_country": {"value": "CO"},
                        }
                    },
                }
                with patch.object(
                    module,
                    "get_transaction",
                    AsyncMock(return_value=transaction),
                ), patch.object(
                    module,
                    "save_routing_result",
                    AsyncMock(),
                ):
                    with self.assertRaises(module.HTTPException) as ctx:
                        await module.create_routing_recommendation(
                            module.RoutingRequest(document_id="doc-8"),
                            current_user={"uid": "test-user-1"},
                        )

                self.assertEqual(ctx.exception.status_code, 422)
                detail = ctx.exception.detail
                # Must be the structured preflight response, not the generic
                # 'Could not generate routing recommendation' string
                self.assertIsInstance(detail, dict, msg=(
                    f"Expected dict detail from preflight, got {type(detail).__name__}: {detail!r}"
                ))
                self.assertIn("missing_fields", detail)
                self.assertIn("amount", detail["missing_fields"])


if __name__ == "__main__":
    unittest.main()
