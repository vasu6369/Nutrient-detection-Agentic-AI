# agent/tools/cv_tool.py
from __future__ import annotations

import torch
from torchvision import models, transforms
from PIL import Image


class CVTool:
    """
    Wraps the trained PyTorch model for leaf deficiency classification.
    """

    def __init__(self, model_path="models/banana_deficiency_model.pth", class_names=None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        checkpoint = torch.load(model_path, map_location=self.device)

        num_classes = checkpoint['fc.weight'].size(0)
        if class_names is None:
            class_names = [f"Class_{i}" for i in range(num_classes)]
        self.class_names = class_names

        self.model = models.resnet18(pretrained=False)
        num_ftrs = self.model.fc.in_features
        self.model.fc = torch.nn.Linear(num_ftrs, num_classes)
        self.model.load_state_dict(checkpoint)
        self.model.to(self.device)
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ])

    def run(self, image_path: str) -> dict:
        img = Image.open(image_path).convert("RGB") 
        tensor = self.transform(img).unsqueeze(0).to(self.device)
    
        with torch.no_grad():
            outputs = self.model(tensor)
            probs = torch.nn.functional.softmax(outputs, dim=1)
            conf, pred = torch.max(probs, 1)
    
        result = {
            "deficiency": self.class_names[pred.item()],
            "confidence": float(conf.item())
        }
        print("CV:", result)
        return result
