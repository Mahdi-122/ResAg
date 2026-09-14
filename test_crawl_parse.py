from Crawler import crawl
from Parser import parse
from Planner import create_plan
from Analyzer import analyze_sources
from search import search
from SourceSelector import select_sources


def test_crawler_parser(url):
    p = crawl(url)
    print("crawl successful : ", p)

    parsed = parse(p)
    print(parsed)
    return parsed



def test_planner(q):
    plan = create_plan(q)
    print(plan)
    return plan


def test_search(q):
    plan = create_plan(q)
    placeholder = []
    for _ in plan["search_queries"]:
        s = search(_, 5)
        placeholder.extend(s)

    print(placeholder)

def test_ranker(q):
    plan = create_plan(q)
    placeholder = []
    for _ in plan["search_queries"]:
        s = search(_, 5)
        placeholder.extend(s)
    Ranked = select_sources(plan, placeholder)
    print("selected sources", Ranked)


if __name__ == "__main__":
    while True :
        operate = input("1-for planner \n"
                        "2-for crawler&parser\n"
                        "3-for search engine (requires planner)\n"
                        "4-Ranker (requires the previous parts\n"
                        "Enter 5 to exit \n"
                        "enter:")
        try :
            operate = int(operate)
        except Exception as e :
            print(e)

        if operate == 1 :

            q = input("Enter your research subject :")

            tp = test_planner(q)

        elif operate == 2 :
            q = input("url for crawler&Parser :")
            cpt = test_crawler_parser(q)
        elif operate == 3 :
            q = input("Enter your research subject :")
            st = test_search(q)
        elif operate == 4 :
            q = input("Enter your research subject :")
            print("on it")
            rt = test_ranker(q)
        elif operate == 5 :
            print("bye!")
            break
