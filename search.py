from ddgs import DDGS


def search(query: str, max_results: int = 5) -> list[dict]:
    try:
        results = DDGS().text(
            query,
            max_results=max_results
        )

        return results

    except Exception as e:
        print(f"Search failed for '{query}': {e}")
        return []



