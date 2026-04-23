import requests
from bs4 import BeautifulSoup


def get_real_url(google_url):
    try:
        response = requests.get(google_url, allow_redirects=True, timeout=10)
        return response.url  # final redirected URL
    except Exception as e:
        print(f"Error resolving URL: {e}")
        return None


def fetch_article_content(url):
    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        paragraphs = soup.find_all("p")

        content = " ".join([p.get_text() for p in paragraphs])

        return content.strip()

    except Exception as e:
        print(f"Error fetching article: {e}")
        return None


if __name__ == "__main__":
    google_url = "https://www.usthadian.com/first-cbi-prosecuted-wildlife-crime-case-in-india/"

    real_url = get_real_url(google_url)
    print("Real URL:", real_url)

    if real_url:
        content = fetch_article_content(real_url)

        if content:
            print("\nContent Preview:\n")
            print(content[:1000])
        else:
            print("Failed to fetch content")