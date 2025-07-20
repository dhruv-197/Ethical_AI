import pandas as pd
import os
import re
import glob
from googletrans import Translator
from langdetect import detect, DetectorFactory
import time
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import logging

# Set seed for consistent language detection
DetectorFactory.seed = 0

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TweetProcessor:
    def __init__(self, folder_path=".", output_file="processed_tweets.csv"):
        self.folder_path = folder_path
        self.output_file = output_file
        self.translator = Translator()
        self.processed_count = 0
        self.error_count = 0
        
    def clean_text(self, text):
        """
        Clean tweet text by removing extra spaces, @ mentions, and formatting
        """
        if pd.isna(text) or not isinstance(text, str):
            return ""
            
        # Remove @ mentions
        text = re.sub(r'@\w+', '', text)
        
        # Remove hashtags but keep the text (remove # symbol)
        text = re.sub(r'#(\w+)', r'\1', text)
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text)
        
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:\-\'\"()]', '', text)
        
        return text
    
    def detect_language(self, text):
        """
        Detect the language of the text
        """
        try:
            if not text or len(text.strip()) < 3:
                return 'en'  # Default to English for very short texts
            
            lang = detect(text)
            return lang
        except:
            return 'en'  # Default to English if detection fails
    
    def translate_text(self, text, source_lang='auto', target_lang='en'):
        """
        Translate text to English with error handling and rate limiting
        """
        try:
            if not text or len(text.strip()) < 3:
                return text
                
            # If already in English, return as is
            if source_lang == 'en':
                return text
                
            # Add delay to avoid rate limiting
            time.sleep(0.5)
            
            # Translate text
            result = self.translator.translate(text, src=source_lang, dest=target_lang)
            return result.text
            
        except Exception as e:
            logger.warning(f"Translation failed: {e}")
            return text  # Return original text if translation fails
    
    def process_single_tweet(self, row):
        """
        Process a single tweet: clean, detect language, translate
        """
        try:
            # Clean the text
            cleaned_text = self.clean_text(row['tweet_text'])
            
            if not cleaned_text:
                return row.copy()
            
            # Detect language
            detected_lang = self.detect_language(cleaned_text)
            
            # Translate if not English
            if detected_lang != 'en':
                translated_text = self.translate_text(cleaned_text, detected_lang, 'en')
            else:
                translated_text = cleaned_text
            
            # Update row
            result_row = row.copy()
            result_row['original_text'] = row['tweet_text']
            result_row['cleaned_text'] = cleaned_text
            result_row['detected_language'] = detected_lang
            result_row['tweet_text'] = translated_text
            result_row['is_translated'] = detected_lang != 'en'
            
            self.processed_count += 1
            if self.processed_count % 10 == 0:
                logger.info(f"Processed {self.processed_count} tweets...")
            
            return result_row
            
        except Exception as e:
            logger.error(f"Error processing tweet: {e}")
            self.error_count += 1
            return row.copy()
    
    def process_csv_file(self, csv_file):
        """
        Process a single CSV file
        """
        try:
            logger.info(f"Processing file: {csv_file}")
            
            # Read CSV file
            df = pd.read_csv(csv_file)
            
            # Check if tweet_text column exists
            if 'tweet_text' not in df.columns:
                logger.warning(f"No 'tweet_text' column found in {csv_file}")
                return pd.DataFrame()
            
            # Add source file column
            df['source_file'] = os.path.basename(csv_file)
            
            # Process each tweet
            processed_rows = []
            for idx, row in df.iterrows():
                processed_row = self.process_single_tweet(row)
                processed_rows.append(processed_row)
                
                # Add small delay to avoid overwhelming the translation service
                if idx % 20 == 0:
                    time.sleep(1)
            
            processed_df = pd.DataFrame(processed_rows)
            logger.info(f"Completed processing {csv_file}: {len(processed_df)} tweets")
            
            return processed_df
            
        except Exception as e:
            logger.error(f"Error processing file {csv_file}: {e}")
            return pd.DataFrame()
    
    def process_all_files(self):
        """
        Process all CSV files in the folder
        """
        logger.info(f"Starting to process CSV files in: {self.folder_path}")
        
        # Find all CSV files
        csv_pattern = os.path.join(self.folder_path, "*.csv")
        csv_files = glob.glob(csv_pattern)
        
        if not csv_files:
            logger.warning("No CSV files found in the specified folder")
            return
        
        logger.info(f"Found {len(csv_files)} CSV files")
        
        # Process all files
        all_processed_data = []
        
        for csv_file in csv_files:
            processed_df = self.process_csv_file(csv_file)
            if not processed_df.empty:
                all_processed_data.append(processed_df)
        
        if not all_processed_data:
            logger.warning("No data was processed successfully")
            return
        
        # Combine all processed data
        logger.info("Combining all processed data...")
        combined_df = pd.concat(all_processed_data, ignore_index=True)
        
        # Create summary statistics
        self.create_summary_stats(combined_df)
        
        # Save to CSV
        output_path = os.path.join(self.folder_path, self.output_file)
        combined_df.to_csv(output_path, index=False)
        
        logger.info(f"✅ Processing completed!")
        logger.info(f"   Total tweets processed: {len(combined_df)}")
        logger.info(f"   Successful translations: {self.processed_count}")
        logger.info(f"   Errors encountered: {self.error_count}")
        logger.info(f"   Output saved to: {output_path}")
        
        return combined_df
    
    def create_summary_stats(self, df):
        """
        Create and display summary statistics
        """
        logger.info("\n📊 PROCESSING SUMMARY:")
        logger.info(f"Total tweets: {len(df)}")
        
        if 'detected_language' in df.columns:
            lang_counts = df['detected_language'].value_counts()
            logger.info(f"Languages detected:")
            for lang, count in lang_counts.items():
                logger.info(f"  {lang}: {count} tweets")
        
        if 'is_translated' in df.columns:
            translated_count = df['is_translated'].sum()
            logger.info(f"Tweets translated: {translated_count}")
            logger.info(f"Tweets kept original: {len(df) - translated_count}")
        
        if 'source_file' in df.columns:
            file_counts = df['source_file'].value_counts()
            logger.info(f"Tweets per file:")
            for file, count in file_counts.items():
                logger.info(f"  {file}: {count} tweets")

def main():
    """
    Main function to run the processor
    """
    # Configuration
    folder_path = "/home/bacancy/Development/DataScience/X_seniment_analyis"  # Change this to your folder path
    output_file = "all_tweets_processed_english.csv"
    
    # Create processor instance
    processor = TweetProcessor(folder_path, output_file)
    
    # Process all files
    try:
        result_df = processor.process_all_files()
        
        if result_df is not None and not result_df.empty:
            print(f"\n✅ SUCCESS: Processed {len(result_df)} tweets")
            print(f"📁 Output file: {os.path.join(folder_path, output_file)}")
            
            # Display sample of processed data
            print("\n📋 Sample of processed data:")
            print(result_df[['source_file', 'detected_language', 'is_translated', 'tweet_text']].head())
            
        else:
            print("❌ No data was processed")
            
    except Exception as e:
        logger.error(f"Main process failed: {e}")

if __name__ == "__main__":
    main()