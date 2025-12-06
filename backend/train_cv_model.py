import os
import random
import shutil
import torch
from torch import nn, optim
from torchvision import models, transforms, datasets
from torch.utils.data import DataLoader

# -----------------------------
# 1️⃣ Paths
# -----------------------------
raw_data_dir = "dataset"              # Your original dataset folder
dataset_split_dir = "dataset_split"   # Folder to store train/val split
train_dir = os.path.join(dataset_split_dir, "train")
val_dir = os.path.join(dataset_split_dir, "val")
os.makedirs(train_dir, exist_ok=True)
os.makedirs(val_dir, exist_ok=True)

# -----------------------------
# 2️⃣ Split Dataset (80% train, 20% val)
# -----------------------------
split_ratio = 0.8

for category in os.listdir(raw_data_dir):
    cat_path = os.path.join(raw_data_dir, category)
    if not os.path.isdir(cat_path):
        continue
    
    images = os.listdir(cat_path)
    random.shuffle(images)
    split_idx = int(len(images) * split_ratio)
    
    train_images = images[:split_idx]
    val_images = images[split_idx:]
    
    os.makedirs(os.path.join(train_dir, category), exist_ok=True)
    os.makedirs(os.path.join(val_dir, category), exist_ok=True)
    
    for img in train_images:
        shutil.copy(os.path.join(cat_path, img), os.path.join(train_dir, category, img))
    for img in val_images:
        shutil.copy(os.path.join(cat_path, img), os.path.join(val_dir, category, img))

print("✅ Dataset split completed!")

# -----------------------------
# 3️⃣ Transformations
# -----------------------------
train_transforms = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.ToTensor(),
])

val_transforms = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
])

# -----------------------------
# 4️⃣ Datasets & DataLoaders
# -----------------------------
train_dataset = datasets.ImageFolder(train_dir, transform=train_transforms)
train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)

val_dataset = datasets.ImageFolder(val_dir, transform=val_transforms)
val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)

print(f"Classes: {train_dataset.classes}")

# -----------------------------
# 5️⃣ Model Setup (ResNet18)
# -----------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = models.resnet18(pretrained=True)
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, len(train_dataset.classes))
model = model.to(device)

# -----------------------------
# 6️⃣ Loss & Optimizer
# -----------------------------
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=1e-4)

# -----------------------------
# 7️⃣ Training Loop
# -----------------------------
epochs = 10
for epoch in range(epochs):
    model.train()
    running_loss = 0
    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()
    
    avg_loss = running_loss / len(train_loader)
    print(f"Epoch {epoch+1}/{epochs} | Train Loss: {avg_loss:.4f}")

    # Validation
    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, preds = torch.max(outputs, 1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)
    val_acc = correct / total
    print(f"Validation Accuracy: {val_acc:.4f}")

# -----------------------------
# 8️⃣ Save Trained Model
# -----------------------------
os.makedirs("models", exist_ok=True)
torch.save(model.state_dict(), "models/banana_deficiency_model.pth")
print("✅ Model training complete and saved to models/banana_deficiency_model.pth")
