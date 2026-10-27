import os
import numpy as np
from PIL import Image
import torch
import torch.nn as nn
from torchvision import transforms, models
from sklearn.metrics import confusion_matrix, classification_report
import matplotlib.pyplot as plt


# =========================
# SETTINGS
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data", "Classification")
IMAGE_DIR = os.path.join(DATA_DIR, "JPEGImages")
TEST_FILE = os.path.join(DATA_DIR, "NNEW_test_0.txt")
MODEL_PATH = os.path.join(BASE_DIR, "models", "acne_ldl_resnet50_best.pth")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

os.makedirs(OUTPUT_DIR, exist_ok=True)

DEVICE = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

NUM_CLASSES = 4
NUM_COUNT_CLASSES = 65


# =========================
# MODEL
# =========================
class AcneLDLResNet50(nn.Module):
    def __init__(self):
        super().__init__()

        backbone = models.resnet50(
            weights=None
        )

        features = backbone.fc.in_features
        backbone.fc = nn.Identity()

        self.backbone = backbone

        self.fc = nn.Linear(features, NUM_CLASSES)
        self.counting = nn.Linear(features, NUM_COUNT_CLASSES)

    def forward(self, x):
        x = self.backbone(x)

        cls_logits = self.fc(x)
        count_logits = self.counting(x)

        cls = torch.softmax(cls_logits, dim=1)
        count = torch.softmax(count_logits, dim=1)

        count_to_class = torch.stack(
            (
                torch.sum(count[:, :5], dim=1),
                torch.sum(count[:, 5:20], dim=1),
                torch.sum(count[:, 20:50], dim=1),
                torch.sum(count[:, 50:], dim=1),
            ),
            dim=1,
        )

        return cls, count, count_to_class


# =========================
# DATA
# =========================
class AcneTestDataset(torch.utils.data.Dataset):
    def __init__(self, test_file, image_dir):
        self.image_dir = image_dir
        self.samples = []

        with open(test_file, "r") as f:
            for line in f:
                parts = line.strip().split()

                if len(parts) >= 3:
                    filename = parts[0]
                    label = int(parts[1])
                    lesion = int(parts[2])

                    self.samples.append(
                        (filename, label, lesion)
                    )

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.45815152, 0.361242, 0.29348266],
                std=[0.2814769, 0.226306, 0.20132513]
            )
        ])

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        filename, label, lesion = self.samples[index]

        image_path = os.path.join(
            self.image_dir,
            filename
        )

        image = Image.open(image_path).convert("RGB")
        image = self.transform(image)

        return image, label, filename


# =========================
# LOAD MODEL
# =========================
print()
print("==========================================")
print("ACNE04 BEST MODEL EVALUATION")
print("==========================================")
print("Device:", DEVICE)
print("Model:", MODEL_PATH)

model = AcneLDLResNet50()

checkpoint = torch.load(
    MODEL_PATH,
    map_location=DEVICE
)

if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
    model.load_state_dict(checkpoint["model_state_dict"])
else:
    model.load_state_dict(checkpoint)

model.to(DEVICE)
model.eval()

print("Best model loaded successfully.")


# =========================
# LOAD TEST DATA
# =========================
dataset = AcneTestDataset(
    TEST_FILE,
    IMAGE_DIR
)

loader = torch.utils.data.DataLoader(
    dataset,
    batch_size=16,
    shuffle=False,
    num_workers=0
)

print("Testing images:", len(dataset))


# =========================
# EVALUATION
# =========================
all_labels = []
all_predictions = []
all_confidences = []

with torch.no_grad():

    for images, labels, filenames in loader:

        images = images.to(DEVICE)

        cls, count, count_to_class = model(images)

        # Same combined prediction idea used during training
        combined = cls + count_to_class

        predictions = torch.argmax(
            combined,
            dim=1
        )

        confidence = torch.max(
            combined,
            dim=1
        ).values

        all_labels.extend(
            labels.numpy().tolist()
        )

        all_predictions.extend(
            predictions.cpu().numpy().tolist()
        )

        all_confidences.extend(
            confidence.cpu().numpy().tolist()
        )


