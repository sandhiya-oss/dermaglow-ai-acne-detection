import matplotlib.pyplot as plt

# Actual recorded results from your ACNE04 training
epochs = [4, 32, 33, 36]

training_accuracy = [67.38, 89.61, 91.59, 92.36]
test_accuracy = [73.63, 78.77, 78.08, 78.42]

plt.figure(figsize=(10, 6))

plt.plot(
    epochs,
    training_accuracy,
    marker="o",
    linewidth=2,
    label="Training Accuracy"
)

plt.plot(
    epochs,
    test_accuracy,
    marker="o",
    linewidth=2,
    linestyle="--",
    label="Test Accuracy"
)

plt.xlabel("Epochs")
plt.ylabel("Accuracy (%)")
plt.title("Training and Test Accuracy Curve")

plt.ylim(0, 100)
plt.grid(True, alpha=0.3)
plt.legend()

plt.tight_layout()

plt.savefig(
    "outputs/training_validation_curve.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()