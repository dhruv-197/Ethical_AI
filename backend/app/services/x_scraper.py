import time
import requests
import os
import hashlib
import shutil
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from datetime import datetime
import logging
from typing import Dict, List, Optional
import re
from langdetect import detect
from googletrans import Translator
import os
from dotenv import load_dotenv
load_dotenv(override=True)
logger = logging.getLogger(__name__)
CHROME_DRIVER_PATH = os.getenv('CHROME_DRIVER_PATH')


class XScraper:
    def __init__(self, headless=True, delay=2):
        self.delay = delay
        self.setup_driver(headless)
        self.setup_image_directory()
    
    def setup_image_directory(self):
        """Setup directory for downloaded images"""
        self.images_dir = os.path.join(os.getcwd(), 'downloaded_images')
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)
            logger.info(f"Created images directory: {self.images_dir}")
    
    def setup_driver(self, headless=False):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            # Try local chromedriver first, then use webdriver manager
            try:
                service = Service(CHROME_DRIVER_PATH)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                
            # Execute script to avoid detection
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.wait = WebDriverWait(self.driver, 15)
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            raise
    
    def download_image(self, url: str, username: str, tweet_id: str = None) -> Optional[str]:
        """
        Download image from URL and return local path
        
        Args:
            url: Image URL
            username: Username for organizing files
            tweet_id: Tweet ID for unique naming
            
        Returns:
            Local file path or None if download failed
        """
        try:
            # Create user directory
            user_dir = os.path.join(self.images_dir, username)
            if not os.path.exists(user_dir):
                os.makedirs(user_dir)
            
            # Generate unique filename
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            parsed_url = urlparse(url)
            file_extension = os.path.splitext(parsed_url.path)[1] or '.jpg'
            
            if tweet_id:
                filename = f"{tweet_id}_{url_hash}{file_extension}"
            else:
                filename = f"{url_hash}{file_extension}"
            
            local_path = os.path.join(user_dir, filename)
            # Check if file already exists
            if os.path.exists(local_path):
                logger.info(f"Image already exists: {local_path}")
                return local_path
            
            # Download image
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10, stream=True)
            response.raise_for_status()
            
            # Save image
            with open(local_path, 'wb') as f:
                shutil.copyfileobj(response.raw, f)
            
            logger.info(f"Downloaded image: {url} -> {local_path}")
            return local_path
            
        except Exception as e:
            logger.error(f"Failed to download image {url}: {e}")
            return None
    
    def get_user_profile(self, username: str) -> Optional[Dict]:
        """Scrape basic user profile information"""
        try:      
            url = f"https://x.com/{username}"
            # print(f"🔍 Scraping profile for {username}")
            self.driver.get(url)
            time.sleep(self.delay)
            
            # Check if profile exists
            if "doesn't exist" in self.driver.page_source.lower():
                print(f"❌ Account {username} doesn't exist")
                return None
            
            # Wait for profile to load
            try:
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
            except TimeoutException:
                print(f"❌ Profile page didn't load for {username}")
                return None
            
            # Download profile image (but store separately)
            profile_image_url = self._get_profile_image()
            if profile_image_url:
                local_profile_image = self.download_image(profile_image_url, username)
                print(f"📸 Downloaded profile image to: {local_profile_image}")
            banner_image_url = self._get_banner_image()
            if banner_image_url:
                local_banner_image_url = self.download_image(banner_image_url, username)
                print(f"📸 Downloaded profile image to: {local_profile_image}")
            
            # Extract profile data - only fields that exist in User model
            profile_data = {
                'username': username,
                'name': self._get_profile_name(),
                'bio': self._get_profile_bio(),
                'followers_count': self._get_followers_count(),
                'following_count': self._get_following_count(),
                'joined_date':self._get_joined_date(),
                'profile_image_url': profile_image_url,
                'banner_image_url':banner_image_url,
                'tweets_count': 0,
                'verified': False,
                'protected': False,
                'likes_count': 0,
                'location':self._get_location()
            }

            return profile_data
            
        except Exception as e:
            print(f"❌ Error scraping profile for {username}: {e}")
            return None
        
    def _handle_retry_and_scroll(self, consecutive_no_new_tweets: int, total_scrolls: int):
        """Handle retry buttons and enhanced scrolling"""
        try:
            # Check for retry button and click it
            retry_selectors = [
                '//span[contains(text(), "Retry")]',
                '//span[contains(text(), "Try again")]',
                '//button[contains(text(), "Retry")]',
                '//button[contains(text(), "Try again")]',
                '//div[contains(text(), "Retry")]',
                '//div[contains(text(), "Try again")]',
                '//span[contains(text(), "Something went wrong")]/..//span[contains(text(), "Retry")]',
                '//div[@role="button" and contains(., "Retry")]',
                '//div[@role="button" and contains(., "Try again")]'
            ]
            
            retry_clicked = False
            for selector in retry_selectors:
                try:
                    retry_button = self.driver.find_element(By.XPATH, selector)
                    if retry_button and retry_button.is_displayed():
                        self.driver.execute_script("arguments[0].click();", retry_button)
                        retry_clicked = True
                        time.sleep(3)  # Wait after clicking retry
                        break
                except:
                    continue
            
            if retry_clicked:
                time.sleep(5)  # Extra wait for content to load
                
                # Wait for tweets to reload
                try:
                    self.wait.until(
                        EC.presence_of_element_located((By.XPATH, '//article[@role="article"]'))
                    )
                except:
                    print("⚠️ Content still not loaded after retry")
            
            # Enhanced scrolling
            scroll_amount = 1500 + (total_scrolls * 100)  # Increase scroll amount over time
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(3)
            
            # Additional scroll if no new tweets found
            if consecutive_no_new_tweets >= 2:
                # Check for retry button again before additional scrolling
                try:
                    retry_button = self.driver.find_element(By.XPATH, '//span[contains(text(), "Retry")] | //span[contains(text(), "Try again")]')
                    if retry_button and retry_button.is_displayed():
                        self.driver.execute_script("arguments[0].click();", retry_button)
                        time.sleep(3)
                except:
                    pass
                
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                # Try scrolling back up a bit and then down again
                self.driver.execute_script("window.scrollBy(0, -500);")
                time.sleep(1)
                self.driver.execute_script("window.scrollBy(0, 1000);")
                time.sleep(2)
                
        except Exception as e:
            print(f"⚠️ Error in retry/scroll handling: {e}")

    def detect_language(self,text, max_length=500):
        """
        Detect the language of the text by sampling from the content.
        Uses up to `max_length` characters of meaningful text for detection.
        """
        try:
            if not text or len(text.strip()) < 3:
                return False  # Too short to detect language

            # Clean and condense whitespace
            text = re.sub(r'\s+', ' ', text).strip()

            # Use only the first `max_length` characters
            sample = text[:max_length]

            lang = detect(sample)
            return lang

        except Exception:
            return False
    def translate_text(self,text: str, source_lang: str, target_lang: str = 'en') -> str:
        """
        Translate YouTube transcript text from source language to target language.
        
        Args:
            text (str): The transcript text to translate
            source_lang (str): Source language code (e.g., 'es', 'fr', 'de')
            target_lang (str): Target language code (default: 'en')
        
        Returns:
            str: Translated text
        """
        
        # Initialize translator
        translator = Translator()
        
        # Clean the text - remove excessive whitespace and transcript artifacts
        text = re.sub(r'\s+', ' ', text.strip())
        text = re.sub(r'\[.*?\]', '', text)  # Remove [Music], [Applause], etc.
        text = re.sub(r'\(.*?\)', '', text)  # Remove (inaudible), etc.
        
        # If text is empty after cleaning
        if not text:
            return ""
        
        # Google Translate has a character limit (~5000 chars per request)
        # Split long text into chunks
        max_chunk_size = 4000
        
        if len(text) <= max_chunk_size:
            try:
                result = translator.translate(text, src=source_lang, dest=target_lang)
                return result.text
            except Exception as e:
                print(f"Translation error: {e}")
                return text
        
        # For longer texts, split into chunks
        chunks = self.split_text_into_chunks(text, max_chunk_size)
        translated_chunks = []
        
        for i, chunk in enumerate(chunks):
            try:
                # Add small delay to avoid rate limiting
                if i > 0:
                    time.sleep(0.1)
                
                result = translator.translate(chunk, src=source_lang, dest=target_lang)
                translated_chunks.append(result.text)
                
            except Exception as e:
                print(f"Error translating chunk {i+1}: {e}")
                translated_chunks.append(chunk)  # Keep original if translation fails
        return ' '.join(translated_chunks)

    def split_text_into_chunks(self,text: str, max_size: int) -> List[str]:
        """
        Split text into chunks while preserving sentence boundaries.
        
        Args:
            text (str): Text to split
            max_size (int): Maximum chunk size in characters
        
        Returns:
            List[str]: List of text chunks
        """
        if len(text) <= max_size:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        # Split by sentences first
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        for sentence in sentences:
            # If single sentence is too long, split by words
            if len(sentence) > max_size:
                words = sentence.split()
                for word in words:
                    if len(current_chunk) + len(word) + 1 <= max_size:
                        current_chunk += (" " + word) if current_chunk else word
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = word
            else:
                # Check if adding this sentence exceeds limit
                if len(current_chunk) + len(sentence) + 1 <= max_size:
                    current_chunk += (" " + sentence) if current_chunk else sentence
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence
        
        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks

    def get_user_tweets(self, username: str, max_tweets: int = 50, media_only: bool = False) -> List[Dict]:
        """
        Scrape user tweets with improved logic from working scraper
        
        Args:
            username: Twitter username
            max_tweets: Maximum number of tweets to scrape
            media_only: If True, only return tweets with media
        
        Returns:
            List of tweet dictionaries with simplified structure
        """
        try:
            url = f"https://x.com/{username}"
            self.driver.get(url)
            time.sleep(self.delay)
            
            # Wait for tweets to load
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.XPATH, '//article[@role="article"]'))
                )
            except Exception:
                print("❌ Tweets did not load in time")
                return []
            
            tweets = []
            processed_texts = set()  # Avoid duplicates
            consecutive_no_new_tweets = 0
            max_consecutive_attempts = 8
            total_scrolls = 0
            max_total_scrolls = 50
            
            while len(tweets) < max_tweets and consecutive_no_new_tweets < max_consecutive_attempts and total_scrolls < max_total_scrolls:
                tweets_before = len(tweets)
                
                # Find tweet elements using improved selector
                tweet_elements = self.driver.find_elements(By.XPATH, '//article[@role="article"]')
                
                if not tweet_elements:
                    print(f"❌ No tweet articles found")
                    consecutive_no_new_tweets += 1
                    self._handle_retry_and_scroll(consecutive_no_new_tweets, total_scrolls)
                    continue

                for article in tweet_elements:
                    if len(tweets) >= max_tweets:
                        break
                    
                    try:
                        # Check if this is a main tweet from the target user (not a retweet)
                        try:
                            # Look for the main tweet author link
                            main_author_link = article.find_element(By.XPATH, './/div[@data-testid="User-Name"]//a[contains(@href, "/")]')
                            author_href = main_author_link.get_attribute("href")
                            
                            # Skip if not from target user
                            if f"/{username}" not in author_href:
                                continue
                                
                        except Exception:
                            continue
                        
                        # Skip if this is a reply to someone else
                        try:
                            reply_indicator = article.find_element(By.XPATH, './/span[contains(text(), "Replying to")]')
                            if reply_indicator:
                                continue  # Skip replies
                        except:
                            pass  # No reply indicator found, continue
                        
                        # Handle "Show more" for main tweet only
                        try:
                            main_tweet_area = article.find_element(By.XPATH, './/div[@data-testid="tweetText"]')
                            show_more_link = main_tweet_area.find_element(By.XPATH, './/following-sibling::*//span[text()="Show more"]')
                            if show_more_link:
                                self.driver.execute_script("arguments[0].click();", show_more_link)
                                time.sleep(1)
                        except:
                            pass  # No "Show more" found
                        
                        # Extract tweet text from main tweet only
                        try:
                            tweet_text_elem = article.find_element(By.XPATH, './/div[@data-testid="tweetText"]')
                            tweet_text = tweet_text_elem.text.strip()
                            source_lang = self.detect_language(text=tweet_text)
                            if source_lang != 'en':
                                tweet_text = self.translate_text(text=tweet_text,source_lang=source_lang)
                        except:
                            continue  # Skip if can't find tweet text
                        
                        # Skip if empty, too short, or already seen
                        if not tweet_text or len(tweet_text) < 20 or tweet_text in processed_texts:
                            continue
                        
                        processed_texts.add(tweet_text)
                        
                        # Extract tweet time
                        try:
                            time_elem = article.find_element(By.XPATH, './/time')
                            tweet_time = time_elem.get_attribute("datetime")
                            # Convert to datetime object
                            posted_at = datetime.fromisoformat(tweet_time.replace('Z', '+00:00')) if tweet_time else datetime.utcnow()
                        except:
                            posted_at = datetime.utcnow()
                        
                        # Extract media links from main tweet only
                        media_links = []
                        local_media_paths = []
                        
                        try:
                            # Look for images in the main tweet area, not in quoted tweets
                            main_content_area = article.find_element(By.XPATH, './/div[@data-testid="tweetText"]/parent::*/parent::*')
                            images = main_content_area.find_elements(By.XPATH, './/img[contains(@src,"twimg.com/media") or contains(@src,"pbs.twimg.com/media")]')
                            
                            for img in images:
                                try:
                                    img_url = img.get_attribute("src")
                                    if img_url and "media" in img_url:
                                        # Clean up the URL to get full size image
                                        if '?format=' in img_url:
                                            img_url = img_url.split('?format=')[0] + '?format=jpg&name=large'
                                        
                                        if img_url not in media_links:
                                            media_links.append(img_url)
                                            
                                            # Download image
                                            tweet_id = str(abs(hash(tweet_text[:50])))
                                            local_path = self.download_image(img_url, username, tweet_id)
                                            if local_path:
                                                local_media_paths.append(local_path)
                                                
                                except Exception as e:
                                    print(f"Failed to process image: {e}")
                                    continue
                        except:
                            pass
                        
                        # Look for videos
                        try:
                            video_elements = article.find_elements(By.TAG_NAME, 'video')
                            for video in video_elements:
                                src = video.get_attribute('src')
                                if src and src not in media_links:
                                    media_links.append(src)
                        except:
                            pass
                        
                        # Extract URLs from text
                        urls = self._extract_urls(tweet_text)
                        
                        # If media_only is True, skip tweets without media
                        if media_only and not media_links:
                            continue
                        
                        # Generate tweet ID
                        tweet_id = str(abs(hash(tweet_text[:50])))
                        
                        # Create simplified tweet data
                        tweet_data = {
                            'tweet_id': tweet_id,
                            'text': tweet_text,
                            'language': 'en',  # Default language
                            'media_urls': media_links,
                            'local_media_paths': local_media_paths,
                            'urls': urls,
                            'hashtags': self._extract_hashtags(tweet_text),
                            'posted_at': posted_at
                        }
                        
                        tweets.append(tweet_data)
                        
                        # Show different message based on media
                        if media_links:
                            print(f"✅ Tweet {len(tweets)} (with {len(media_links)} media, {len(local_media_paths)} downloaded): {tweet_text[:50]}...")
                        else:
                            print(f"✅ Tweet {len(tweets)}: {tweet_text[:50]}...")
                            
                    except Exception as e:
                        continue
                
                # Check if we got new tweets
                tweets_after = len(tweets)
                if tweets_after > tweets_before:
                    consecutive_no_new_tweets = 0
                    # print(f"✅ Found {tweets_after - tweets_before} new tweets. Total: {tweets_after}")
                else:
                    consecutive_no_new_tweets += 1
                    # print(f"⚠️ No new tweets found. Attempt {consecutive_no_new_tweets}/{max_consecutive_attempts}")
                
                if len(tweets) >= max_tweets:
                    # print(f"🎯 Reached target of {max_tweets} tweets!")
                    break
                
                # Enhanced scrolling and retry logic
                self._handle_retry_and_scroll(consecutive_no_new_tweets, total_scrolls)
                total_scrolls += 1
            
            print(f"🎯 Scraped {len(tweets)} tweets for @{username}")
            return tweets
            
        except Exception as e:
            print(f"❌ Error scraping tweets for @{username}: {e}")
            return []

    def scrape_user_tweets(self, username: str, max_tweets: int = 50) -> List[Dict]:
        """
        Alias for get_user_tweets method for compatibility with routes
        """
        return self.get_user_tweets(username, max_tweets)
    
    def _extract_tweet_text(self, tweet_element) -> str:
        """Extract tweet text - improved version"""
        text_selectors = [
            '[data-testid="tweetText"]',
            'div[data-testid="tweetText"]',
            'span[data-testid="tweetText"]'
        ]
        
        for selector in text_selectors:
            try:
                text_element = tweet_element.find_element(By.CSS_SELECTOR, selector)
                text = text_element.text.strip()
                if text:
                    return text
            except NoSuchElementException:
                continue
        
        # Fallback - get any text from the element
        try:
            all_text = tweet_element.text.strip()
            if all_text and len(all_text) > 10:
                # Clean up the text
                lines = all_text.split('\n')
                for line in lines:
                    if len(line) > 20 and not line.startswith('@') and not line.isdigit():
                        # Skip lines that look like engagement metrics
                        if not any(word in line.lower() for word in ['reply', 'retweet', 'like', 'share', 'view']):
                            return line.strip()
        except:
            pass
        
        return ""
    
    def _extract_media_links(self, tweet_element) -> List[str]:
        """Extract media links from tweet - improved version"""
        media_urls = []
        
        # Look for images
        try:
            img_elements = tweet_element.find_elements(By.TAG_NAME, 'img')
            for img in img_elements:
                src = img.get_attribute('src')
                if src and ('pbs.twimg.com' in src and 'media' in src):
                    # Clean up the URL to get full size image
                    if '?format=' in src:
                        src = src.split('?format=')[0] + '?format=jpg&name=large'
                    if src not in media_urls:
                        media_urls.append(src)
        except:
            pass
        
        # Look for videos
        try:
            video_elements = tweet_element.find_elements(By.TAG_NAME, 'video')
            for video in video_elements:
                src = video.get_attribute('src')
                if src and src not in media_urls:
                    media_urls.append(src)
        except:
            pass
        
        return media_urls
    
    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.findall(url_pattern, text)
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        return re.findall(r'#\w+', text)
    
    def _get_profile_name(self) -> str:
        """Extract profile name with improved selectors"""
        selectors = [
            'div[data-testid="UserName"] span span',
            'h1[role="heading"] span span',
            '[data-testid="UserName"] span:first-child',
            'h1 span:first-child',
            '.css-1jxf684 span'
        ]

        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    name = element.text.strip()
                    if name and not name.startswith('@') and len(name) > 1:
                        return name
            except Exception:
                continue

        return "Unknown"
    
    def _get_profile_bio(self) -> str:
        """Extract profile bio with improved selectors"""
        selectors = [
            '[data-testid="UserDescription"]',
            'div[data-testid="UserDescription"]',
            '[data-testid="UserDescription"] span',
            '.css-1dbjc4n .css-1dbjc4n .css-1dbjc4n .css-901oao'
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                bio = element.text.strip()
                if bio and len(bio) > 0:
                    return bio
            except Exception:
                continue
        
        return ""
    
    def _get_followers_count(self) -> int:
        """Extract followers count with improved logic"""
        try:
            # Method 1: Look for followers link with better selectors
            followers_selectors = [
                'a[href$="/followers"] span',
                'a[href*="/followers"] span span',
                'a[href*="/verified_followers"] span',
                'div[data-testid="UserName"] ~ div a[href*="/followers"] span'
            ]
            
            for selector in followers_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if text and any(char.isdigit() for char in text) and 'following' not in text.lower():
                            count = self._parse_count(text)
                            if count >= 0:  # Allow 0 followers
                                print(f"Found followers count via CSS selector: {count}")
                                return count
                except Exception:
                    continue
            
            # Method 2: Look for profile stats section with better positioning
            try:
                # Find all links in the profile stats area
                profile_links = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="UserName"] ~ div a')
                
                for link in profile_links:
                    href = link.get_attribute('href')
                    if href and '/followers' in href:
                        # This is the followers link
                        spans = link.find_elements(By.TAG_NAME, 'span')
                        for span in spans:
                            text = span.text.strip()
                            if text and any(char.isdigit() for char in text):
                                count = self._parse_count(text)
                                if count >= 0:
                                    print(f"Found followers count via profile link: {count}")
                                    return count
            except Exception:
                pass
            
            # Method 3: Look for the pattern "X Followers" specifically
            try:
                # Look for elements that contain "Followers" but not "Following"
                xpath_selectors = [
                    "//a[contains(@href, '/followers')]/span[contains(text(), 'Followers')]/preceding-sibling::span",
                    "//a[contains(@href, '/followers')]//span[contains(text(), 'Followers')]/../span[1]",
                    "//span[contains(text(), 'Followers')]/preceding-sibling::span",
                    "//span[contains(text(), 'Followers')]/../span[1]"
                ]
                
                for xpath in xpath_selectors:
                    try:
                        elements = self.driver.find_elements(By.XPATH, xpath)
                        for element in elements:
                            text = element.text.strip()
                            if text and any(char.isdigit() for char in text):
                                count = self._parse_count(text)
                                if count >= 0:
                                    print(f"Found followers count via XPath: {count}")
                                    return count
                    except Exception:
                        continue
            except Exception:
                pass
            
            # Method 4: Look for the complete text pattern "X Followers"
            try:
                all_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Followers')]")
                for element in all_elements:
                    text = element.text.strip()
                    if 'followers' in text.lower() and 'following' not in text.lower():
                        # Extract number from patterns like "1.2K Followers"
                        numbers = re.findall(r'([\d,]+\.?\d*[KMB]?)\s*followers', text, re.IGNORECASE)
                        if numbers:
                            count = self._parse_count(numbers[0])
                            if count >= 0:
                                print(f"Found followers count via text pattern: {count}")
                                return count
            except Exception:
                pass
            
            # Method 5: Manual navigation approach
            try:
                # Look for the stats section structure
                stats_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="UserName"] ~ div div')
                
                for i, stat_element in enumerate(stats_elements):
                    try:
                        # Check if this element contains "Followers"
                        if 'followers' in stat_element.text.lower():
                            # Look for numeric value in the same element or nearby
                            all_spans = stat_element.find_elements(By.TAG_NAME, 'span')
                            for span in all_spans:
                                text = span.text.strip()
                                if text and any(char.isdigit() for char in text) and 'following' not in text.lower():
                                    count = self._parse_count(text)
                                    if count >= 0:
                                        print(f"Found followers count via stats navigation: {count}")
                                        return count
                    except Exception:
                        continue
            except Exception:
                pass
            
            print("Could not find followers count")
            
        except Exception as e:
            print(f"Error getting followers count: {e}")
        
        return 0

    def _get_following_count(self) -> int:
        """Extract following count with improved logic"""
        try:
            # Method 1: Look for following link with better selectors
            following_selectors = [
                'a[href$="/following"] span',
                'a[href*="/following"] span span',
                'div[data-testid="UserName"] ~ div a[href*="/following"] span'
            ]
            
            for selector in following_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if text and any(char.isdigit() for char in text) and 'followers' not in text.lower():
                            count = self._parse_count(text)
                            if count >= 0:  # Allow 0 following
                                print(f"Found following count via CSS selector: {count}")
                                return count
                except Exception:
                    continue
            
            # Method 2: Look for profile stats section
            try:
                # Find all links in the profile stats area
                profile_links = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="UserName"] ~ div a')
                
                for link in profile_links:
                    href = link.get_attribute('href')
                    if href and '/following' in href and '/followers' not in href:
                        # This is the following link
                        spans = link.find_elements(By.TAG_NAME, 'span')
                        for span in spans:
                            text = span.text.strip()
                            if text and any(char.isdigit() for char in text):
                                count = self._parse_count(text)
                                if count >= 0:
                                    print(f"Found following count via profile link: {count}")
                                    return count
            except Exception:
                pass
            
            # Method 3: Look for the pattern "X Following" specifically
            try:
                xpath_selectors = [
                    "//a[contains(@href, '/following') and not(contains(@href, '/followers'))]/span[contains(text(), 'Following')]/preceding-sibling::span",
                    "//a[contains(@href, '/following') and not(contains(@href, '/followers'))]//span[contains(text(), 'Following')]/../span[1]",
                    "//span[contains(text(), 'Following') and not(contains(text(), 'Followers'))]/preceding-sibling::span"
                ]
                
                for xpath in xpath_selectors:
                    try:
                        elements = self.driver.find_elements(By.XPATH, xpath)
                        for element in elements:
                            text = element.text.strip()
                            if text and any(char.isdigit() for char in text):
                                count = self._parse_count(text)
                                if count >= 0:
                                    print(f"Found following count via XPath: {count}")
                                    return count
                    except Exception:
                        continue
            except Exception:
                pass
            
            # Method 4: Look for the complete text pattern "X Following"
            try:
                all_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Following')]")
                for element in all_elements:
                    text = element.text.strip()
                    if 'following' in text.lower() and 'followers' not in text.lower():
                        # Extract number from patterns like "1.2K Following"
                        numbers = re.findall(r'([\d,]+\.?\d*[KMB]?)\s*following', text, re.IGNORECASE)
                        if numbers:
                            count = self._parse_count(numbers[0])
                            if count >= 0:
                                print(f"Found following count via text pattern: {count}")
                                return count
            except Exception:
                pass
            
            print("Could not find following count")
            
        except Exception as e:
            print(f"Error getting following count: {e}")
        
        return 0
    
    def _get_location(self) -> str:
        """Extract location from profile"""
        selectors = [
            '[data-testid="UserLocation"]',
            'span[data-testid="UserLocation"]',
            '.css-1dbjc4n .css-1dbjc4n .css-901oao[dir="ltr"]'
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                location = element.text.strip()
                if location:
                    return location
            except Exception:
                continue
        
        return ""
    
    def _get_location(self) -> str:
        """Extract location from profile"""
        selectors = [
            '[data-testid="UserLocation"]',
            'span[data-testid="UserLocation"]',
            '.css-1dbjc4n .css-1dbjc4n .css-901oao[dir="ltr"]'
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                location = element.text.strip()
                if location:
                    return location
            except Exception:
                continue
        
        return ""

    def _get_website(self) -> str:
        """Extract website from profile"""
        selectors = [
            '[data-testid="UserUrl"] a',
            'a[href*="http"]',
            '.css-4rbku5 a'
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                website = element.get_attribute('href')
                if website and 'http' in website and 'x.com' not in website:
                    return website
            except Exception:
                continue
        
        return ""

    def _get_joined_date(self) -> Optional[datetime.date]:
        """Extract join date from X (Twitter) profile using innerText and return as date"""
        try:
            parent = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="UserJoinDate"]')
            spans = parent.find_elements(By.TAG_NAME, 'span')
            for span in spans:
                joined_text = span.get_attribute("innerText").strip()
                if 'joined' in joined_text.lower():
                    # Extract date from "Joined Month Year"
                    date_match = re.search(r'joined\s+(\w+\s+\d{4})', joined_text, re.IGNORECASE)
                    if date_match:
                        date_str = date_match.group(1)
                        # Convert to datetime.date object
                        return datetime.strptime(date_str, "%B %Y").date()
        except NoSuchElementException:
            pass

        return None


    def _get_tweets_count(self) -> int:
        """Extract tweets count from profile"""
        try:
            # Look for "posts" or "tweets" in the navigation
            nav_elements = self.driver.find_elements(By.CSS_SELECTOR, 'nav a, [role="tablist"] a')
            for nav_element in nav_elements:
                text = nav_element.text.strip()
                if any(word in text.lower() for word in ['posts', 'tweets']) and any(char.isdigit() for char in text):
                    numbers = re.findall(r'([\d,]+\.?\d*[KMB]?)', text)
                    if numbers:
                        return self._parse_count(numbers[0])
        except Exception:
            pass
        
        return 0

    def _is_verified(self) -> bool:
        """Check if profile is verified"""
        try:
            # Look for verification badge
            verification_selectors = [
                '[data-testid="verificationBadge"]',
                '.css-1dbjc4n .css-1dbjc4n svg[aria-label*="verified"]',
                'svg[aria-label*="Verified"]'
            ]
            
            for selector in verification_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element:
                        return True
                except Exception:
                    continue
        except Exception:
            pass
        
        return False

    def _is_protected(self) -> bool:
        """Check if profile is protected"""
        try:
            # Look for protected account indicator
            protected_selectors = [
                'svg[aria-label*="protected"]',
                'svg[aria-label*="locked"]',
                '[data-testid="protectedBadge"]'
            ]
            
            for selector in protected_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element:
                        return True
                except Exception:
                    continue
        except Exception:
            pass
        
        return False
    def _get_profile_image(self) -> str:
        """Extract profile image URL from X (Twitter) profile"""
        try:
            # 1. First try <img> tag with reliable alt attribute
            img_elements = self.driver.find_elements(By.CSS_SELECTOR, 'img[alt="Opens profile photo"]')
            for img in img_elements:
                src = img.get_attribute('src')
                if src and 'profile_images' in src:
                    return src.replace('_normal', '_400x400')

            # 2. Fallback: Check for background-image from div
            divs = self.driver.find_elements(By.CSS_SELECTOR, 'div[style*="background-image"]')
            for div in divs:
                style = div.get_attribute('style')
                match = re.search(r'url\(\"(https://[^"]+)\"\)', style)
                if match and 'profile_images' in match.group(1):
                    src = match.group(1)
                    return src.replace('_normal', '_400x400')

            # 3. Final fallback: any img with profile_images
            img_elements = self.driver.find_elements(By.TAG_NAME, 'img')
            for img in img_elements:
                src = img.get_attribute('src')
                if src and 'profile_images' in src:
                    return src.replace('_normal', '_400x400')

        except Exception as e:
            print(f"Error getting profile image: {e}")

        return ""

    def _get_banner_image(self) -> str:
        """Extract banner image URL from X (Twitter) profile"""
        try:
            # Look for div with background-image containing profile_banners
            divs = self.driver.find_elements(By.CSS_SELECTOR, 'div[style*="background-image"]')
            for div in divs:
                style = div.get_attribute('style')
                match = re.search(r'url\(\"(https://[^"]+profile_banners[^"]+)\"\)', style)
                if match:
                    src = match.group(1)
                    # Optionally replace '_1500x500' with highest available resolution
                    return src.replace('_1500x500', '_1500x500')
            # Fallback: any img with profile_banners in src
            img_elements = self.driver.find_elements(By.TAG_NAME, 'img')
            for img in img_elements:
                src = img.get_attribute('src')
                if src and 'profile_banners' in src:
                    return src
        except Exception as e:
            print(f"Error getting banner image: {e}")
        return ""
    # def _get_profile_image(self) -> str:
    #     """Extract profile image URL with improved logic"""
    #     try:
    #         # Look for profile image with better selectors
    #         img_selectors = [
    #             'img[src*="profile_images"]',
    #             'div[data-testid="UserAvatar"] img',
    #             'img[alt*="profile picture"]'
    #         ]
            
    #         for selector in img_selectors:
    #             try:
    #                 element = self.driver.find_element(By.CSS_SELECTOR, selector)
    #                 src = element.get_attribute('src')
    #                 if src and 'profile_images' in src:
    #                     # Get higher quality image
    #                     if '_normal' in src:
    #                         src = src.replace('_normal', '_400x400')
    #                     return src
    #             except Exception:
    #                 continue
            
    #         # Fallback: look for any image that might be profile image
    #         img_elements = self.driver.find_elements(By.TAG_NAME, 'img')
    #         for img in img_elements:
    #             src = img.get_attribute('src')
    #             if src and ('profile_images' in src or 'twimg.com' in src):
    #                 return src
                    
    #     except Exception:
    #         pass
        
    #     return ""

    def _parse_count(self, count_str: str) -> int:
        """Parse count string like '1.2K' to integer with improved logic"""
        if not count_str:
            return 0
        
        # Clean the string
        count_str = count_str.replace(',', '').replace(' ', '').upper()
        
        # Remove any non-numeric characters except K, M, B
        count_str = re.sub(r'[^\d\.KMB]', '', count_str)
        
        try:
            if 'K' in count_str:
                number = float(count_str.replace('K', ''))
                return int(number * 1000)
            elif 'M' in count_str:
                number = float(count_str.replace('M', ''))
                return int(number * 1000000)
            elif 'B' in count_str:
                number = float(count_str.replace('B', ''))
                return int(number * 1000000000)
            else:
                return int(float(count_str))
        except (ValueError, TypeError):
            return 0
    
    def close(self):
        """Close the driver"""
        if hasattr(self, 'driver'):
            self.driver.quit()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO)
#     scraper = XScraper(headless=False)
#
#     try:
#         username = 'MortalxS8ul'
#         profile = scraper.get_user_profile(username)
#         if profile:
#             # print(f"Profile data for {username}: {profile}")
#             tweets = scraper.get_user_tweets(username, max_tweets=5)
#             # print(f"Found {len(tweets)} tweets for {username}")
#             for tweet in tweets:
#                 print(f"Tweet: {tweet['text'][:50]}...")
#                 print(f"Media URLs: {tweet['media_urls']}")
#                 print(f"Local paths: {tweet['local_media_paths']}")
#                 print(f"Hashtags: {tweet['hashtags']}")
#                 print("---")
#     finally:
#         scraper.close()
#         print("Scraper closed.")