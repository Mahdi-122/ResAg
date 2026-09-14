from litellm import completion
import json
import os
from dotenv import load_dotenv


print("USING SOURCE SELECTOR FILE")

load_dotenv("API Key.env")
LLM_model = os.getenv("model")
OLLAMA_B = os.getenv("api_base")


SOURCE_SELECTOR_PROMPT = """
You are a research source selection assistant.

You will receive:
1. A research plan created earlier.
2. A list of search results found for that research plan.

Your job is to select the best sources to crawl and use for the research.

Use the research plan's preferred_sources as an important criterion.

Consider:
- relevance to the research topic
- how well the source matches the preferred source types
- apparent authority of the source
- usefulness of the title and search snippet
- whether the source appears to contain substantive information

Do NOT crawl or invent information about the webpages.
You only have the title, URL, and search snippet.

Select at most the requested max_sources.

For EVERY selected source:
- You MUST provide a non-empty "reason".
- The reason must explain WHY this source was selected.
- The reason must be based only on the research plan, title, URL, and search snippet.
- Mention the specific strengths that made the source preferable, such as relevance, authority, preferred source type, or useful information indicated by the snippet.
- Do not give generic reasons such as "This is a good source."

Return ONLY valid JSON.

IMPORTANT:
- Do not use Markdown.
- Do not use headings.
- Do not explain your answer outside the JSON.
- Do not write any text before or after the JSON.
- Your entire response must be one JSON object.
- Use exactly this structure:


{
    "selected_sources": [
        {
            "title": "source title",
            "url": "source URL",
            "reason": "short explanation for selecting this source"
        }
    ]
}

The first character of your response must be {.
The last character of your response must be }."""


def select_sources(plan: dict, search_results: list[dict]) -> dict:

    candidates = []

    for result in search_results:
        candidates.append({
            "title": result.get("title", ""),
            "url": result.get("href", ""),
            "snippet": result.get("body", "")
        })

    user_message = f"""
Research plan:

{json.dumps(plan, indent=2, ensure_ascii=False)}

Candidate search results:

{json.dumps(candidates, indent=2, ensure_ascii=False)}

Select the best sources according to the research plan.
Return no more than {plan["max_sources"]} sources.
"""

    response = completion(
        model=LLM_model,
        messages=[
            {
                "role": "system",
                "content": SOURCE_SELECTOR_PROMPT
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        api_base=OLLAMA_B,
        response_format={"type": "json_object"}
    )

    answer = response.choices[0].message.content



    try:
        return json.loads(answer)
    except json.JSONDecodeError:
        print("\nSOURCE SELECTOR DID NOT RETURN VALID JSON.")
        print("Raw output:")
        print(answer)
        raise