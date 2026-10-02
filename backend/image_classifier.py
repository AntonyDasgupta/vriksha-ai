"""
backend/image_classifier.py
===========================
Utility to load the trained PyTorch image classification model and 
predict plant disease labels from an uploaded image file.
"""

import os
import io
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "plant_disease_model.pth")

# List of class names matching your training dataset order
CLASS_NAMES = ["Healthy", "Powdery", "Rust"] 

# Map model outputs to Knowledge Base (plant, problem) pairs
CLASS_TO_CONTEXT_MAP = {
    "Healthy": {"plant": "Tomato", "problem": "Healthy"},
    "Powdery": {"plant": "Rose", "problem": "Powdery mildew"},
    "Rust": {"plant": "Tomato", "problem": "Rust"}
}

class DiseaseClassifier:
    def __init__(self, model_path=MODEL_PATH, device=None):
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.class_names = CLASS_NAMES
        self.model = self._load_model(model_path)
        
        # Standard PyTorch image preprocessing (replaces Albumentations for inference)
        self.transform = transforms.Compose([
            transforms.Resize((128, 128)),
            transforms.ToTensor(),
        ])

    def _load_model(self, model_path):
        model = models.resnet18(weights=None)
        num_ftrs = model.fc.in_features
        model.fc = nn.Linear(num_ftrs, len(self.class_names))
        
        if os.path.exists(model_path):
            model.load_state_dict(torch.load(model_path, map_location=self.device))
        
        model.to(self.device)
        model.eval()
        return model

    def predict(self, image_bytes: bytes) -> dict:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # Apply torchvision transformation
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(input_tensor)
            probabilities = torch.softmax(outputs, dim=1)
            confidence, predicted_idx = torch.max(probabilities, 1)
            
        predicted_class = self.class_names[predicted_idx.item()]
        confidence_score = float(confidence.item())
        
        context = CLASS_TO_CONTEXT_MAP.get(predicted_class, {"plant": None, "problem": None})
        
        return {
            "predicted_class": predicted_class,
            "confidence_score": confidence_score,
            "extracted_plant": context.get("plant"),
            "extracted_problem": context.get("problem")
        }

# Global singleton classifier instance
classifier = DiseaseClassifier()