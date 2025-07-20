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
from .models import  TextModels
load_dotenv(override=True)

class TextClassifier:
    def __init__(self, model_name: str = "xlnet"):
        self.model_name = model_name
        self.text_models = TextModels()
        if model_name == "xlnet":
            self.tokenizer = self.text_models.xlnet_text_tokenizer
            self.model = self.text_models.xlnet_text_model
        elif model_name == "bert":
            self.tokenizer = self.text_models.bert_text_tokenizer
            self.model = self.text_models.bert_text_model
        else:
            raise ValueError(f"Unsupported model: {model_name}")

    def preprocess_text(self,text):
        # Lowercase
        text = text.lower()
        # Remove URLs
        text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        # Remove numbers
        text = re.sub(r'\d+', '', text)
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def predict(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.array([1 / 3, 1 / 3, 1 / 3])  # Neutral

        probs_list = []
        for text in texts:
            text = self.preprocess_text(text)
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
            with torch.no_grad():
                outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=1).squeeze().numpy()
            probs_list.append(probs)

        return np.mean(probs_list, axis=0)





