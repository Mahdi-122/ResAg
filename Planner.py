from litellm import completion
import json
import os
from dotenv import load_dotenv
from langchain_core.runnables import RunnableLambda



load_dotenv("API Key.env")
LLM_model = os.getenv("model")
OLLAMA_B = os.getenv("api_base")



PLANNER_PROMPT = """
You are a research planning assistant.

The user will give you a research question.
Your job is to create a plan for researching that question on the web.

Return ONLY valid JSON with this structure:

{
    "topic": "the research topic",
    "search_queries": [
        "search query 1",
        "search query 2",
        "search query 3",
        "search query 4"
    ],
    "preferred_sources": [
        "type of source 1",
        "type of source 2",
        "type of source 3"
    ],
    "max_sources": 8
}

Create search queries that approach the topic from different angles.
Prefer reliable sources such as academic papers, government reports,
universities, and reputable research organizations.
"""



def create_plan(question: str) -> dict:
    response = completion(
        model=LLM_model ,
        messages=[
            {
                "role": "system",
                "content": PLANNER_PROMPT
            },
            {
                "role": "user",
                "content": question
            }
        ],
        api_base=OLLAMA_B
    )

    answer = response.choices[0].message.content

    return json.loads(answer)


planner_chain = RunnableLambda(create_plan).with_config(
    run_name="Planner"
)