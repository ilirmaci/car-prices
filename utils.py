import re
import time
import urllib.request as request
import bs4
from bs4 import BeautifulSoup

def url(maker: str, model: str, zip: str="1019-amsterdam", page: int|None=None, max_price: int|None=None, max_km: int|None=None) -> str:
    """Return formatted url for autoscout24.nl"""
    result = f"https://www.autoscout24.nl/lst/{maker}/{model}/1019-amsterdam?"

    if page:
        result += f"&page={page}"
    if max_price:
        result += f"&priceto={max_price}"
    if max_km:
        result += f"&kmto={max_km}"
    return result

def get_html(url: str) -> str:
    """Return HTML code of `url`"""
    connection = request.urlopen(url)
    result = connection.read().decode()
    connection.close()
    return result

def get_count_pages(html: str) -> int:
    """Return number of pages in search results"""
    patt = re.compile("(?<=Ga naar pagina )[0-9]{1,3}")
    matches = re.findall(patt, html)
    if len(matches) == 0:
        return 1
    return int(matches[-1])

def search_car(maker: str, model: str, delay: int=10, **kwargs) -> list[str]:
    """Return list of HTML of all pages for a car. `delay` sets time to wait before url calls.
    `*kwargs` are passed to `get_html`"""
    page1 = get_html(url(maker, model, **kwargs))
    num_pages = get_count_pages(page1)
    result = [page1]
    if num_pages < 2:
        return result

    for page in range(2, num_pages + 1):
        time.sleep(delay)
        next_page = get_html(url(maker, model, page=page))
        result.append(next_page)
    return result

def listings(html: str) -> list[bs4.element.Tag]:
    """Return list of parsed car listings from `html` of results page"""
    parsed = BeautifulSoup(html, features="lxml")
    return parsed.find_all("article")

def parse_data(listing: bs4.element.Tag) -> dict:
    """Return structured car data record from parsed `listing`"""
    id2col = {
        "data-price": "price",
        "id": "id",
        "data-fuel-type": "fuel_type",
        "data-model": "model",
        "data-mileage": "mileage",
        "data-first-registration": "registration",
        "data-listing-country": "country",
        "data-listing-zip-code": "zip",
    }
    span2col = {"transmission": "transmission", "speedometer": "power"}
    id_features = {v: listing[k] for k, v in id2col.items()}
    span_values = listing.find_all("span")
    
    def find_value(elements: list[bs4.element.Tag], pattern: str) -> str:
        try:
            return [_.text for _ in elements if pattern in str(_)][0]
        except IndexError as err:
            elements_str = '\n'.join([str(_) for _ in elements])
            raise IndexError(f"could not find {pattern} in {elements_str}") from err

    span_features = {v: find_value(span_values, k) for k, v in span2col.items()}
    listing_url = listing.find_all("a")[0]["href"]
    return id_features | span_features | {"post_url": listing_url}

def extract(pages: list[str]) -> list[dict]:
    """Return car listings as structured data records from all entries in `pages`"""
    return [parse_data(listing) for page in pages for listing in listings(page)]
