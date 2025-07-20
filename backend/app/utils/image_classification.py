from transformers import XLNetTokenizer, XLNetForSequenceClassification
from keras.models import load_model
from keras.preprocessing import image as keras_image
import torch
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
from dotenv import load_dotenv
import re
import string
from typing import List, Optional
from .models import ImageModels
import torch.nn.functional as F

load_dotenv(override=True)


class ImageClassifier:
    def __init__(self, model_name: str = "vgg16"):
        self.model_name = model_name
        self.image_models = ImageModels()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        if model_name == "vgg16":
            self.model = self.image_models.vgg16_image_model
        elif model_name == "clip":
            self.model = self.image_models.clip_model
            self.processor = self.image_models.clip_model_processor
        else:
            raise ValueError(f"Unsupported model: {model_name}")

    def preprocess_image(self,image_path):
        """Preprocess image for model input"""
        try:
            img = keras_image.load_img(image_path, target_size=(224, 224))
            img_array = keras_image.img_to_array(img)
            img_array = img_array / 255.0  # Normalize
            return np.expand_dims(img_array, axis=0)
        except Exception as e:
            logger.error(f"Image preprocessing error: {e}")
            raise e

    def predict(self,images: List[str]) -> np.ndarray:
        if not images:
            return np.array([1 / 3, 1 / 3, 1 / 3])  # Neutral
        probs_list = []
        if self.model_name == 'vgg16':
            for img_path in images:
                # For VGG16, we use the Keras model directly
                img_array = self.preprocess_image(img_path)
                preds = self.model.predict(img_array)
                probs_list.append(preds.squeeze())
        elif self.model_name == 'clip':
            for img_path in images:
                image = Image.open(img_path).convert('RGB')
                text_labels = [
                    "an image showing non-radical, moderate, or neutral content, sports person, athletes, normal people, families, nature, landscapes, animals, food, entertainment, celebrities, art, music, technology, science, education, business, fashion, travel",
                    "an image showing political content, government, elections, politician, political figures, voting, campaigns, political rallies, government buildings, flags, political parties, political debates, political meetings, political speeches",
                    "an image showing radical content, terrorism, extremism, violent protests, revolutionary symbols, anarchist symbols, hate symbols, armed conflicts, radical propaganda",
                ]
                inputs = self.processor(text=text_labels, images=image, return_tensors="pt", padding=True)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    logits_per_image = outputs.logits_per_image
                    probs = F.softmax(logits_per_image, dim=-1)
                probs_list.append(probs[0])
        return np.mean(probs_list, axis=0)



