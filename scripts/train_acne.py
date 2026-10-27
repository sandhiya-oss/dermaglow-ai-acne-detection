import os
import sys
import math
import random
import numpy as np
from PIL import Image

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from torchvision.models import resnet50, ResNet50_Weights

from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    classification_report,
    precision_recall_fscore_support
)

import matplotlib.pyplot as plt


# ============================================================
# ACNE04 - LABEL DISTRIBUTION LEARNING
# Corrected Mac/MPS implementation
# ============================================================

SEED = 42
EPOCHS = 120
BATCH_SIZE = 16
LR = 0.001
MOMENTUM = 0.9
WEIGHT_DECAY = 5e-4

NUM_CLASSES = 4
COUNT_CLASSES = 65

SIGMA = 3.0
LAM = 0.6

NUM_WORKERS = 0

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(
    ROOT,
    "data",
    "Classification"
)

IMAGE_DIR = os.path.join(
    DATA_DIR,
    "JPEGImages"
)

OUTPUT_DIR = os.path.join(
    ROOT,
    "outputs"
)

MODEL_DIR = os.path.join(
    ROOT,
    "models"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)


# ============================================================
# REPRODUCIBILITY
# ============================================================

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)


# ============================================================
# DEVICE
# ============================================================

if torch.backends.mps.is_available():
    DEVICE = torch.device("mps")
elif torch.cuda.is_available():
    DEVICE = torch.device("cuda")
else:
    DEVICE = torch.device("cpu")


print("=" * 70)
print("ACNE DETECTION - ACNE04 LABEL DISTRIBUTION LEARNING")
print("=" * 70)
print("Device       :", DEVICE)
print("Epochs       :", EPOCHS)
print("Batch size   :", BATCH_SIZE)
print("Learning rate:", LR)
print("=" * 70)


# ============================================================
# DATASET
# ============================================================

class AcneDataset(Dataset):

    def __init__(self, annotation_file, transform=None):

        self.transform = transform
        self.images = []
        self.labels = []
        self.lesions = []

        with open(annotation_file, "r") as f:

            for line in f:

                line = line.strip()

                if not line:
                    continue

                parts = line.split()

                if len(parts) < 3:
                    continue

                filename = parts[0]
                label = int(parts[1])
                lesion = int(parts[2])

                self.images.append(filename)
                self.labels.append(label)
                self.lesions.append(lesion)

    def __len__(self):
        return len(self.images)

    def __getitem__(self, index):

        filename = self.images[index]

        image_path = os.path.join(
            IMAGE_DIR,
            filename
        )

        image = Image.open(image_path).convert("RGB")

        label = self.labels[index]
        lesion = self.lesions[index]

        if self.transform:
            image = self.transform(image)

        return (
            image,
            torch.tensor(label, dtype=torch.long),
            torch.tensor(lesion, dtype=torch.long)
        )


# ============================================================
# TRANSFORMS
# ============================================================

MEAN = [
    0.45815152,
    0.36124200,
    0.29348266
]

STD = [
    0.28147690,
    0.22630600,
    0.20132513
]


train_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.RandomCrop(224),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(20),
    transforms.ToTensor(),
    transforms.Normalize(MEAN, STD)
])


test_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(MEAN, STD)
])


# ============================================================
# LABEL DISTRIBUTION
# ============================================================

def generate_label_distribution(labels, sigma=3.0):

    labels = np.asarray(labels)

    class_values = np.arange(COUNT_CLASSES)

    distributions = []

    for label in labels:

        difference = class_values - label

        distribution = (
            1.0 /
            (math.sqrt(2.0 * math.pi) * sigma)
            *
            np.exp(
                -1.0 *
                np.power(difference, 2)
                /
                (2.0 * np.power(sigma, 2))
            )
        )

        distribution = distribution / np.sum(distribution)

        distributions.append(distribution)

    return np.asarray(distributions, dtype=np.float32)


# ============================================================
# 65 COUNT DISTRIBUTION -> 4 ACNE CLASSES
# ============================================================

