# Automated Web Research & Summarization Agent

An automated research agent that searches the web, selects relevant sources, analyzes their content, and generates a summarized research report with citations.

## 
* Python
* Qwen 3 8B + Ollama
* LiteLLM
* LangChain
* ddgs
* Playwright
* BeautifulSoup
* Docker

## Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
playwright install chromium
```

Make sure Ollama is running with Qwen 3 8B, then run:


## Run with Docker

Pull the image:

```bash
docker pull ghcr.io/mahdi-122/research-agent:latest
```

Run it with your Ollama configuration:

```bash
docker run -it --rm --env-file ".env" ghcr.io/mahdi-122/research-agent:latest
```

The Docker image contains the application and its dependencies. Ollama and the Qwen model run separately.

## Project Structure

* `MainAg.py` — Main program
* `Planner.py` — Research planning
* `search.py` — Web search
* `SourceSelector.py` — Source selection
* `Crawler.py` — Web crawling
* `Parser.py` — Text extraction
* `Valid.py` — Source validation
* `Analyzer.py` — Source analysis
* `Summarizer.py` — Final summary
* `AgentLogger.py` — Execution logging

## Docker Image

`ghcr.io/mahdi-122/research-agent:latest`
