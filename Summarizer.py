from litellm import completion
import json
import os
from dotenv import load_dotenv
from langchain_core.runnables import RunnableLambda


load_dotenv("API Key.env")

LLM_model = os.getenv("model")
OLLAMA_B = os.getenv("api_base")


SUMMARIZER_PROMPT = """
You are a research report writing assistant.

You will receive:
1. A research question.
2. Structured findings extracted by an Analyzer from multiple sources.
3. The original parsed content from the crawled sources.

Your job is to produce a clear, factual research report based only
on the research material provided.

The structured findings should be used to identify the main findings
and create the key points.

The original parsed source content should be used to verify and
support the report and to preserve important information that may
not appear in the structured findings.

Requirements:

- Write a 500–800 word summary.
- Directly answer the research question.
- Combine information from multiple sources rather than describing
  each source separately.
- Do not invent facts or information.
- If sources disagree, clearly mention the disagreement.
- Keep important claims connected to their source.
- Generate the key_points primarily from the Analyzer's findings.
- Include 3–7 concise key points.

Source requirements:

- Include only sources that are present in the provided original
  parsed source content.
- NEVER invent a source.
- NEVER invent a URL.
- NEVER modify a URL.
- NEVER replace a provided URL with a homepage or another URL.
- Copy the source title exactly from the provided source.
- Copy the source URL exactly from the provided source.
- The sources list must contain the sources actually used to support
  the report.

Use Markdown formatting inside the summary field.

Return ONLY valid JSON.

Do not use Markdown outside the JSON.
Do not use ```json.
Do not write anything before or after the JSON.

Use exactly this structure:

{
    "summary": "500–800 word research summary...",
    "key_points": [
        "key point 1",
        "key point 2",
        "key point 3"
    ],
    "sources": [
        {
            "title": "source title",
            "url": "source URL"
        }
    ]
}
"""


def summarize_research(
    question: str,
    all_sources: list[dict],
    findings: dict
) -> dict:

    user_message = f"""
Research question:

{question}

Structured research findings from the Analyzer:

{json.dumps(findings, indent=2, ensure_ascii=False)}

Original parsed source content:

{json.dumps(all_sources, indent=2, ensure_ascii=False)}

Create the final research report.

Use the structured findings to identify the key points.

Use the parsed source content to ensure that the final report is
grounded in the actual crawled sources and to preserve important
information that may not appear in the structured findings.

For the sources list, use the sources that were actually used in
the report. Use their exact titles and URLs from the original
parsed source content.
"""

    response = completion(
        model=LLM_model,
        messages=[
            {
                "role": "system",
                "content": SUMMARIZER_PROMPT
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

    print("\n========== RAW SUMMARIZER OUTPUT ==========")
    print(repr(answer))
    print("===========================================")

    result = json.loads(answer)

    # ---------------------------------------------------------
    # Fix source metadata using the original all_sources data.
    # The LLM is NOT responsible for access_date.
    # ---------------------------------------------------------

    corrected_sources = []

    for source in result.get("sources", []):

        source_url = source.get("url", "").strip()
        source_title = source.get("title", "").strip()

        matched_source = None

        # First: match using the URL
        for original in all_sources:
            original_url = original.get("url", "").strip()

            if source_url and source_url == original_url:
                matched_source = original
                break

        # Second: if URL did not match, try the title
        if matched_source is None and source_title:
            for original in all_sources:
                original_title = original.get("title", "").strip()

                if source_title == original_title:
                    matched_source = original
                    break

        # Only include sources that actually exist in all_sources
        if matched_source is not None:
            corrected_sources.append({
                "title": matched_source["title"],
                "url": matched_source["url"],
                "access_date": matched_source["access_date"]
            })

    result["sources"] = corrected_sources

    return result


summarizer_chain = RunnableLambda(
    lambda x: summarize_research(
        x["question"],
        x["all_sources"],
        x["findings"]
    )
).with_config(
    run_name="Summarizer"
)