def count_distribution_to_four_classes(distribution):

    class_0 = np.sum(distribution[:, :5], axis=1)

    class_1 = np.sum(distribution[:, 5:20], axis=1)

    class_2 = np.sum(distribution[:, 20:50], axis=1)

    class_3 = np.sum(distribution[:, 50:], axis=1)

    return np.vstack(
        (
            class_0,
            class_1,
            class_2,
            class_3
        )
    ).transpose().astype(np.float32)


# ============================================================
# MODEL
# ============================================================

class AcneLDLResNet50(nn.Module):

    def __init__(self):

        super().__init__()

        print("\nCreating ResNet50...")

        # Load ImageNet pretrained ResNet50.
        #
        # If the Mac SSL problem is fixed, this downloads once
        # and is cached locally.
        #
        # If the weights are already cached, no download occurs.

        backbone = resnet50(
            weights=ResNet50_Weights.DEFAULT
        )

        feature_size = backbone.fc.in_features

        # Remove original ImageNet classifier
        backbone.fc = nn.Identity()

        self.backbone = backbone

        # 4-class acne severity classifier
        self.fc = nn.Linear(
            feature_size,
            NUM_CLASSES
        )

        # 65-class lesion counting branch
        self.counting = nn.Linear(
            feature_size,
            COUNT_CLASSES
        )

        # Initialize new layers
        nn.init.normal_(
            self.fc.weight,
            mean=0.0,
            std=0.01
        )

        nn.init.constant_(
            self.fc.bias,
            0.0
        )

        nn.init.normal_(
            self.counting.weight,
            mean=0.0,
            std=0.01
        )

        nn.init.constant_(
            self.counting.bias,
            0.0
        )

    def forward(self, x):

        features = self.backbone(x)

        cls_logits = self.fc(features)

        count_logits = self.counting(features)

        cls = F.softmax(
            cls_logits,
            dim=1
        ) + 1e-4

        count = F.softmax(
            count_logits,
            dim=1
        ) + 1e-4

        # Convert 65 lesion-count probabilities
        # into 4 acne severity probabilities.

        count_to_class = torch.stack(
            (
                torch.sum(count[:, :5], dim=1),
                torch.sum(count[:, 5:20], dim=1),
                torch.sum(count[:, 20:50], dim=1),
                torch.sum(count[:, 50:], dim=1)
            ),
            dim=1
        )

        return cls, count, count_to_class


# ============================================================
# KL LOSS
# ============================================================

def distribution_kl_loss(
    predicted_probability,
    target_distribution,
    lad=0
):

    predicted_probability = torch.clamp(
        predicted_probability,
        min=1e-8
    )

    kl_values = F.kl_div(
        torch.log(predicted_probability),
        target_distribution,
        reduction="none"
    )

    kl_values = torch.sum(
        kl_values,
        dim=1
    )

    maximum_target = torch.max(
        target_distribution,
        dim=1
    ).values

    weights = (
        1.0 +
        torch.pow(
            1.0 - maximum_target,
            lad
        )
    )

    return torch.mean(
        kl_values * weights
    )


# ============================================================
# LEARNING RATE
# ============================================================

def adjust_learning_rate(
    optimizer,
    epoch
):

    # Original implementation changes LR
    # at epochs 30, 60, 90, 120.

    lr = LR

    if epoch >= 90:
        lr = LR * 0.001
    elif epoch >= 60:
        lr = LR * 0.01
    elif epoch >= 30:
        lr = LR * 0.1

    for param_group in optimizer.param_groups:
        param_group["lr"] = lr

    return lr


# ============================================================
# TRAIN ONE EPOCH
# ============================================================

