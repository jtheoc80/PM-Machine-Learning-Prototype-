"""
Web Data Collection Module

Gathers relevant data about pressure relief valves from the internet
"""

import os
import logging
from typing import List, Dict, Optional
from urllib.parse import quote_plus
import time

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class WebDataCollector:
    """
    Collects relevant data about pressure relief valves from web sources
    """
    
    def __init__(self, cache_dir: str = "./data/cache"):
        """
        Initialize the web data collector
        
        Args:
            cache_dir: Directory to cache downloaded content
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        # Set up headers to mimic a browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def search_web(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Search for information on the web (simplified version)
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with titles and URLs
        """
        logger.info(f"Searching web for: {query}")
        
        # Note: This is a placeholder implementation
        # In production, you would integrate with a proper search API
        # or use a search engine that allows scraping
        
        results = []
        
        # Example: Search using DuckDuckGo HTML (respects robots.txt)
        try:
            encoded_query = quote_plus(query)
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse search results
            result_divs = soup.find_all('div', class_='result')[:max_results]
            
            for div in result_divs:
                title_elem = div.find('a', class_='result__a')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href', '')
                    
                    snippet_elem = div.find('a', class_='result__snippet')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                    
                    results.append({
                        'title': title,
                        'url': link,
                        'snippet': snippet
                    })
            
            logger.info(f"Found {len(results)} results")
            
        except Exception as e:
            logger.error(f"Error searching web: {e}")
        
        return results
    
    def fetch_url_content(self, url: str) -> Optional[str]:
        """
        Fetch content from a URL
        
        Args:
            url: URL to fetch
            
        Returns:
            Text content of the page, or None if failed
        """
        try:
            logger.info(f"Fetching content from: {url}")
            
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(['script', 'style', 'nav', 'footer', 'header']):
                script.decompose()
            
            # Get text
            text = soup.get_text(separator='\n', strip=True)
            
            # Clean up text
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            content = '\n'.join(lines)
            
            logger.info(f"Fetched {len(content)} characters")
            return content
            
        except Exception as e:
            logger.error(f"Error fetching URL {url}: {e}")
            return None
    
    def collect_valve_information(self, topics: List[str] = None) -> List[str]:
        """
        Collect information about pressure relief valves from the web
        
        Args:
            topics: List of specific topics to search for
            
        Returns:
            List of collected documents
        """
        if topics is None:
            topics = [
                "pressure relief valve types and applications",
                "pressure relief valve sizing calculations",
                "pressure relief valve maintenance procedures",
                "pressure relief valve safety standards",
                "pressure relief valve installation guidelines"
            ]
        
        documents = []
        
        for topic in topics:
            logger.info(f"Collecting information on: {topic}")
            
            # Search for the topic
            results = self.search_web(topic, max_results=3)
            
            # Fetch content from top results
            for result in results:
                url = result.get('url', '')
                if url:
                    content = self.fetch_url_content(url)
                    if content and len(content) > 500:
                        # Create a document with metadata
                        doc = f"Source: {result['title']}\nURL: {url}\n\n{content}"
                        documents.append(doc)
                    
                    # Be respectful with rate limiting
                    time.sleep(2)
        
        logger.info(f"Collected {len(documents)} documents from the web")
        return documents
    
    def get_technical_documentation(self) -> List[str]:
        """
        Get general technical documentation about pressure relief valves
        
        Returns:
            List of documentation texts
        """
        # This would integrate with technical documentation APIs or databases
        # For now, return some basic technical information
        
        docs = [
            """
            Pressure Relief Valve Fundamentals:
            
            A pressure relief valve (PRV) is a safety device designed to protect 
            a pressurized vessel or system from overpressure. When the system 
            pressure exceeds the set pressure, the PRV opens and releases fluid 
            until the pressure drops to acceptable levels.
            
            Key Components:
            - Valve body and seat
            - Spring mechanism
            - Disc or poppet
            - Adjustment mechanism
            - Outlet connection
            
            Types of Pressure Relief Valves:
            1. Spring-loaded: Uses spring force to keep valve closed
            2. Pilot-operated: Uses system pressure for control
            3. Balanced bellows: Compensates for back pressure
            4. Conventional: Simple spring-loaded design
            """,
            
            """
            Pressure Relief Valve Sizing:
            
            Proper sizing is critical for PRV effectiveness. Key factors:
            
            - Required relief capacity (mass or volume flow)
            - Set pressure
            - Overpressure allowance (typically 10%)
            - Back pressure
            - Fluid properties (compressible or incompressible)
            - Operating temperature
            
            Sizing Standards:
            - ASME Boiler and Pressure Vessel Code Section VIII
            - API Standard 520/521
            - ISO 4126
            """,
            
            """
            Pressure Relief Valve Maintenance:
            
            Regular maintenance ensures reliable operation:
            
            Inspection Schedule:
            - Visual inspection: Monthly
            - Operational test: Quarterly or semi-annually
            - Full service: Annually or per manufacturer specs
            
            Common Issues:
            - Seat leakage
            - Corrosion
            - Spring degradation
            - Blocked discharge
            - Chattering
            
            Best Practices:
            - Follow manufacturer guidelines
            - Document all maintenance
            - Test in controlled environment
            - Use proper tools and spare parts
            - Train personnel on procedures
            """
        ]
        
        return docs
