def clean_results(results):
    cleaned = []
    seen = set()

    for result in results:
        title = result["title"].strip()

        if title.lower() not in seen:
            seen.add(title.lower())
            cleaned.append(result)

    return cleaned