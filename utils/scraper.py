"""
Scraping Engine - Core extraction logic
"""
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import time
import random

# User agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
]


class Scraper:
    def __init__(self):
        self.session = requests.Session()
    
    def get_random_user_agent(self):
        return random.choice(USER_AGENTS)
    
    def fetch(self, url, timeout=10):
        """Fetch HTML from URL with anti-bot measures"""
        headers = {
            'User-Agent': self.get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        try:
            # Use certifi for SSL verification in production
            import certifi
            response = self.session.get(url, headers=headers, timeout=timeout, verify=certifi.where())
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch URL: {str(e)}")
    
    def extract_text(self, soup, selector=None):
        """Extract text content from soup"""
        if selector:
            elements = soup.select(selector)
            return [el.get_text(strip=True) for el in elements]
        return soup.get_text(strip=True)
    
    def extract_links(self, soup, base_url):
        """Extract all links from page"""
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            full_url = urljoin(base_url, href)
            links.append({
                'text': a.get_text(strip=True),
                'url': full_url
            })
        return links
    
    def extract_images(self, soup, base_url):
        """Extract all images from page"""
        images = []
        for img in soup.find_all('img', src=True):
            src = img['src']
            full_url = urljoin(base_url, src)
            images.append({
                'alt': img.get('alt', ''),
                'url': full_url
            })
        return images
    
    def extract_meta(self, soup):
        """Extract meta information"""
        meta = {}
        
        # Title
        title = soup.find('title')
        meta['title'] = title.get_text(strip=True) if title else None
        
        # Description
        desc = soup.find('meta', attrs={'name': 'description'})
        meta['description'] = desc.get('content') if desc else None
        
        # Open Graph
        og_title = soup.find('meta', property='og:title')
        og_desc = soup.find('meta', property='og:description')
        og_image = soup.find('meta', property='og:image')
        
        meta['og'] = {
            'title': og_title.get('content') if og_title else None,
            'description': og_desc.get('content') if og_desc else None,
            'image': og_image.get('content') if og_image else None,
        }
        
        return meta
    
    def extract_headings(self, soup):
        """Extract heading structure"""
        headings = []
        for level in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            for h in soup.find_all(level):
                headings.append({
                    'level': level,
                    'text': h.get_text(strip=True)
                })
        return headings
    
    def extract_lists(self, soup):
        """Extract list items"""
        lists = []
        for ul in soup.find_all(['ul', 'ol']):
            items = [li.get_text(strip=True) for li in ul.find_all('li')]
            lists.append({
                'type': ul.name,
                'items': items
            })
        return lists
    
    def smart_extract(self, url, options=None):
        """
        Smart extraction - automatically detect content type and extract
        """
        options = options or {}
        
        # Fetch HTML
        html = self.fetch(url)
        soup = BeautifulSoup(html, 'lxml')
        
        # Remove unwanted elements
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            tag.decompose()
        
        result = {
            'url': url,
            'domain': urlparse(url).netloc,
            'scraped_at': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'meta': self.extract_meta(soup),
            'content': {
                'headings': self.extract_headings(soup),
                'text': self.extract_text(soup, options.get('text_selector')),
                'links': self.extract_links(soup, url) if options.get('include_links') else [],
                'images': self.extract_images(soup, url) if options.get('include_images') else [],
                'lists': self.extract_lists(soup),
            }
        }
        
        # Custom selector extraction
        if options.get('selectors'):
            result['custom'] = {}
            for name, selector in options['selectors'].items():
                elements = soup.select(selector)
                result['custom'][name] = [el.get_text(strip=True) for el in elements]
        
        return result


# Global scraper instance
scraper = Scraper()