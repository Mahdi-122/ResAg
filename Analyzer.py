from litellm import completion
import json
import os
from dotenv import load_dotenv
from langchain_core.runnables import RunnableLambda

load_dotenv("API Key.env")

LLM_model = os.getenv("model")
OLLAMA_B = os.getenv("api_base")


ANALYZER_PROMPT = """
You are the analysis stage of an autonomous web research agent.

Your job is to analyze multiple sources and consolidate their information
before the final report is written.

The research question and the selected sources will be provided to you.

You MUST perform these tasks:

1. EVALUATE SOURCE QUALITY
   Evaluate each source based on:
   - apparent authority
   - relevance to the research question
   - whether it appears to provide substantive information
   - the type of organization behind the source when this can be
     reasonably determined from the provided title, URL, or text

   Do not invent information about the source.

2. REMOVE DUPLICATES
   If multiple sources make essentially the same claim, do not repeat
   the same finding separately.

3. MERGE RELATED INFORMATION
   Combine complementary information from different sources into a
   single finding when they discuss the same issue.

   Example:
   Source A says AI automates administrative tasks.
   Source B says entry-level administrative jobs are especially exposed.
   Source C says companies are reducing entry-level hiring.

   These should be combined into one broader finding about the effect
   of AI on entry-level administrative employment.

4. PRESERVE SOURCE ATTRIBUTION
   Every important finding must identify which sources support it.

5. IDENTIFY DISAGREEMENTS
   If credible sources make conflicting claims, do not choose one
   arbitrarily. Record the disagreement and identify the sources
   supporting each position.

6. KEEP IMPORTANT DETAILS
   Preserve important:
   - statistics
   - percentages
   - dates
   - names
   - study findings
   - numerical estimates
   - important qualifications or limitations

7. DO NOT INVENT INFORMATION
   Use ONLY information contained in the provided sources.

8. DO NOT WRITE THE FINAL REPORT
   Do not write an introduction, conclusion, essay, or 500-800 word
   summary. Your output is structured research analysis for another
   model to summarize later.

Return ONLY valid JSON.

Use EXACTLY this structure:

{
    "source_quality": [
        {
            "title": "source title",
            "url": "source URL",
            "quality": "high | medium | low",
            "reason": "short explanation"
        }
    ],
    "findings": [
        {
            "finding": "consolidated finding",
            "supporting_details": [
                "important supporting detail",
                "important supporting detail"
            ],
            "sources": [
                {
                    "title": "source title",
                    "url": "source URL"
                }
            ]
        }
    ],
    "disagreements": [
        {
            "issue": "what the sources disagree about",
            "positions": [
                {
                    "claim": "position or claim",
                    "sources": [
                        {
                            "title": "source title",
                            "url": "source URL"
                        }
                    ]
                }
            ]
        }
    ]
}

If there are no disagreements, return:

"disagreements": []

Keep findings concise but informative.
"""


def analyze_sources(question: str, sources: list[dict]) -> dict:

    user_message = f"""
Research question:

{question}

Sources to analyze:

{json.dumps(sources, indent=2, ensure_ascii=False)}

Perform the required source-quality evaluation, deduplication,
cross-source merging, and disagreement detection.

Return ONLY the required JSON.
"""

    response = completion(
        model=LLM_model,
        messages=[
            {
                "role": "system",
                "content": ANALYZER_PROMPT
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        api_base=OLLAMA_B
    )

    answer = response.choices[0].message.content


    return json.loads(answer)

from langchain_core.runnables import RunnableLambda

analyzer_chain = RunnableLambda(
    lambda x: analyze_sources(
        x["question"],
        x["all_sources"]
    )
).with_config(
    run_name="Analyzer"
)