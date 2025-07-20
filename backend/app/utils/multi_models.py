import os
import numpy as np
import torch
import concurrent.futures
from typing import List, Optional
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import joblib
from transformers import XLNetTokenizer, XLNetForSequenceClassification, CLIPProcessor, CLIPModel

from .text_classification import TextClassifier
from .image_classification import ImageClassifier

target_names = ['Non-Radical', 'Political', 'Radical']


def _predict_text(model_name, texts):
    model = TextClassifier(model_name=model_name)
    return model.predict(texts)


def _predict_image(model_name, images):
    model = ImageClassifier(model_name=model_name)
    return model.predict(images)


def format_results(final_probs):
    label_idx = np.argmax(final_probs)
    dominant_label = target_names[label_idx]
    overall_conf = round(final_probs[label_idx] * 100, 2)

    return {
        "classification_summary": {
            "confidence_score": float(overall_conf),
            "dominant_category": dominant_label
        },
        "overall_classification": dominant_label,
        "overall_confidence": float(overall_conf),
        "percentages": {
            "non_radical": float(round(final_probs[0] * 100, 1)),
            "political": float(round(final_probs[1] * 100, 1)),
            "radical": float(round(final_probs[2] * 100, 1))
        }
    }


def add_content_stats(result, texts=None, images=None):
    total_images = len(images) if images else 0
    total_texts = len(texts) if texts else 0
    total_content = total_images + total_texts

    result["content_stats"] = {
        "images_found": int(total_images),
        "total_content_analyzed": int(total_content),
        "total_images": int(total_images),
        "total_tweets": int(total_texts)
    }
    return result


# 1. Simple Weighted Average
def predict_multimodal(
        text_model_names=['vgg16'],
        image_model_names=['clip'],
        texts: Optional[List[str]] = None,
        images: Optional[List[str]] = None,
        alpha=0.5,
        username="user"
):
    text_output = np.zeros(3)
    image_output = np.zeros(3)

    with concurrent.futures.ProcessPoolExecutor() as executor:
        text_futures = [
            executor.submit(_predict_text, name, texts)
            for name in text_model_names
        ]
        for future in concurrent.futures.as_completed(text_futures):
            text_output += future.result()
        image_futures = [
            executor.submit(_predict_image, name, images)
            for name in image_model_names
        ]
        for future in concurrent.futures.as_completed(image_futures):
            image_output += future.result()

    text_probs = text_output / len(text_model_names)
    image_probs = image_output / len(image_model_names)

    final_probs = alpha * text_probs + (1 - alpha) * image_probs

    result = format_results(final_probs)
    return add_content_stats(result, texts, images)


# 2. Feature-Level Fusion
class FeatureFusionModel:
    def __init__(self, model_path="fusion_model.pkl"):
        self.base_path = os.path.dirname(__file__)
        self.model_path = os.path.join(self.base_path, model_path)
        self.model = self._load_model() if os.path.exists(self.model_path) else None
        self.feature_scaler = self._load_scaler() if os.path.exists(
            self.base_path + "/feature_scaler.pkl") else StandardScaler()

    def _load_model(self):
        try:
            return joblib.load(self.model_path)
        except:
            # Fallback model if saved one doesn't exist
            return LogisticRegression(max_iter=1000)

    def _load_scaler(self):
        try:
            return joblib.load(self.base_path + "/feature_scaler.pkl")
        except:
            return StandardScaler()

    def predict(self, features):
        if self.model is None:
            # Fallback to softmax if no model exists
            exp_scores = np.exp(features)
            return exp_scores / np.sum(exp_scores, axis=1, keepdims=True)

        scaled_features = self.feature_scaler.transform(features)
        return self.model.predict_proba(scaled_features)


