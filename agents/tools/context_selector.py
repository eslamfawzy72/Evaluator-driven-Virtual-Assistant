"""Context Selector tool: picks the final compact evidence set from the
reranked candidates -- balancing relevance, diversity, and a context
length budget, so the Analyst Agent gets a small, high-quality set
instead of everything the earlier stages found.
"""
from schemas.retriever_schema import Evidence

DEFAULT_MAX_CHUNKS = 6
DEFAULT_MAX_CHARS = 8000
DEFAULT_MAX_PER_SOURCE = 3  # avoid one document crowding out every other source


def select_context(
    candidates: list[Evidence],
    max_chunks: int = DEFAULT_MAX_CHUNKS,
    max_chars: int = DEFAULT_MAX_CHARS,
    max_per_source: int = DEFAULT_MAX_PER_SOURCE,
) -> list[Evidence]:
    """Assumes `candidates` is already ranked best-first (e.g. by the
    Reranker). Walks the list greedily, skipping exact-duplicate content
    and capping how many chunks come from any single source, until either
    max_chunks or max_chars is reached."""
    selected: list[Evidence] = []
    seen_content: set[str] = set()
    per_source_count: dict[str, int] = {}
    total_chars = 0

    for candidate in candidates:
        if len(selected) >= max_chunks:
            break

        normalized = candidate.content.strip()
        if not normalized or normalized in seen_content:
            continue

        if per_source_count.get(candidate.source, 0) >= max_per_source:
            continue

        if total_chars + len(normalized) > max_chars and selected:
            # Budget exceeded -- stop, but always keep at least one chunk
            # even if it alone exceeds the budget.
            continue

        selected.append(candidate)
        seen_content.add(normalized)
        per_source_count[candidate.source] = per_source_count.get(candidate.source, 0) + 1
        total_chars += len(normalized)

    return selected