def train_one_epoch(
    model,
    loader,
    optimizer,
    epoch
):

    model.train()

    total_loss = 0.0
    total_samples = 0

    correct = 0

    for batch_index, (
        images,
        labels,
        lesions
    ) in enumerate(loader):

        images = images.to(DEVICE)
        labels = labels.to(DEVICE)
        lesions = lesions.to(DEVICE)

        optimizer.zero_grad()

        cls, count, count_to_class = model(images)

        # ----------------------------------------------------
        # Create 65-class label distribution
        # ----------------------------------------------------

        lesions_np = lesions.detach().cpu().numpy()

        count_distribution = generate_label_distribution(
            lesions_np,
            SIGMA
        )

        count_distribution = torch.tensor(
            count_distribution,
            dtype=torch.float32,
            device=DEVICE
        )

        # ----------------------------------------------------
        # Convert 65-class distribution into 4 classes
        # ----------------------------------------------------

        class_distribution = count_distribution_to_four_classes(
            count_distribution.cpu().numpy()
        )

        class_distribution = torch.tensor(
            class_distribution,
            dtype=torch.float32,
            device=DEVICE
        )

        # ----------------------------------------------------
        # Three LDL losses
        # ----------------------------------------------------

        loss_cls = distribution_kl_loss(
            cls,
            class_distribution,
            lad=0
        ) * 4.0

        loss_count = distribution_kl_loss(
            count,
            count_distribution,
            lad=0
        ) * 65.0

        loss_cls_count = distribution_kl_loss(
            count_to_class,
            class_distribution,
            lad=0
        ) * 4.0

        # ----------------------------------------------------
        # Original LDL combination
        # ----------------------------------------------------

        loss = (
            (loss_cls + loss_cls_count)
            * 0.5
            * LAM
            +
            loss_count
            * (1.0 - LAM)
        )

        loss.backward()

        optimizer.step()

        total_loss += loss.item() * images.size(0)

        total_samples += images.size(0)

        predictions = torch.argmax(
            cls + count_to_class,
            dim=1
        )

        correct += (
            predictions == labels
        ).sum().item()

        if (batch_index + 1) % 10 == 0:

            print(
                f"Epoch {epoch:03d} | "
                f"Batch {batch_index + 1:03d}/{len(loader):03d} | "
                f"Loss {loss.item():.4f}"
            )

    epoch_loss = total_loss / total_samples

    epoch_accuracy = (
        correct /
        total_samples
        *
        100.0
    )

    return epoch_loss, epoch_accuracy


# ============================================================
# EVALUATION
# ============================================================

@torch.no_grad()
def evaluate(
    model,
    loader
):

    model.eval()

    predictions = []
    true_labels = []

    for images, labels, lesions in loader:

        images = images.to(DEVICE)

        cls, count, count_to_class = model(images)

        # Final prediction combines both branches.
        final_probability = cls + count_to_class

        pred = torch.argmax(
            final_probability,
            dim=1
        )

        predictions.extend(
            pred.cpu().numpy().tolist()
        )

        # IMPORTANT:
        # Ground truth comes from the annotation LABEL,
        # not from converting lesion count into a class.

        true_labels.extend(
            labels.numpy().tolist()
        )

    accuracy = accuracy_score(
        true_labels,
        predictions
    ) * 100.0

    precision, recall, f1, _ = (
        precision_recall_fscore_support(
            true_labels,
            predictions,
            average="weighted",
            zero_division=0
        )
    )

    cm = confusion_matrix(
        true_labels,
        predictions,
        labels=[0, 1, 2, 3]
    )

    return (
        accuracy,
        precision,
        recall,
        f1,
        cm,
        true_labels,
        predictions
    )


# ============================================================
# PLOTS
# ============================================================

def save_confusion_matrix(
    cm,
    accuracy,
    filename
):

    plt.figure(figsize=(7, 6))

    plt.imshow(
        cm,
        interpolation="nearest",
        cmap="Blues"
    )

    plt.title(
        f"ACNE04 Confusion Matrix\nAccuracy: {accuracy:.2f}%"
    )

    plt.colorbar()

    classes = [
        "Level 0",
        "Level 1",
        "Level 2",
        "Level 3"
    ]

    plt.xticks(
        range(4),
        classes,
        rotation=45
    )

    plt.yticks(
        range(4),
        classes
    )

    threshold = cm.max() / 2.0

    for i in range(4):

        for j in range(4):

            plt.text(
                j,
                i,
                str(cm[i, j]),
                ha="center",
                va="center",
                color="white"
                if cm[i, j] > threshold
                else "black"
            )

    plt.ylabel("True Label")
    plt.xlabel("Predicted Label")

    plt.tight_layout()

    plt.savefig(
        filename,
        dpi=300
    )

    plt.close()


