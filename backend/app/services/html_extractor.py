from bs4 import BeautifulSoup

def extract_text_from_html(html_bytes: bytes) -> dict:
    soup = BeautifulSoup(html_bytes, "html.parser")

    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    title = soup.title.string if soup.title else None

    return {
        "pages": [{
            "page_number": 1,
            "text": text,
            "meta": {"title": title}
        }],
        "meta": {}
    }
