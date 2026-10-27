import matplotlib.pyplot as plt
import numpy as np

# ============================================================
# ACTUAL BEST MODEL RESULTS - EPOCH 32
# ============================================================

metrics = ["Accuracy", "Precision", "Recall", "F1-Score"]

values = [
    78.77,
    79.27,
    78.77,
    78.76
]

x = np.arange(len(metrics))

plt.figure(figsize=(10, 6))

bars = plt.bar(x, values, width=0.55)

plt.ylabel("Score (%)", fontsize=12)
plt.xlabel("Performance Metrics", fontsize=12)
plt.title("Performance of Proposed Acne Detection Model",
          fontsize=14, fontweight="bold")

plt.xticks(x, metrics)
plt.ylim(0, 100)

# Display values above bars
for bar, value in zip(bars, values):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        value + 1,
        f"{value:.2f}%",
        ha="center",
        va="bottom",
        fontsize=11,
        fontweight="bold"
    )

plt.grid(axis="y", linestyle="--", alpha=0.4)

plt.tight_layout()

plt.savefig(
    "outputs/performance_comparison.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print("Performance comparison graph saved successfully!")
print("Location: outputs/performance_comparison.png")