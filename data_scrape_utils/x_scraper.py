import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import os
from PIL import Image
import json

# def setup_driver():
#     chrome_options = Options()
#     # chrome_options.add_argument("--headless")  # Run in background
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")
#     chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
#     service = Service(ChromeDriverManager().install())
#     driver = webdriver.Chrome(service=service, options=chrome_options)
#     return driver


def setup_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36")
    
    # Since chromedriver is working in your system, use it directly
    try:
        # Try system chromedriver first (since yours is working)
        service = Service('/usr/local/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ Using system ChromeDriver")
        return driver
    except:
        try:
            # Try without specifying path (let system find it)
            driver = webdriver.Chrome(options=chrome_options)
            print("✅ Using system PATH ChromeDriver")
            return driver
        except Exception as e:
            print(f"❌ Error: {e}")
            raise



x_users = [
    "AOC",
    "SpeakerPelosi",
    "SenSchumer",
    "Jim_Jordan",
    "GOPLeader",
    "HakeemJeffries",
    "SpeakerMcConnell",
    "RonJohnsonWI",
    "SenSchatz",
    "SenTedLieu",
    "SenMarkey",
    "SenSanders",
    "SenWarren",
    "SenTimScott",
    "GovNikkiHaley",
    "VP",
    "GovTgop",
    "GovRonDeSantis",
    "GavinNewsom",
    "PierrePoilievre",
    "JagmeetSingh",
    "Keir_Starmer",
    "NicolaSturgeon",
    "theresa_may",
    "jeremycorbyn",
    "Nigel_Farage",
    "SadiqKhan",
    "mlp_officiel",
    "OlafScholz"
]


def hybrid_scraper_manual_login(max_tweets=500, images_folder="posts"):
    """
    Scraper that waits for manual login and fetches only user's original tweets
    """
    if not os.path.exists(images_folder):
        os.makedirs(images_folder, exist_ok=True)
    
    try:
        driver = setup_driver()

        # Go to Twitter login page
        print("Opening Twitter login page...")
        driver.get("https://twitter.com/login")
        
        # Wait for manual login
        print("🔐 Please login manually in the browser window")
        print("⏳ Waiting 120 seconds for you to complete login...")
        print("   1. Enter your username/email")
        print("   2. Enter your password") 
        print("   3. Complete any 2FA/CAPTCHA if required")
        print("   4. Wait for the script to continue automatically")
        
        # Wait for login completion
        wait_time = 0
        while wait_time < 120:
            time.sleep(5)
            wait_time += 5
            current_url = driver.current_url
            
            if "home" in current_url or ("twitter.com" in current_url and "login" not in current_url):
                print("✅ Login detected! Continuing with scraping...")
                break
            else:
                print(f"Still waiting... ({wait_time}/120 seconds)")
        
        if wait_time >= 120:
            print("❌ Timeout waiting for login")
        
        for search_user in x_users:
        # Navigate to user profile
            profile_url = f"https://twitter.com/{search_user}"
            print(f"Navigating to profile: {profile_url}")
            driver.get(profile_url)
            time.sleep(25)

            # Wait for tweets to load
            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//article[@role="article"]'))
                )
                print("✅ Tweets loaded successfully")
            except Exception:
                print("❌ Tweets did not load in time.")

            tweet_data = []
            seen_tweet_texts = set()
            consecutive_no_new_tweets = 0
            max_consecutive_attempts = 8
            total_scrolls = 0
            max_total_scrolls = 100

            while len(tweet_data) < max_tweets and consecutive_no_new_tweets < max_consecutive_attempts and total_scrolls < max_total_scrolls:
                tweets_before = len(tweet_data)
                
                # Get all tweet articles on current page
                articles = driver.find_elements(By.XPATH, '//article[@role="article"]')
                print(f"Found {len(articles)} articles on page")
                
                for article in articles:
                    try:
                        # First check if this is a main tweet from the target user (not a retweet or quote)
                        try:
                            # Look for the main tweet author link
                            main_author_link = article.find_element(By.XPATH, './/div[@data-testid="User-Name"]//a[contains(@href, "/")]')
                            author_href = main_author_link.get_attribute("href")
                            
                            # Skip if not from target user
                            if f"/{search_user}" not in author_href:
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
                        
                        # Only click "Show more" for the main tweet (not quoted tweets)
                        try:
                            # Look for "Show more" but make sure it's in the main tweet area, not in quoted content
                            main_tweet_area = article.find_element(By.XPATH, './/div[@data-testid="tweetText"]')
                            # Check if there's a "Show more" link in the main tweet area
                            show_more_link = main_tweet_area.find_element(By.XPATH, './/following-sibling::*//span[text()="Show more"]')
                            if show_more_link:
                                driver.execute_script("arguments[0].click();", show_more_link)
                                time.sleep(1)
                        except:
                            pass  # No "Show more" found in main tweet
                        
                        # Extract tweet text from main tweet only
                        try:
                            tweet_text_elem = article.find_element(By.XPATH, './/div[@data-testid="tweetText"]')
                            tweet_text = tweet_text_elem.text.strip()
                        except:
                            continue  # Skip if can't find tweet text
                        
                        # Skip if empty, too short, or already seen
                        if not tweet_text or len(tweet_text) < 20 or tweet_text in seen_tweet_texts:
                            continue
                        
                        seen_tweet_texts.add(tweet_text)

                        # Extract tweet time
                        try:
                            time_elem = article.find_element(By.XPATH, './/time')
                            tweet_time = time_elem.get_attribute("datetime")
                        except:
                            tweet_time = ""

                        # Extract images from main tweet only (not from quoted content)
                        image_paths = []
                        try:
                            # Look for images in the main tweet area, not in quoted tweets
                            main_content_area = article.find_element(By.XPATH, './/div[@data-testid="tweetText"]/parent::*/parent::*')
                            images = main_content_area.find_elements(By.XPATH, './/img[contains(@src,"twimg.com/media")]')
                            
                            for img in images:
                                try:
                                    img_url = img.get_attribute("src")
                                    if img_url and "media" in img_url:
                                        img_name = f"{search_user}_{len(tweet_data)}_img_{len(image_paths)}.jpg"
                                        img_path = os.path.join(images_folder, img_name)
                                        
                                        if not os.path.exists(img_path):
                                            img_data = requests.get(img_url).content
                                            with open(img_path, "wb") as f:
                                                f.write(img_data)
                                        image_paths.append(img_path)
                                except Exception as e:
                                    print(f"Failed to download image: {e}")
                                    continue
                        except:
                            pass

                        # Save tweet data
                        tweet_data.append({
                            "tweet_id": len(tweet_data) + 1,
                            "tweet_time": tweet_time,
                            "tweet_text": tweet_text,
                            "images": ";".join(image_paths) if image_paths else "",
                            "is_reply": False  # We're only getting original tweets
                        })
                        
                        print(f"Scraped tweet #{len(tweet_data)}: {tweet_text[:100]}...")
                        
                    except Exception as e:
                        continue

                # Check if we got new tweets
                tweets_after = len(tweet_data)
                if tweets_after > tweets_before:
                    consecutive_no_new_tweets = 0
                    print(f"✅ Found {tweets_after - tweets_before} new tweets. Total: {tweets_after}")
                else:
                    consecutive_no_new_tweets += 1
                    print(f"⚠️ No new tweets found. Attempt {consecutive_no_new_tweets}/{max_consecutive_attempts}")
                    
                    # Check for retry button and click it
                    try:
                        # Look for various retry button patterns
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
                                retry_button = driver.find_element(By.XPATH, selector)
                                if retry_button and retry_button.is_displayed():
                                    print("🔄 Found retry button, clicking it...")
                                    driver.execute_script("arguments[0].click();", retry_button)
                                    retry_clicked = True
                                    time.sleep(3)  # Wait after clicking retry
                                    break
                            except:
                                continue
                        
                        if retry_clicked:
                            print("✅ Retry button clicked, waiting for content to reload...")
                            time.sleep(5)  # Extra wait for content to load
                            
                            # Wait for tweets to reload
                            try:
                                WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.XPATH, '//article[@role="article"]'))
                                )
                                print("✅ Content reloaded after retry")
                            except:
                                print("⚠️ Content still not loaded after retry")
                        else:
                            print("ℹ️ No retry button found")
                            
                    except Exception as e:
                        print(f"⚠️ Error handling retry button: {e}")
                
                if len(tweet_data) >= max_tweets:
                    print(f"🎯 Reached target of {max_tweets} tweets!")
                    break

                # Enhanced scrolling
                total_scrolls += 1
                
                # Scroll more aggressively
                scroll_amount = 1500 + (total_scrolls * 100)  # Increase scroll amount over time
                driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                time.sleep(3)
                
                # Additional scroll if no new tweets found
                if consecutive_no_new_tweets >= 2:
                    # Check for retry button again before additional scrolling
                    try:
                        retry_button = driver.find_element(By.XPATH, '//span[contains(text(), "Retry")] | //span[contains(text(), "Try again")]')
                        if retry_button and retry_button.is_displayed():
                            print("🔄 Found retry button during additional scrolling, clicking it...")
                            driver.execute_script("arguments[0].click();", retry_button)
                            time.sleep(3)
                    except:
                        pass
                    
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    # Try scrolling back up a bit and then down again
                    driver.execute_script("window.scrollBy(0, -500);")
                    time.sleep(1)
                    driver.execute_script("window.scrollBy(0, 1000);")
                    time.sleep(2)

            print(f"📊 Scraping completed! Total scrolls: {total_scrolls}")
            
            # Save to CSV
            df = pd.DataFrame(tweet_data)
            df.to_csv(f"{search_user}_tweets.csv", index=False)
            print(f"✅ Saved {len(df)} tweets to {search_user}_tweets.csv and images to {images_folder}/")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()
   
    


# driver = setup_driver()
# for user in x_users:
#     try:
#         hybrid_scraper_manual_login(driver,user)
#     except Exception as e:
#         print("Error",e)
#     finally:
#         driver.quit()
hybrid_scraper_manual_login()