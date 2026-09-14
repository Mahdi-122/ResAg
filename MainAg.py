import json
from Planner import create_plan, planner_chain
from search import search
from Crawler import crawl
from Parser import parse
from SourceSelector import select_sources
from Valid import is_valid_source
from Analyzer import analyze_sources, analyzer_chain
from Summarizer import summarize_research, summarizer_chain
from datetime import date
from AgentLogger import AgentLogger


if __name__ == "__main__":

    question = input("Enter your research question/topic: ")

    # log
    logger = AgentLogger()


    # -------------------------
    # Planning
    # -------------------------

    print("planning ... pls wait")

    plan = planner_chain.invoke(
        question,
        config={
            "callbacks": [logger]
        }
    )

    print("\nResearch Plan:")
    print(json.dumps(plan, indent=4, ensure_ascii=False))


    # -------------------------
    # Search
    # -------------------------

    print("searching ... pls wait")

    search_results = []

    for query in plan["search_queries"]:

        print("\nSEARCHING:", repr(query))

        try:
            results = search(query, max_results=5)

            print("FOUND:", len(results))
            print(results)

            search_results.extend(results)

        except Exception as e:
            print("SEARCH ERROR:", e)

    print("\nSearch results found:", len(search_results))


    # -------------------------
    # Select best search results
    # -------------------------

    print("selecting best search results pls wait ...")

    selected = select_sources(plan, search_results)

    with open("ranker.txt", "w", encoding="utf-8") as file:

        file.write("RANKER / SOURCE SELECTION\n")
        file.write("=" * 70)
        file.write("\n\n")
        file.write(str(selected))


    print("\nSelected Sources:")
    print(json.dumps(selected, indent=4, ensure_ascii=False))


    # -------------------------
    # Crawl selected sources
    # -------------------------

    print("Crawling ... pls wait")

    all_sources = []

    print("\nStarting crawl of selected sources...")

    for source in selected["selected_sources"]:

        print("\nSOURCE OBJECT:")
        print(source)

        url = source["url"]

        print(f"URL TO CRAWL: {url}")

        try:

            html = crawl(url)

            print("Crawl successful.")

            text = parse(html)

            print(f"Parsed text length: {len(text)} characters")

            if not is_valid_source(text):

                print(f"Skipping invalid source: {url}")
                continue

            all_sources.append({
                "title": source["title"],
                "url": url,
                "reason": source.get("reason", ""),
                "text": text,
                "access_date": date.today().isoformat()
            })

            print("Successfully processed.")

        except Exception as e:

            print(f"Failed to process {url}: {e}")


    print("\nSuccessfully processed sources:", len(all_sources))

    with open("Extracted Content.txt", "w", encoding="utf-8") as file:
        file.write(str(all_sources))


    # -------------------------
    # Analyze sources
    # -------------------------

    print("analyzing ... pls wait")

    if not all_sources:
        print("No usable sources were found.")
        exit()


    findings = analyzer_chain.invoke(
        {
            "question": question,
            "all_sources": all_sources
        },
        config={
            "callbacks": [logger]
        }
    )


    print("\nResearch Findings:")
    print(json.dumps(findings, indent=4, ensure_ascii=False))

    with open("analyze.txt", "w", encoding="utf-8") as file:
        file.write(str(findings))


    # -------------------------
    # Summarize research
    # -------------------------

    print("summarizing ... pls wait")

    report = summarizer_chain.invoke(
        {
            "question": question,
            "all_sources": all_sources,
            "findings": findings
        },
        config={"callbacks": [logger]}
    )


    # Add ranker reasons to final report sources
    for report_source in report.get("sources", []):

        report_url = report_source.get("url", "").strip()
        report_title = report_source.get("title", "").strip()

        for original_source in all_sources:

            if (
                report_url == original_source["url"]
                or report_title == original_source["title"]
            ):
                report_source["reason"] = original_source["reason"]
                break


    print("\nFinal Report:")
    print(json.dumps(report, indent=4, ensure_ascii=False))


    # -------------------------
    # Save final report + AI chain trace
    # -------------------------

    with open("summary.txt", "w", encoding="utf-8") as file:

        # Final report
        file.write(str(report))

        # Access dates
        file.write("\n\n")
        file.write("=" * 70)
        file.write("\nACCESS DATES\n")
        file.write("=" * 70)
        file.write("\n\n")

        for source in all_sources:
            file.write(f"Title: {source['title']}\n")
            file.write(f"URL: {source['url']}\n")
            file.write(f"Access date: {source['access_date']}\n\n")

        # AI chain trace
        file.write("\n")
        file.write("=" * 70)
        file.write("\nCHAIN OF THOUGHT / AGENT TRACE\n")
        file.write("=" * 70)
        file.write("\n\n")

        # Step 1 - Planner
        step = logger.steps[0]

        file.write("STEP 1: Planner\n")
        file.write("-" * 70)

        file.write("\nINPUT:\n")
        file.write(str(step["input"]))

        file.write("\n\nOUTPUT:\n")
        file.write(str(step["output"]))
        file.write("\n\n")


        # Step 2 - Source Selector / Ranker
        file.write("STEP 2: Source Selector / Ranker\n")
        file.write("-" * 70)

        file.write("\nOUTPUT:\n")
        file.write(str(selected))
        file.write("\n\n")


        # Steps 3+ - Analyzer and Summarizer
        for i, step in enumerate(logger.steps[1:], 3):

            file.write(f"STEP {i}: {step['name']}\n")
            file.write("-" * 70)

            if step["name"] not in ["Analyzer", "Summarizer"]:
                file.write("\nINPUT:\n")
                file.write(str(step["input"]))

            file.write("\n\nOUTPUT:\n")
            file.write(str(step["output"]))
            file.write("\n\n")