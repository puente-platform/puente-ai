"""
Idempotent Firestore migration script — KAN-16 tenant path scoping.

Migrates documents from the old flat-path layout:

    transactions/{doc_id}

to the new per-user subcollection layout:

    transactions/_dev_owner/docs/{doc_id}

All migrated documents receive an added field ``user_id: "_dev_owner"``.

Usage
-----
Dry run (no mutations — lists what *would* be moved):

    python scripts/migrate_firestore_tenant_scoping.py --dry-run

Real run (copy + verify + delete):

    python scripts/migrate_firestore_tenant_scoping.py

The script is idempotent: a second real run finds 0 orphan docs under the
old flat path and exits cleanly with code 0.

Orphan definition
-----------------
A document is considered an orphan (pre-KAN-16 layout) if it exists directly
under ``transactions/{doc_id}`` where ``doc_id`` is NOT a user-id-style
segment (i.e., the document has no sub-collection named ``docs``).

In practice, since the pre-KAN-16 schema used ``doc_id`` values that look like
UUIDs (e.g. ``a1b2c3d4-…``), we simply list *all* direct documents in the
``transactions`` collection that are not ``_dev_owner`` (the sentinel user_id
created by this script).

Batched writes
--------------
Firestore batched commits are limited to 500 operations.  This script uses
batches of up to 500 ops to remain safe when run against larger datasets
(e.g. staging).  Each batch includes: one SET (copy) and one DELETE — so at
most 250 documents can be processed per batch.  The script commits each batch
before starting the next one.

Environment
-----------
GCP_PROJECT_ID  — required; Firestore project ID.

Exit codes
----------
0  — success (including 0 orphans found)
1  — one or more copy-verification failures
"""

import argparse
import logging
import os
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# Maximum Firestore batch size (platform limit: 500 ops per commit).
# Each migrated document costs 2 ops (set + delete), so cap at 250 docs/batch.
_MAX_OPS_PER_BATCH = 500
_MAX_DOCS_PER_BATCH = _MAX_OPS_PER_BATCH // 2

_DEV_OWNER_ID = "_dev_owner"


def _get_firestore_client():
    """
    Return the module-level singleton Firestore client from app.services.firestore.

    Importing from the service module ensures we reuse the same initialized
    client and pick up any future credential changes in one place.
    """
    # Import lazily so the script fails fast if GCP_PROJECT_ID is missing.
    from app.services.firestore import get_firestore_client  # noqa: PLC0415
    return get_firestore_client()


def _list_orphan_docs(db) -> list:
    """
    Return all direct documents under ``transactions/`` that are candidates
    for migration (i.e., not the sentinel ``_dev_owner`` document itself).

    An orphan is any document whose ID does not look like a user-id sentinel.
    Since the new schema writes to ``transactions/{user_id}`` (where user_id is
    a Firebase UID or ``_dev_owner``), and the old schema wrote to
    ``transactions/{uuid-style-doc_id}``, the simplest safe heuristic is:
    list all docs in ``transactions/`` and skip ``_dev_owner``.
    """
    orphans = []
    for snap in db.collection("transactions").list_documents():
        doc_id = snap.id
        if doc_id == _DEV_OWNER_ID:
            # This is the new-schema user container — skip.
            continue
        doc_snap = snap.get()
        if not doc_snap.exists:
            # Document reference exists (e.g. as subcollection parent) but has
            # no data — not a pre-KAN-16 flat record, skip.
            continue
        orphans.append((doc_id, doc_snap.to_dict()))
    return orphans


def _migrate(dry_run: bool) -> int:
    """
    Core migration logic.

    Returns the number of copy-verification failures.  Callers should
    ``sys.exit(failures)`` so the process exits non-zero on any failure.
    """
    db = _get_firestore_client()

    orphans = _list_orphan_docs(db)
    logger.info("Found %d orphan document(s) to migrate.", len(orphans))

    if not orphans:
        logger.info("Nothing to do — already migrated or no pre-KAN-16 data.")
        return 0

    if dry_run:
        for doc_id, data in orphans:
            logger.info(
                "[DRY-RUN] Would migrate: transactions/%s → "
                "transactions/%s/docs/%s  (fields: %s)",
                doc_id,
                _DEV_OWNER_ID,
                doc_id,
                list(data.keys()),
            )
        return 0

    # --- Real run: copy → verify → delete in batches ---
    failures = 0  # global — counted across all batches, returned for exit code
    batch_start = 0

    while batch_start < len(orphans):
        batch_docs = orphans[batch_start: batch_start + _MAX_DOCS_PER_BATCH]
        batch = db.batch()

        for doc_id, data in batch_docs:
            dest_ref = (
                db.collection("transactions")
                .document(_DEV_OWNER_ID)
                .collection("docs")
                .document(doc_id)
            )
            migrated_data = {**data, "user_id": _DEV_OWNER_ID}
            batch.set(dest_ref, migrated_data)

        logger.info(
            "Committing copy batch (%d docs, batch_start=%d) …",
            len(batch_docs),
            batch_start,
        )
        batch.commit()

        # --- Verify copies then delete originals ---
        # Scope the delete-gate to THIS batch's failures. A failure in an
        # earlier batch must not cascade into skipping deletes for later
        # successful batches (that was the pre-fix bug CodeRabbit flagged).
        batch_failures = 0
        delete_batch = db.batch()
        for doc_id, _ in batch_docs:
            dest_ref = (
                db.collection("transactions")
                .document(_DEV_OWNER_ID)
                .collection("docs")
                .document(doc_id)
            )
            dest_snap = dest_ref.get()
            if not dest_snap.exists:
                logger.error(
                    "VERIFY FAILED: transactions/%s/docs/%s not found after copy.",
                    _DEV_OWNER_ID,
                    doc_id,
                )
                failures += 1
                batch_failures += 1
                continue  # Do NOT delete the original — preserve data.

            src_ref = db.collection("transactions").document(doc_id)
            delete_batch.delete(src_ref)
            logger.info(
                "Verified copy OK — queued delete of transactions/%s",
                doc_id,
            )

        if batch_failures == 0:
            logger.info(
                "Committing delete batch (%d docs) …", len(batch_docs)
            )
            delete_batch.commit()
        else:
            logger.warning(
                "Skipping delete batch — %d verification failure(s) in this batch.",
                batch_failures,
            )

        batch_start += _MAX_DOCS_PER_BATCH

    if failures:
        logger.error(
            "%d copy-verification failure(s). Original documents preserved. "
            "Re-run after investigating.",
            failures,
        )
    else:
        logger.info("Migration complete. All documents moved to new paths.")

    return failures


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Migrate pre-KAN-16 flat Firestore docs to tenant-scoped paths."
        )
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List what would be migrated without making any changes.",
    )
    args = parser.parse_args()

    project_id = os.getenv("GCP_PROJECT_ID")
    if not project_id:
        logger.error("GCP_PROJECT_ID environment variable is not set.")
        sys.exit(1)

    logger.info(
        "Starting migration (project=%s, dry_run=%s)",
        project_id,
        args.dry_run,
    )

    failures = _migrate(dry_run=args.dry_run)
    sys.exit(failures)


if __name__ == "__main__":
    main()
