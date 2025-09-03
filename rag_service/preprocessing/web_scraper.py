"""
Web scraper module for PharmaRAG service.
Handles scraping pharmaceutical information from websites.
"""

import os
import re
import time
import logging
import requests
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import markdown

logger = logging.getLogger(__name__)

# Default headers to mimic a browser
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}


class WebScraper:
    """
    Web scraper for pharmaceutical information.
    """
    
    def __init__(self, headers: Optional[Dict[str, str]] = None, delay: float = 1.0):
        """
        Initialize the web scraper.
        
        Args:
            headers: Custom headers for requests
            delay: Delay between requests in seconds
        """
        self.headers = headers or DEFAULT_HEADERS
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_page_content(self, url: str) -> Optional[str]:
        """
        Get the HTML content of a webpage.
        
        Args:
            url: URL to scrape
            
        Returns:
            HTML content or None if failed
        """
        try:
            logger.info(f"Scraping URL: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Add delay to be respectful
            time.sleep(self.delay)
            
            return response.text
            
        except requests.RequestException as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {str(e)}")
            return None
    
    def extract_text_from_html(self, html_content: str) -> str:
        """
        Extract clean text from HTML content.
        
        Args:
            html_content: Raw HTML content
            
        Returns:
            Clean text content
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from HTML: {str(e)}")
            return ""
    
    def extract_markdown_from_html(self, html_content: str) -> str:
        """
        Convert HTML content to markdown format.
        
        Args:
            html_content: Raw HTML content
            
        Returns:
            Markdown content
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Convert to markdown
            markdown_content = ""
            
            # Process headings
            for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                level = int(heading.name[1])
                markdown_content += f"{'#' * level} {heading.get_text().strip()}\n\n"
            
            # Process paragraphs
            for p in soup.find_all('p'):
                text = p.get_text().strip()
                if text:
                    markdown_content += f"{text}\n\n"
            
            # Process lists
            for ul in soup.find_all('ul'):
                for li in ul.find_all('li'):
                    text = li.get_text().strip()
                    if text:
                        markdown_content += f"- {text}\n"
                markdown_content += "\n"
            
            for ol in soup.find_all('ol'):
                for i, li in enumerate(ol.find_all('li'), 1):
                    text = li.get_text().strip()
                    if text:
                        markdown_content += f"{i}. {text}\n"
                markdown_content += "\n"
            
            return markdown_content.strip()
            
        except Exception as e:
            logger.error(f"Error converting HTML to markdown: {str(e)}")
            return ""
    
    def extract_medicine_info(self, html_content: str) -> Dict[str, Any]:
        """
        Extract medicine information from HTML content.
        
        Args:
            html_content: Raw HTML content
            
        Returns:
            Dictionary with medicine information
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            info = {
                "name": "",
                "description": "",
                "ingredients": [],
                "dosage": "",
                "side_effects": [],
                "contraindications": [],
                "raw_text": self.extract_text_from_html(html_content),
                "markdown": self.extract_markdown_from_html(html_content)
            }
            
            # Try to extract medicine name from title or h1
            title = soup.find('title')
            if title:
                info["name"] = title.get_text().strip()
            
            h1 = soup.find('h1')
            if h1:
                info["name"] = h1.get_text().strip()
            
            # Extract description from meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                info["description"] = meta_desc.get('content', '').strip()
            
            # Look for common medicine information patterns
            text = info["raw_text"].lower()
            
            # Extract ingredients
            if "skład" in text or "ingredients" in text:
                # Look for ingredients section
                pass
            
            # Extract dosage information
            if "dawkowanie" in text or "dosage" in text:
                # Look for dosage section
                pass
            
            # Extract side effects
            if "działania niepożądane" in text or "side effects" in text:
                # Look for side effects section
                pass
            
            return info
            
        except Exception as e:
            logger.error(f"Error extracting medicine info: {str(e)}")
            return {"error": str(e)}
    
    def scrape_medicine_page(self, url: str) -> Dict[str, Any]:
        """
        Scrape a medicine information page.
        
        Args:
            url: URL of the medicine page
            
        Returns:
            Dictionary with scraped information
        """
        try:
            html_content = self.get_page_content(url)
            if not html_content:
                return {"error": "Failed to get page content"}
            
            medicine_info = self.extract_medicine_info(html_content)
            medicine_info["url"] = url
            medicine_info["scraped_at"] = time.time()
            
            return medicine_info
            
        except Exception as e:
            logger.error(f"Error scraping medicine page {url}: {str(e)}")
            return {"error": str(e), "url": url}


def scrape_pharmaceutical_website(base_url: str, max_pages: int = 100) -> List[Dict[str, Any]]:
    """
    Scrape a pharmaceutical website for medicine information.
    
    Args:
        base_url: Base URL of the website
        max_pages: Maximum number of pages to scrape
        
    Returns:
        List of scraped medicine information
    """
    scraper = WebScraper()
    results = []
    
    try:
        # Get the main page
        main_content = scraper.get_page_content(base_url)
        if not main_content:
            logger.error(f"Failed to get main page content from {base_url}")
            return results
        
        # Parse the main page to find medicine links
        soup = BeautifulSoup(main_content, 'html.parser')
        
        # Look for links that might lead to medicine pages
        medicine_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text().strip().lower()
            
            # Check if this looks like a medicine link
            if any(keyword in text for keyword in ['lek', 'medicine', 'drug', 'tablet', 'syrop']):
                full_url = urljoin(base_url, href)
                medicine_links.append(full_url)
        
        # Limit the number of pages
        medicine_links = medicine_links[:max_pages]
        
        logger.info(f"Found {len(medicine_links)} potential medicine pages")
        
        # Scrape each medicine page
        for i, url in enumerate(medicine_links, 1):
            logger.info(f"Scraping medicine page {i}/{len(medicine_links)}: {url}")
            
            medicine_info = scraper.scrape_medicine_page(url)
            if "error" not in medicine_info:
                results.append(medicine_info)
            
            # Add delay between requests
            time.sleep(scraper.delay)
        
        logger.info(f"Scraping completed. Successfully scraped {len(results)} pages")
        return results
        
    except Exception as e:
        logger.error(f"Error during website scraping: {str(e)}")
        return results


def save_scraped_data_to_markdown(scraped_data: List[Dict[str, Any]], output_dir: str) -> Dict[str, Any]:
    """
    Save scraped data to markdown files.
    
    Args:
        scraped_data: List of scraped medicine information
        output_dir: Output directory for markdown files
        
    Returns:
        Dictionary with save results
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        results = {
            "total": len(scraped_data),
            "saved": 0,
            "failed": 0,
            "errors": []
        }
        
        for medicine_info in scraped_data:
            try:
                if "error" in medicine_info:
                    results["failed"] += 1
                    results["errors"].append(f"Error in medicine info: {medicine_info['error']}")
                    continue
                
                # Create filename from medicine name
                name = medicine_info.get("name", "unknown")
                clean_name = re.sub(r'[<>:"/\\|?*]', '_', name)
                filename = f"{clean_name}.md"
                filepath = os.path.join(output_dir, filename)
                
                # Create markdown content
                markdown_content = f"# {name}\n\n"
                
                if medicine_info.get("description"):
                    markdown_content += f"{medicine_info['description']}\n\n"
                
                if medicine_info.get("markdown"):
                    markdown_content += medicine_info["markdown"]
                
                # Add metadata
                markdown_content += f"\n\n---\n"
                markdown_content += f"Source: {medicine_info.get('url', 'Unknown')}\n"
                markdown_content += f"Scraped: {time.ctime(medicine_info.get('scraped_at', time.time()))}\n"
                
                # Save to file
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                
                results["saved"] += 1
                logger.info(f"Saved medicine info: {name}")
                
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"Error saving {medicine_info.get('name', 'unknown')}: {str(e)}")
        
        logger.info(f"Save completed: {results['saved']} saved, {results['failed']} failed")
        return results
        
    except Exception as e:
        logger.error(f"Error saving scraped data: {str(e)}")
        return {
            "total": len(scraped_data),
            "saved": 0,
            "failed": len(scraped_data),
            "errors": [str(e)]
        }
