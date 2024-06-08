import aiohttp
import asyncio
from bs4 import BeautifulSoup
import multiprocessing
import time
import sys

# Ustawienie kodowania na UTF-8
sys.stdout.reconfigure(encoding='utf-8')

async def fetch_content(session, url, profile):
    async with session.get(url) as response:
        if response.status == 200:
            start_time = time.time()
            text = await response.text()
            soup = BeautifulSoup(text, 'html.parser')

            result = {"url": url}
            
            if profile.get('headers'):
                headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                result['headers'] = [header.text.strip() for header in headers]
            
            if profile.get('links'):
                links = soup.find_all('a', href=True)
                result['links'] = [link['href'] for link in links]
            
            if profile.get('paragraphs'):
                paragraphs = soup.find_all('p')
                result['paragraphs'] = [paragraph.text.strip() for paragraph in paragraphs]
            
            if profile.get('addresses'):
                addresses = []
                address_tags = soup.find_all('address')
                for address_tag in address_tags:
                    addresses.append(address_tag.get_text(strip=True))

                address_classes = ['contact-address', 'address', 'company-address', 'office-address']
                for class_name in address_classes:
                    elements = soup.find_all(class_=class_name)
                    for element in elements:
                        addresses.append(element.get_text(strip=True))

                result['addresses'] = addresses

            end_time = time.time()
            execution_time = end_time - start_time
            print(f"Czas wykonania dla {url}: {execution_time} sekund\n")

            return result, execution_time
        else:
            return None, None

async def fetch_all(urls, profile):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_content(session, url, profile) for url in urls]
        return await asyncio.gather(*tasks)

def run_async_scraper(urls, profile):
    return asyncio.run(fetch_all(urls, profile))

def main():
    urls = [
        'https://example.com',
        'https://example.org',
        'https://example.net'
    ]
    profile = {
        "headers": True,
        "links": True,
        "paragraphs": True,
        "addresses": True
    }
    
    pool = multiprocessing.Pool()
    results = pool.starmap(run_async_scraper, [(urls, profile)])
    pool.close()
    pool.join()

    for result_set in results:
        for result, _ in result_set:
            if result:
                print(result)
                print()  # Dodaj pustą linię między wynikami
    
    total_execution_time = sum(execution_time for result_set in results for _, execution_time in result_set if execution_time is not None)
    print(f"Całkowity czas wykonania: {total_execution_time} sekund")

if __name__ == '__main__':
    main()
