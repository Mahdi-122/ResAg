from readability import Document
from bs4 import BeautifulSoup


def parse(html: str) -> str:
    document = Document(html)

    article_html = document.summary()

    soup = BeautifulSoup(article_html, "html.parser")

    text = soup.get_text(separator=" ", strip=True)


    return text