def save_accuracy_pie(
    accuracy,
    filename
):

    incorrect = 100.0 - accuracy

    plt.figure(figsize=(7, 7))

    plt.pie(
        [accuracy, incorrect],
        labels=[
            f"Correct\n{accuracy:.2f}%",
            f"Incorrect\n{incorrect:.2f}%"
        ],
        autopct="%1.1f%%",
        startangle=90
    )

    plt.title(
        "ACNE04 Test Accuracy"
    )

    plt.tight_layout()

    plt.savefig(
        filename,
        dpi=300
    )

    plt.close()


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # For the first complete run, use fold 0.
    #
    # Once this works successfully, we can run all 5 folds.
    # --------------------------------------------------------

    fold = 0

    train_file = os.path.join(
        DATA_DIR,
        f"NNEW_trainval_{fold}.txt"
    )

    test_file = os.path.join(
        DATA_DIR,
        f"NNEW_test_{fold}.txt"
    )

    if not os.path.exists(train_file):

        raise FileNotFoundError(
            f"Training file not found:\n{train_file}"
        )

    if not os.path.exists(test_file):

        raise FileNotFoundError(
            f"Testing file not found:\n{test_file}"
        )

    train_dataset = AcneDataset(
        train_file,
        train_transform
    )

    test_dataset = AcneDataset(
        test_file,
        test_transform
    )

    print(
        "Training images:",
        len(train_dataset)
    )

    print(
        "Testing images :",
        len(test_dataset)
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=NUM_WORKERS
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=NUM_WORKERS
    )

    # --------------------------------------------------------
    # MODEL
    # --------------------------------------------------------

    model = AcneLDLResNet50()

    model = model.to(DEVICE)

    print("Model ready.")

    # --------------------------------------------------------
    # OPTIMIZER
    # --------------------------------------------------------

    optimizer = torch.optim.SGD(
        model.parameters(),
        lr=LR,
        momentum=MOMENTUM,
        weight_decay=WEIGHT_DECAY
    )

    best_accuracy = 0.0

    history_loss = []
    history_train_accuracy = []
    history_test_accuracy = []

    best_model_path = os.path.join(
        MODEL_DIR,
        "acne_ldl_resnet50_best.pth"
    )

    # --------------------------------------------------------
    # TRAINING
    # --------------------------------------------------------

    for epoch in range(
        1,
        EPOCHS + 1
    ):

        current_lr = adjust_learning_rate(
            optimizer,
            epoch
        )

        print("\n" + "=" * 70)

        print(
            f"Epoch {epoch}/{EPOCHS}"
        )

        print(
            f"Learning rate: {current_lr:.7f}"
        )

        print("=" * 70)

        train_loss, train_accuracy = train_one_epoch(
            model,
            train_loader,
            optimizer,
            epoch
        )

        (
            test_accuracy,
            precision,
            recall,
            f1,
            cm,
            true_labels,
            predictions
        ) = evaluate(
            model,
            test_loader
        )

        history_loss.append(
            train_loss
        )

        history_train_accuracy.append(
            train_accuracy
        )

        history_test_accuracy.append(
            test_accuracy
        )

        print(
            f"\nTrain Loss     : {train_loss:.4f}"
        )

        print(
            f"Train Accuracy : {train_accuracy:.2f}%"
        )

        print(
            f"Test Accuracy  : {test_accuracy:.2f}%"
        )

        print(
            f"Precision      : {precision:.4f}"
        )

        print(
            f"Recall         : {recall:.4f}"
        )

        print(
            f"F1 Score       : {f1:.4f}"
        )

        if test_accuracy > best_accuracy:

            best_accuracy = test_accuracy

            torch.save(
                model.state_dict(),
                best_model_path
            )

            print(
                f"\nNEW BEST MODEL: "
                f"{best_accuracy:.2f}%"
            )

    # ========================================================
    # FINAL EVALUATION USING BEST MODEL
    # ========================================================

    print("\n")
    print("=" * 70)
    print("FINAL BEST MODEL EVALUATION")
    print("=" * 70)

    model.load_state_dict(
        torch.load(
            best_model_path,
            map_location=DEVICE
        )
    )

    (
        accuracy,
        precision,
        recall,
        f1,
        cm,
        true_labels,
        predictions
    ) = evaluate(
        model,
        test_loader
    )

    print(
        f"\nFinal Accuracy : {accuracy:.2f}%"
    )

    print(
        f"Precision      : {precision:.4f}"
    )

    print(
        f"Recall         : {recall:.4f}"
    )

    print(
        f"F1 Score       : {f1:.4f}"
    )

    print("\nConfusion Matrix:")
    print(cm)

    print("\nClassification Report:")

    print(
        classification_report(
            true_labels,
            predictions,
            target_names=[
                "Level 0",
                "Level 1",
                "Level 2",
                "Level 3"
            ],
            zero_division=0
        )
    )

    # ========================================================
    # SAVE RESULTS
    # ========================================================

    results_file = os.path.join(
        OUTPUT_DIR,
        "ldl_results.txt"
    )

    with open(
        results_file,
        "w"
    ) as f:

        f.write(
            "ACNE04 LABEL DISTRIBUTION LEARNING RESULTS\n"
        )

        f.write(
            "==========================================\n\n"
        )

        f.write(
            f"Fold: {fold}\n"
        )

        f.write(
            f"Epochs: {EPOCHS}\n"
        )

        f.write(
            f"Batch Size: {BATCH_SIZE}\n"
        )

        f.write(
            f"Device: {DEVICE}\n\n"
        )

        f.write(
            f"Accuracy: {accuracy:.2f}%\n"
        )

        f.write(
            f"Precision: {precision:.4f}\n"
        )

        f.write(
            f"Recall: {recall:.4f}\n"
        )

        f.write(
            f"F1 Score: {f1:.4f}\n\n"
        )

        f.write(
            "Confusion Matrix:\n"
        )

        f.write(
            str(cm)
        )

        f.write(
            "\n\nClassification Report:\n"
        )

        f.write(
            classification_report(
                true_labels,
                predictions,
                target_names=[
                    "Level 0",
                    "Level 1",
                    "Level 2",
                    "Level 3"
                ],
                zero_division=0
            )
        )

    # ========================================================
    # SAVE CONFUSION MATRIX
    # ========================================================

    save_confusion_matrix(
        cm,
        accuracy,
        os.path.join(
            OUTPUT_DIR,
            "confusion_matrix.png"
        )
    )

    # ========================================================
    # SAVE ACCURACY PIE
    # ========================================================

    save_accuracy_pie(
        accuracy,
        os.path.join(
            OUTPUT_DIR,
            "accuracy_pie_chart.png"
        )
    )

    # ========================================================
    # SAVE TRAINING ACCURACY GRAPH
    # ========================================================

    # ========================================================
