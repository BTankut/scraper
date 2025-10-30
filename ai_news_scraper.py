import requests
from bs4 import BeautifulSoup

def get_soup(url, headers):
    """Verilen URL'den bir BeautifulSoup nesnesi döndürür."""
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"  ! URL alınamadı: {url} - Hata: {e}")
        return None

def scrape_google_ai(soup):
    """Google AI Blog'dan makaleler çeker."""
    articles = []
    # Google'ın ana sayfasındaki makaleleri hedefleyen en kararlı seçici
    for item in soup.select('div.uni-nup__card'):
        title_element = item.select_one('h3.uni-nup__header a')
        if not title_element: # Bazen link doğrudan h3'ün içinde olmayabilir
             title_element = item.select_one('a.uni-nup__article h3.uni-nup__header')

        link_element = item.find('a', class_='uni-nup__article')

        if title_element and link_element:
            title = title_element.text.strip()
            link = link_element['href']

            if not link.startswith('http'):
                link = "https://blog.google" + link

            if not any(d.get('link') == link for d in articles):
                articles.append({'title': title, 'link': link})
    return articles

def scrape_mit_news(soup):
    """MIT News'den makaleler çeker."""
    articles = []
    for item in soup.select('article.term-page--news-article--item'):
        title_element = item.select_one('h3 a')
        if title_element:
            title = title_element.text.strip()
            link = title_element['href']
            if not link.startswith('http'):
                link = "https://news.mit.edu" + link
            if not any(d.get('link') == link for d in articles):
                articles.append({'title': title, 'link': link})
    return articles

def print_articles(all_articles):
    """Toplanan makaleleri biçimlendirilmiş bir şekilde yazdırır."""
    if not all_articles:
        print("\n\nHiçbir haber bulunamadı.")
        return

    print("\n\n--- En Son Yapay Zeka Haberleri ---")
    total_found = 0
    for source_data in all_articles:
        if source_data['articles']:
            total_found += 1
            print(f"\nKaynak: {source_data['source']}")
            print("-" * (len(source_data['source']) + 9))
            for i, article in enumerate(source_data['articles'], 1):
                print(f"  {i}. {article['title']}")
                print(f"     Bağlantı: {article['link']}")

    if total_found == 0:
         print("\n\nHiçbir haber bulunamadı.")

    print("\n---------------------------------")

def main():
    """Ana scraper fonksiyonu."""
    news_sources = {
        "Google AI Blog": {
            "url": "https://blog.google/technology/ai/",
            "scraper": scrape_google_ai
        },
        "MIT News (AI)": {
            "url": "https://news.mit.edu/topic/artificial-intelligence2",
            "scraper": scrape_mit_news
        }
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9,tr;q=0.8'
    }

    print("Yapay zeka haberleri alınıyor...")
    all_articles = []

    for source, info in news_sources.items():
        print(f"\nKaynak işleniyor: {source}")
        soup = get_soup(info['url'], headers)
        if soup:
            articles = info['scraper'](soup)
            if articles:
                print(f"  + {len(articles)} haber bulundu.")
                all_articles.append({"source": source, "articles": articles[:5]})
            else:
                print("  - Bu kaynaktan haber bulunamadı.")

    print_articles(all_articles)

if __name__ == "__main__":
    main()