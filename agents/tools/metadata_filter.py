"""Metadata Filter tool: turns a simple flat filter dict into the `where`
clause shape Chroma expects, so callers never need to know Chroma's syntax.

Example:
    build_where_clause({"source": "paper.pdf"})
    -> {"source": "paper.pdf"}

    build_where_clause({"source": "paper.pdf", "chapter": 4})
    -> {"$and": [{"source": "paper.pdf"}, {"chapter": 4}]}
"""
from typing import Optional


def build_where_clause(metadata_filter: Optional[dict]) -> Optional[dict]:
    """Convert a flat {field: value} dict into Chroma's `where` format.

    Chroma requires a single top-level operator when there's more than one
    condition -- a plain {"a": 1, "b": 2} dict is rejected. This wraps
    multi-key filters in "$and" automatically so callers can just pass a
    normal dict.
    """
    if not metadata_filter:
        return None

    if len(metadata_filter) == 1:
        key, value = next(iter(metadata_filter.items()))
        return {key: value}

    return {"$and": [{key: value} for key, value in metadata_filter.items()]}
