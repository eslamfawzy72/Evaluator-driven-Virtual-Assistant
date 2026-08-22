"""Test-session setup: isolate the vector store from the real knowledge base.

Runs at collection time, before any test module is imported, so
rag.vector_store picks up CHROMA_PERSIST_DIR / CHROMA_COLLECTION_NAME as
module-level defaults. Without this, repeated test runs accumulate
near-duplicate content in the persisted ./chroma_db store, which
increasingly crowds out other tests' expected retrieval results.
"""
import os
import tempfile
import uuid

_test_dir = tempfile.mkdtemp(prefix="chroma_test_")
os.environ["CHROMA_PERSIST_DIR"] = _test_dir
os.environ["CHROMA_COLLECTION_NAME"] = f"test_{uuid.uuid4().hex[:8]}"