def predict_multimodal_feature_fusion(
        text_model_names=['xlnet', 'bert'],
        image_model_names=['vgg16', 'clip'],
        texts: Optional[List[str]] = None,
        images: Optional[List[str]] = None,
        username="user"
):
    text_features = np.zeros((1, 768 * len(text_model_names))) if texts else np.zeros((1, 768 * len(text_model_names)))
    image_features = np.zeros((1, 512 * len(image_model_names))) if images else np.zeros(
        (1, 512 * len(image_model_names)))

    text_preds = np.zeros(3)
    image_preds = np.zeros(3)

    with concurrent.futures.ProcessPoolExecutor() as executor:
        if texts:
            text_futures = [
                executor.submit(_predict_text, name, texts)
                for name in text_model_names
            ]
            for future in concurrent.futures.as_completed(text_futures):
                text_preds += future.result()

        if images:
            image_futures = [
                executor.submit(_predict_image, name, images)
                for name in image_model_names
            ]
            for future in concurrent.futures.as_completed(image_futures):
                image_preds += future.result()

    if texts:
        text_preds = text_preds / len(text_model_names)
    if images:
        image_preds = image_preds / len(image_model_names)

    combined_features = np.concatenate([
        text_preds.reshape(1, -1) if texts else np.zeros((1, 3)),
        image_preds.reshape(1, -1) if images else np.zeros((1, 3))
    ], axis=1)

    fusion_model = FeatureFusionModel()
    final_probs = fusion_model.predict(combined_features)[0]

    result = format_results(final_probs)
    return add_content_stats(result, texts, images)


# 3. Attention-Based Fusion
class AttentionFusionModel:
    def __init__(self, input_dim=6):
        self.attention_weights = np.array([0.6, 0.4])  # Default: text weight, image weight

    def calculate_attention(self, text_confidence, image_confidence):
        text_conf = np.max(text_confidence)
        image_conf = np.max(image_confidence)

        total_conf = text_conf + image_conf
        if total_conf > 0:
            text_weight = text_conf / total_conf
            image_weight = image_conf / total_conf
        else:
            text_weight = 0.5
            image_weight = 0.5

        return np.array([text_weight, image_weight])


def predict_multimodal_attention(
        text_model_names=['xlnet', 'bert'],
        image_model_names=['vgg16', 'clip'],
        texts: Optional[List[str]] = None,
        images: Optional[List[str]] = None,
        username="user"
):
    text_output = np.zeros(3)
    image_output = np.zeros(3)

    with concurrent.futures.ProcessPoolExecutor() as executor:
        text_futures = []
        if texts:
            text_futures = [
                executor.submit(_predict_text, name, texts)
                for name in text_model_names
            ]

        image_futures = []
        if images:
            image_futures = [
                executor.submit(_predict_image, name, images)
                for name in image_model_names
            ]
        for future in concurrent.futures.as_completed(text_futures):
            text_output += future.result()

        for future in concurrent.futures.as_completed(image_futures):
            image_output += future.result()

    text_probs = text_output / max(1, len(text_model_names))
    image_probs = image_output / max(1, len(image_model_names))

    attention_model = AttentionFusionModel()

    if texts is None or len(texts) == 0:
        attention_weights = np.array([0, 1])
    elif images is None or len(images) == 0:
        attention_weights = np.array([1, 0])
    else:
        attention_weights = attention_model.calculate_attention(text_probs, image_probs)

    final_probs = attention_weights[0] * text_probs + attention_weights[1] * image_probs

    result = format_results(final_probs)
    result["modality_weights"] = {
        "text_weight": float(attention_weights[0]),
        "image_weight": float(attention_weights[1])
    }

    return add_content_stats(result, texts, images)


# 4. Model Stacking
class MetaClassifier:
    def __init__(self, model_path="meta_classifier.pkl"):
        self.base_path = os.path.dirname(__file__)
        self.model_path = os.path.join(self.base_path, model_path)

        try:
            self.model = joblib.load(self.model_path)
            self.using_pretrained = True
        except:
            self.model = None
            self.using_pretrained = False

    def predict(self, features):
        if self.model is None or not self.using_pretrained:
            num_models = features.shape[1] // 3
            reshaped = features.reshape(-1, num_models, 3)
            return np.mean(reshaped, axis=1)

        return self.model.predict_proba(features)


def predict_multimodal_stacking(
        text_model_names=['xlnet', 'bert'],
        image_model_names=['vgg16', 'clip'],
        texts: Optional[List[str]] = None,
        images: Optional[List[str]] = None,
        username="user"
):
    all_model_outputs = []

    with concurrent.futures.ProcessPoolExecutor() as executor:
        text_futures = []
        if texts:
            text_futures = [
                executor.submit(_predict_text, name, texts)
                for name in text_model_names
            ]

        image_futures = []
        if images:
            image_futures = [
                executor.submit(_predict_image, name, images)
                for name in image_model_names
            ]

        for future in concurrent.futures.as_completed(text_futures):
            all_model_outputs.append(future.result())

        for future in concurrent.futures.as_completed(image_futures):
            all_model_outputs.append(future.result())

    if not all_model_outputs:
        default_probs = np.array([0.33, 0.33, 0.34])  # Default to balanced probabilities
        result = format_results(default_probs)
        return add_content_stats(result, texts, images)

    meta_features = np.hstack([output.reshape(1, -1) for output in all_model_outputs])

    meta_clf = MetaClassifier()
    final_probs = meta_clf.predict(meta_features)[0]

    result = format_results(final_probs)
    return add_content_stats(result, texts, images)


