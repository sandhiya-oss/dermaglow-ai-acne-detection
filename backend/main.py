
import io
import os

import torch
import torch.nn as nn
from PIL import Image, UnidentifiedImageError
from torchvision import transforms, models
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware


# ==========================================
# SETTINGS
# ==========================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "acne_ldl_resnet50_best.pth",
)

DEVICE = torch.device(
    "mps" if torch.backends.mps.is_available() else "cpu"
)

NUM_CLASSES = 4
NUM_COUNT_CLASSES = 65

CLASS_NAMES = [
    "Level 0",
    "Level 1",
    "Level 2",
    "Level 3",
]

IMAGE_TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.45815152, 0.361242, 0.29348266],
        std=[0.2814769, 0.226306, 0.20132513],
    ),
])


# ==========================================
# MODEL ARCHITECTURE
# ==========================================
class AcneLDLResNet50(nn.Module):
    def __init__(self):
        super().__init__()

        backbone = models.resnet50(weights=None)
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


# ==========================================
# LOAD EXISTING TRAINED MODEL
# ==========================================
# The model is optional during CI testing because
# large model weights are not stored in GitHub.
# If the weights exist, load the real trained model.

model = None

if os.path.isfile(MODEL_PATH):
    model = AcneLDLResNet50()

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=DEVICE,
    )

    if (
        isinstance(checkpoint, dict)
        and "model_state_dict" in checkpoint
    ):
        model.load_state_dict(checkpoint["model_state_dict"])
    else:
        model.load_state_dict(checkpoint)

    model.to(DEVICE)
    model.eval()

    print(f"Acne model loaded successfully on {DEVICE}")

else:
    print(
        "WARNING: Trained model not found. "
        "API tests can run, but predictions are unavailable."
    )


# ==========================================
# FASTAPI APPLICATION
# ==========================================
app = FastAPI(
    title="DermaGlow AI Acne Detection API",
    description="Image prediction using the existing ACNE04 model.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# HOME ENDPOINT
# ==========================================
@app.get("/")
def home():
    return {
        "message": "DermaGlow AI backend is running",
        "device": str(DEVICE),
        "model_loaded": model is not None,
    }


# ==========================================
# HEALTH ENDPOINT
# ==========================================
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "device": str(DEVICE),
        "model_loaded": model is not None,
    }


# ==========================================
# PREDICTION ENDPOINT
# ==========================================
@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Please upload an image file.",
        )

    try:
        contents = await file.read()

        if not contents:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty.",
            )

        with Image.open(io.BytesIO(contents)) as source:
            image = source.convert("RGB")

    except HTTPException:
        raise

    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
    ):
        raise HTTPException(
            status_code=400,
            detail="The file could not be read as an image.",
        )

    # Return a clear error if model weights are unavailable.
    # This lets CI test the API without uploading large weights.
    if model is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "The trained model is unavailable. "
                "Install the model weights to enable predictions."
            ),
        )

    image_tensor = IMAGE_TRANSFORM(image).unsqueeze(0).to(DEVICE)

    try:
        with torch.no_grad():
            cls, count, count_to_class = model(image_tensor)

            # Preserve the existing evaluation prediction rule.
            combined = cls + count_to_class

            predicted_index = int(
                torch.argmax(combined, dim=1).item()
            )

            normalized_scores = (
                combined[0] / combined[0].sum()
            )

            class_scores = {
                CLASS_NAMES[i]: round(
                    float(normalized_scores[i].item()) * 100,
                    2,
                )
                for i in range(NUM_CLASSES)
            }

        return {
            "predicted_level": predicted_index,
            "predicted_label": CLASS_NAMES[predicted_index],
            "model_score_percent": class_scores[
                CLASS_NAMES[predicted_index]
            ],
            "class_scores_percent": class_scores,
            "device": str(DEVICE),
            "notice": (
                "Educational model estimate only; "
                "not a medical diagnosis."
            ),
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Prediction failed. Check the backend terminal.",
        ) from exc