# =========================
# METRICS
# =========================
labels_np = np.array(all_labels)
predictions_np = np.array(all_predictions)
confidence_np = np.array(all_confidences)

accuracy = (
    np.mean(labels_np == predictions_np) * 100
)

print()
print("==========================================")
print(f"TEST ACCURACY: {accuracy:.2f}%")
print("==========================================")

print()
print("CLASSIFICATION REPORT")
print("------------------------------------------")

report = classification_report(
    labels_np,
    predictions_np,
    target_names=[
        "Level 0",
        "Level 1",
        "Level 2",
        "Level 3"
    ],
    digits=4,
    zero_division=0
)

print(report)


# =========================
# CONFUSION MATRIX
# =========================
cm = confusion_matrix(
    labels_np,
    predictions_np,
    labels=[0, 1, 2, 3]
)

print("CONFUSION MATRIX")
print("------------------------------------------")
print(cm)


# =========================
# SAVE RESULTS
# =========================
results_path = os.path.join(
    OUTPUT_DIR,
    "best_model_results.txt"
)

with open(results_path, "w") as f:

    f.write("ACNE04 BEST MODEL EVALUATION\n")
    f.write("============================\n\n")

    f.write(f"Device: {DEVICE}\n")
    f.write("Model: acne_ldl_resnet50_best.pth\n")
    f.write(f"Testing Images: {len(dataset)}\n")
    f.write(f"Test Accuracy: {accuracy:.2f}%\n\n")

    f.write("Classification Report\n")
    f.write("---------------------\n")
    f.write(report)

    f.write("\nConfusion Matrix\n")
    f.write("----------------\n")
    f.write(str(cm))

    f.write("\n\nNote:\n")
    f.write(
        "This evaluation uses the saved best checkpoint "
        "acne_ldl_resnet50_best.pth.\n"
    )

print()
print("Results saved to:")
print(results_path)


# =========================
# CONFUSION MATRIX IMAGE
# =========================
plt.figure(figsize=(7, 6))

plt.imshow(
    cm,
    interpolation="nearest",
    cmap="Blues"
)

plt.title("Confusion Matrix - Best ACNE04 Model")
plt.xlabel("Predicted Class")
plt.ylabel("True Class")

plt.xticks(
    range(4),
    ["Level 0", "Level 1", "Level 2", "Level 3"]
)

plt.yticks(
    range(4),
    ["Level 0", "Level 1", "Level 2", "Level 3"]
)

threshold = cm.max() / 2

for i in range(4):
    for j in range(4):

        plt.text(
            j,
            i,
            str(cm[i, j]),
            ha="center",
            va="center",
            color="white" if cm[i, j] > threshold else "black"
        )

plt.colorbar()
plt.tight_layout()

cm_path = os.path.join(
    OUTPUT_DIR,
    "best_model_confusion_matrix.png"
)

plt.savefig(
    cm_path,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("Confusion matrix saved to:")
print(cm_path)


# =========================
# CONFIDENCE BOX PLOT
# =========================
confidence_by_class = []

for class_id in range(NUM_CLASSES):

    values = confidence_np[
        labels_np == class_id
    ]

    confidence_by_class.append(values)


plt.figure(figsize=(8, 6))

plt.boxplot(
    confidence_by_class,
    tick_labels=[
        "Level 0",
        "Level 1",
        "Level 2",
        "Level 3"
    ]
)

plt.title("Prediction Confidence by Acne Severity Level")
plt.xlabel("True Acne Level")
plt.ylabel("Prediction Confidence")

plt.grid(
    axis="y",
    alpha=0.3
)

plt.tight_layout()

boxplot_path = os.path.join(
    OUTPUT_DIR,
    "confidence_boxplot.png"
)

plt.savefig(
    boxplot_path,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("Box plot saved to:")
print(boxplot_path)

print()
print("==========================================")
print("EVALUATION COMPLETE")
print("==========================================")
