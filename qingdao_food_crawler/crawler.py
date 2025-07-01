#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import random
import json
import pandas as pd
import requests
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("crawler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("QingdaoFoodCrawler")

class QingdaoFoodCrawler:
    """
    A web crawler to extract restaurant information from Huangdao, Qingdao.
    """
    
    def __init__(self, output_dir="./data"):
        """
        Initialize the crawler with user agent rotation and output directory.
        
        Args:
            output_dir (str): Directory to save the crawled data
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # User agent rotation to avoid being blocked
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
        ]
        
        # Base headers for requests
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Referer": "https://www.dianping.com/",
        }
        
        # Restaurant data storage
        self.restaurants = []
    
    def _get_random_user_agent(self):
        """Get a random user agent from the list."""
        return random.choice(self.user_agents)
    
    def _get_headers(self):
        """Get request headers with a random user agent."""
        headers = self.headers.copy()
        headers["User-Agent"] = self._get_random_user_agent()
        return headers
    
    def _make_request(self, url, params=None):
        """
        Make an HTTP request with error handling and retry logic.
        
        Args:
            url (str): URL to request
            params (dict, optional): Query parameters
            
        Returns:
            BeautifulSoup: Parsed HTML content or None if failed
        """
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                headers = self._get_headers()
                response = requests.get(url, headers=headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    return BeautifulSoup(response.text, 'html.parser')
                elif response.status_code == 403:
                    logger.warning(f"Access forbidden (403). Possibly rate-limited. URL: {url}")
                    time.sleep(retry_delay * (attempt + 1) * 2)  # Exponential backoff
                else:
                    logger.warning(f"Request failed with status code {response.status_code}. URL: {url}")
                    time.sleep(retry_delay * (attempt + 1))
            except Exception as e:
                logger.error(f"Request error: {str(e)}. URL: {url}")
                time.sleep(retry_delay * (attempt + 1))
        
        logger.error(f"Failed to retrieve {url} after {max_retries} attempts")
        return None
    
    def crawl_dianping_huangdao(self, pages=5):
        """
        Crawl restaurant information from Dianping in Huangdao area.
        
        Args:
            pages (int): Number of pages to crawl
            
        Returns:
            list: List of restaurant dictionaries
        """
        logger.info(f"Starting to crawl Dianping for Huangdao restaurants, {pages} pages")
        
        # Dianping search URL for Huangdao restaurants
        base_url = "https://www.dianping.com/huangdao/ch10"
        
        for page in range(1, pages + 1):
            logger.info(f"Crawling page {page}/{pages}")
            
            # Construct page URL (page 1 has no p parameter)
            url = base_url if page == 1 else f"{base_url}/p{page}"
            
            # Make the request
            soup = self._make_request(url)
            if not soup:
                continue
            
            # Extract restaurant list
            restaurant_list = soup.select(".shop-list ul li")
            
            if not restaurant_list:
                logger.warning(f"No restaurants found on page {page}. Possibly blocked or reached the end.")
                break
            
            # Process each restaurant
            for restaurant in restaurant_list:
                try:
                    # Extract basic information
                    name_tag = restaurant.select_one(".tit a")
                    if not name_tag:
                        continue
                    
                    name = name_tag.text.strip()
                    url = name_tag.get("href", "")
                    
                    # Extract rating
                    rating_tag = restaurant.select_one(".star_icon")
                    rating = rating_tag.get("title", "No rating") if rating_tag else "No rating"
                    
                    # Extract review count
                    review_count_tag = restaurant.select_one(".review-num")
                    review_count = review_count_tag.text.strip() if review_count_tag else "0"
                    
                    # Extract price
                    price_tag = restaurant.select_one(".mean-price")
                    price = price_tag.text.strip() if price_tag else "价格未知"
                    
                    # Extract address
                    address_tag = restaurant.select_one(".addr")
                    address = address_tag.text.strip() if address_tag else "地址未知"
                    
                    # Extract categories
                    category_tags = restaurant.select(".tag-addr a")
                    categories = [tag.text.strip() for tag in category_tags] if category_tags else []
                    
                    # Create restaurant dictionary
                    restaurant_data = {
                        "name": name,
                        "url": url,
                        "rating": rating,
                        "review_count": review_count,
                        "price": price,
                        "address": address,
                        "categories": categories,
                        "source": "dianping"
                    }
                    
                    self.restaurants.append(restaurant_data)
                    logger.debug(f"Extracted restaurant: {name}")
                    
                except Exception as e:
                    logger.error(f"Error extracting restaurant data: {str(e)}")
            
            # Random delay between requests to avoid being blocked
            time.sleep(random.uniform(2, 5))
        
        logger.info(f"Finished crawling Dianping. Extracted {len(self.restaurants)} restaurants.")
        return self.restaurants
    
    def crawl_meituan_huangdao(self, pages=5):
        """
        Crawl restaurant information from Meituan in Huangdao area.
        
        Args:
            pages (int): Number of pages to crawl
            
        Returns:
            list: List of restaurant dictionaries
        """
        logger.info(f"Starting to crawl Meituan for Huangdao restaurants, {pages} pages")
        
        # Meituan search URL for Huangdao restaurants
        base_url = "https://qd.meituan.com/meishi/huangdao/"
        
        for page in range(1, pages + 1):
            logger.info(f"Crawling page {page}/{pages}")
            
            # Construct page URL and parameters
            params = {"page": page}
            
            # Make the request
            soup = self._make_request(base_url, params)
            if not soup:
                continue
            
            # Extract restaurant list - adjust selectors based on Meituan's HTML structure
            restaurant_list = soup.select(".list .item")
            
            if not restaurant_list:
                logger.warning(f"No restaurants found on page {page}. Possibly blocked or reached the end.")
                break
            
            # Process each restaurant
            for restaurant in restaurant_list:
                try:
                    # Extract basic information
                    name_tag = restaurant.select_one(".title")
                    if not name_tag:
                        continue
                    
                    name = name_tag.text.strip()
                    url_tag = restaurant.select_one("a")
                    url = url_tag.get("href", "") if url_tag else ""
                    
                    # Extract rating
                    rating_tag = restaurant.select_one(".score")
                    rating = rating_tag.text.strip() if rating_tag else "No rating"
                    
                    # Extract price
                    price_tag = restaurant.select_one(".price")
                    price = price_tag.text.strip() if price_tag else "价格未知"
                    
                    # Extract address
                    address_tag = restaurant.select_one(".address")
                    address = address_tag.text.strip() if address_tag else "地址未知"
                    
                    # Extract categories
                    category_tag = restaurant.select_one(".tag")
                    categories = [category_tag.text.strip()] if category_tag else []
                    
                    # Create restaurant dictionary
                    restaurant_data = {
                        "name": name,
                        "url": url,
                        "rating": rating,
                        "price": price,
                        "address": address,
                        "categories": categories,
                        "source": "meituan"
                    }
                    
                    self.restaurants.append(restaurant_data)
                    logger.debug(f"Extracted restaurant: {name}")
                    
                except Exception as e:
                    logger.error(f"Error extracting restaurant data: {str(e)}")
            
            # Random delay between requests to avoid being blocked
            time.sleep(random.uniform(2, 5))
        
        logger.info(f"Finished crawling Meituan. Total restaurants: {len(self.restaurants)}")
        return self.restaurants
    
    def save_to_csv(self, filename="qingdao_huangdao_restaurants.csv"):
        """
        Save the crawled restaurant data to a CSV file.
        
        Args:
            filename (str): Output filename
            
        Returns:
            str: Path to the saved file
        """
        if not self.restaurants:
            logger.warning("No restaurant data to save")
            return None
        
        output_path = os.path.join(self.output_dir, filename)
        
        # Convert list of dictionaries to DataFrame
        df = pd.DataFrame(self.restaurants)
        
        # Convert categories list to string
        df['categories'] = df['categories'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
        
        # Save to CSV
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        logger.info(f"Saved {len(self.restaurants)} restaurants to {output_path}")
        
        return output_path
    
    def save_to_json(self, filename="qingdao_huangdao_restaurants.json"):
        """
        Save the crawled restaurant data to a JSON file.
        
        Args:
            filename (str): Output filename
            
        Returns:
            str: Path to the saved file
        """
        if not self.restaurants:
            logger.warning("No restaurant data to save")
            return None
        
        output_path = os.path.join(self.output_dir, filename)
        
        # Save to JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.restaurants, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved {len(self.restaurants)} restaurants to {output_path}")
        return output_path
    
    def run(self, sources=None, pages_per_source=5):
        """
        Run the crawler on specified sources.
        
        Args:
            sources (list): List of sources to crawl ('dianping', 'meituan')
            pages_per_source (int): Number of pages to crawl per source
            
        Returns:
            tuple: Paths to saved CSV and JSON files
        """
        if sources is None:
            sources = ['dianping', 'meituan']
        
        for source in sources:
            if source == 'dianping':
                self.crawl_dianping_huangdao(pages=pages_per_source)
            elif source == 'meituan':
                self.crawl_meituan_huangdao(pages=pages_per_source)
            else:
                logger.warning(f"Unknown source: {source}")
        
        # Save results
        csv_path = self.save_to_csv()
        json_path = self.save_to_json()
        
        return csv_path, json_path


if __name__ == "__main__":
    # Create and run the crawler
    crawler = QingdaoFoodCrawler()
    csv_path, json_path = crawler.run(pages_per_source=3)
    
    print(f"Crawling completed. Results saved to:")
    print(f"CSV: {csv_path}")
    print(f"JSON: {json_path}")