# SAVE TRAINING AND TESTING ACCURACY GRAPH
# ========================================================

plt.figure(figsize=(10, 6))

# Use only epochs that actually have recorded results
epochs_range = range(
    1,
    len(history_train_accuracy) + 1
)

plt.plot(
    epochs_range,
    history_train_accuracy,
    marker="o",
    linewidth=2,
    label="Training Accuracy"
)

plt.plot(
    epochs_range,
    history_test_accuracy,
    marker="o",
    linewidth=2,
    linestyle="--",
    label="Testing Accuracy"
)

plt.xlabel(
    "Epoch",
    fontsize=12
)

plt.ylabel(
    "Accuracy (%)",
    fontsize=12
)

plt.title(
    "Training and Testing Accuracy Curve",
    fontsize=14,
    fontweight="bold"
)

plt.legend(
    loc="lower right"
)

plt.grid(
    True,
    linestyle="--",
    alpha=0.3
)

plt.xlim(
    1,
    len(history_train_accuracy)
)

plt.ylim(
    0,
    100
)

plt.tight_layout()

plt.savefig(
    os.path.join(
        OUTPUT_DIR,
        "training_testing_accuracy_curve.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print(
    "Training and testing accuracy curve saved:"
)

print(
    os.path.join(
        OUTPUT_DIR,
        "training_testing_accuracy_curve.png"
    )
)