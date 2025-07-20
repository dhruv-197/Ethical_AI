import os
import cv2
import numpy as np
from PIL import Image
import glob
import shutil
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self, source_folder="posts", target_folder="politician", target_size=(256, 256)):
        self.source_folder = source_folder
        self.target_folder = target_folder
        self.target_size = target_size
        self.processed_count = 0
        self.error_count = 0
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
        
        # Create target folder if it doesn't exist
        Path(self.target_folder).mkdir(parents=True, exist_ok=True)
        
    def resize_image(self, image_path, output_path):
        """
        Resize image to target size while maintaining aspect ratio
        """
        try:
            # Open image using PIL
            with Image.open(image_path) as img:
                # Convert to RGB if necessary (for PNG with transparency, etc.)
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize image maintaining aspect ratio
                img.thumbnail(self.target_size, Image.Resampling.LANCZOS)
                
                # Create new image with target size and paste resized image in center
                new_img = Image.new('RGB', self.target_size, (255, 255, 255))
                
                # Calculate position to center the image
                x_offset = (self.target_size[0] - img.size[0]) // 2
                y_offset = (self.target_size[1] - img.size[1]) // 2
                
                new_img.paste(img, (x_offset, y_offset))
                
                # Save the resized image
                new_img.save(output_path, 'JPEG', quality=95)
                
                return True
                
        except Exception as e:
            logger.error(f"Error resizing {image_path}: {e}")
            return False
    
    def resize_image_opencv(self, image_path, output_path):
        """
        Alternative resize method using OpenCV (more robust for some formats)
        """
        try:
            # Read image using OpenCV
            img = cv2.imread(image_path)
            
            if img is None:
                logger.error(f"Could not read image: {image_path}")
                return False
            
            # Get original dimensions
            height, width = img.shape[:2]
            
            # Calculate scaling to fit within target size while maintaining aspect ratio
            scale = min(self.target_size[0] / width, self.target_size[1] / height)
            
            # Calculate new dimensions
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            # Resize image
            resized = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
            
            # Create new image with target size and white background
            new_img = np.ones((self.target_size[1], self.target_size[0], 3), dtype=np.uint8) * 255
            
            # Calculate position to center the resized image
            x_offset = (self.target_size[0] - new_width) // 2
            y_offset = (self.target_size[1] - new_height) // 2
            
            # Place resized image in center
            new_img[y_offset:y_offset + new_height, x_offset:x_offset + new_width] = resized
            
            # Save the image
            cv2.imwrite(output_path, new_img)
            
            return True
            
        except Exception as e:
            logger.error(f"Error resizing {image_path} with OpenCV: {e}")
            return False
    
    def get_image_files(self):
        """
        Get all image files from source folder
        """
        image_files = []
        
        for ext in self.supported_formats:
            pattern = os.path.join(self.source_folder, f"**/*{ext}")
            image_files.extend(glob.glob(pattern, recursive=True))
            # Also check uppercase extensions
            pattern = os.path.join(self.source_folder, f"**/*{ext.upper()}")
            image_files.extend(glob.glob(pattern, recursive=True))
        
        return image_files
    
    def process_all_images(self):
        """
        Process all images in the source folder
        """
        logger.info(f"Starting image processing...")
        logger.info(f"Source folder: {os.path.abspath(self.source_folder)}")
        logger.info(f"Target folder: {os.path.abspath(self.target_folder)}")
        logger.info(f"Target size: {self.target_size}")
        
        # Get all image files
        image_files = self.get_image_files()
        
        if not image_files:
            logger.warning(f"No image files found in {self.source_folder}")
            return
        
        logger.info(f"Found {len(image_files)} image files")
        
        # Process each image
        for index, image_path in enumerate(image_files, 1):
            try:
                # Generate new filename
                new_filename = f"politician_{index:04d}.jpg"
                output_path = os.path.join(self.target_folder, new_filename)
                
                logger.info(f"Processing {index}/{len(image_files)}: {os.path.basename(image_path)}")
                
                # Try PIL first, then OpenCV if PIL fails
                success = self.resize_image(image_path, output_path)
                
                if not success:
                    logger.info(f"PIL failed, trying OpenCV for: {image_path}")
                    success = self.resize_image_opencv(image_path, output_path)
                
                if success:
                    self.processed_count += 1
                    logger.info(f"✅ Processed: {new_filename}")
                else:
                    self.error_count += 1
                    logger.error(f"❌ Failed to process: {image_path}")
                
            except Exception as e:
                self.error_count += 1
                logger.error(f"❌ Error processing {image_path}: {e}")
        
        # Summary
        logger.info(f"\n📊 PROCESSING SUMMARY:")
        logger.info(f"Total images found: {len(image_files)}")
        logger.info(f"Successfully processed: {self.processed_count}")
        logger.info(f"Failed to process: {self.error_count}")
        logger.info(f"Output folder: {os.path.abspath(self.target_folder)}")
        
        if self.processed_count > 0:
            logger.info(f"✅ Processing completed successfully!")
        else:
            logger.warning(f"⚠️ No images were processed successfully")

def main():
    """
    Main function to run the image processor
    """
    # Configuration
    source_folder = "/home/bacancy/Development/DataScience/X_seniment_analyis/posts"
    target_folder = "/home/bacancy/Development/DataScience/X_seniment_analyis/politician"
    target_size = (256, 256)
    
    # Create processor instance
    processor = ImageProcessor(source_folder, target_folder, target_size)
    
    # Process all images
    try:
        processor.process_all_images()
        
    except Exception as e:
        logger.error(f"Main process failed: {e}")

if __name__ == "__main__":
    main()