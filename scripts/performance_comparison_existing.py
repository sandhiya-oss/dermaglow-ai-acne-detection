import matplotlib.pyplot as plt
import numpy as np

metrics = ["Accuracy", "Precision", "Recall"]

existing_1 = [66.30, 65.10, 62.75]
existing_2 = [71.30, 68.32, 68.16]
proposed = [78.77, 79.27, 78.77]

x = np.arange(len(metrics))
width = 0.25

plt.figure(figsize=(10, 6))

plt.bar(x - width, existing_1, width, label="Existing [1] - SE-Res18")
plt.bar(x, existing_2, width, label="Existing [2] - SE-Res50")
plt.bar(x + width, proposed, width, label="Proposed Model")

plt.ylabel("Performance (%)")
plt.xlabel("Metrics")
plt.title("Performance Comparison with Existing Methods")

plt.xticks(x, metrics)
plt.ylim(0, 100)

plt.legend()
plt.grid(axis="y", linestyle="--", alpha=0.3)

plt.tight_layout()

plt.savefig(
    "outputs/performance_comparison_existing.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()