# 5. Late Fusion with Learned Weights
class LearnedWeightsFusionModel:
    def __init__(self, model_path="fusion_weights.pkl"):
        self.base_path = os.path.dirname(__file__)
        self.model_path = os.path.join(self.base_path, model_path)

        self.text_weight = 0.5
        self.image_weight = 0.5
        self.bias = np.zeros(3)

        try:
            weights = joblib.load(self.model_path)
            self.text_weight = weights['text_weight']
            self.image_weight = weights['image_weight']
            self.bias = weights.get('bias', np.zeros(3))
        except:
            pass

    def predict(self, text_preds, image_preds):
        return self.text_weight * text_preds + self.image_weight * image_preds + self.bias


def predict_multimodal_learned_weights(
        text_model_names=['xlnet', 'bert'],
        image_model_names=['vgg16', 'clip'],
        texts: Optional[List[str]] = None,
        images: Optional[List[str]] = None,
        username="user"
):
    text_output = np.zeros(3)
    image_output = np.zeros(3)

    with concurrent.futures.ProcessPoolExecutor() as executor:
        text_futures = []
        if texts:
            text_futures = [
                executor.submit(_predict_text, name, texts)
                for name in text_model_names
            ]

        image_futures = []
        if images:
            image_futures = [
                executor.submit(_predict_image, name, images)
                for name in image_model_names
            ]

        for future in concurrent.futures.as_completed(text_futures):
            text_output += future.result()

        for future in concurrent.futures.as_completed(image_futures):
            image_output += future.result()

    text_probs = text_output / max(1, len(text_model_names))
    image_probs = image_output / max(1, len(image_model_names))

    if texts is None or len(texts) == 0:
        text_probs = np.zeros(3)
    if images is None or len(images) == 0:
        image_probs = np.zeros(3)

    fusion_model = LearnedWeightsFusionModel()
    final_probs = fusion_model.predict(text_probs, image_probs)

    if np.sum(final_probs) <= 0:
        final_probs = np.array([0.33, 0.33, 0.34])
    else:
        final_probs = final_probs / np.sum(final_probs)

    result = format_results(final_probs)
    result["fusion_weights"] = {
        "text_weight": float(fusion_model.text_weight),
        "image_weight": float(fusion_model.image_weight)
    }

    return add_content_stats(result, texts, images)


def multimodal_predict(
        texts: Optional[List[str]] = None,
        images: Optional[List[str]] = None,
        text_models: List[str] = ['xlnet', 'bert'],
        image_models: List[str] = ['vgg16', 'clip'],
        fusion_technique: str = 'weighted_average',
        alpha: float = 0.5,  # Only used for weighted_average
        username: str = "user"
):
    if not texts and not images:
        return {
            "error": "No input provided. Please provide at least text or images.",
            "classification_summary": {
                "confidence_score": 0.0,
                "dominant_category": "Non-Radical"
            }
        }

    if fusion_technique == 'weighted_average':
        return predict_multimodal(
            text_model_names=text_models,
            image_model_names=image_models,
            texts=texts,
            images=images,
            alpha=alpha,
            username=username
        )
    elif fusion_technique == 'feature_fusion':
        return predict_multimodal_feature_fusion(
            text_model_names=text_models,
            image_model_names=image_models,
            texts=texts,
            images=images,
            username=username
        )
    elif fusion_technique == 'attention':
        return predict_multimodal_attention(
            text_model_names=text_models,
            image_model_names=image_models,
            texts=texts,
            images=images,
            username=username
        )
    elif fusion_technique == 'stacking':
        return predict_multimodal_stacking(
            text_model_names=text_models,
            image_model_names=image_models,
            texts=texts,
            images=images,
            username=username
        )
    elif fusion_technique == 'learned_weights':
        return predict_multimodal_learned_weights(
            text_model_names=text_models,
            image_model_names=image_models,
            texts=texts,
            images=images,
            username=username
        )
    else:
        # Default to weighted average if invalid technique specified
        return predict_multimodal(
            text_model_names=text_models,
            image_model_names=image_models,
            texts=texts,
            images=images,
            alpha=alpha,
            username=username
        )