"""
Braille-V Training — CNN Character Classifier
Trains a 3-layer CNN to classify 48×48 grayscale Braille cell images into 64 classes.

Architecture:
    Conv2D(32) → ReLU → BatchNorm → MaxPool
    Conv2D(64) → ReLU → BatchNorm → MaxPool
    Conv2D(128) → ReLU → BatchNorm → MaxPool
    Flatten → Dense(256) → ReLU → Dropout(0.5)
    Dense(128) → ReLU → Dropout(0.5)
    Dense(64, softmax)

Prerequisites:
    pip install tensorflow opencv-python numpy

Usage:
    python -m training.train_cnn --data ./data/cnn_split
"""

import argparse
import logging
from pathlib import Path

import cv2
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ── Hyperparameters ──────────────────────────────────────────────────────────
INPUT_SIZE = 48
NUM_CLASSES = 64
EPOCHS = 50
BATCH_SIZE = 32
LEARNING_RATE = 0.001


def build_model():
    """Build the CNN classifier."""
    import tensorflow as tf
    from tensorflow.keras import layers, models

    model = models.Sequential(
        [
            # Block 1
            layers.Conv2D(32, (3, 3), activation="relu", input_shape=(INPUT_SIZE, INPUT_SIZE, 1)),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            # Block 2
            layers.Conv2D(64, (3, 3), activation="relu"),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            # Block 3
            layers.Conv2D(128, (3, 3), activation="relu"),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            # Classifier head
            layers.Flatten(),
            layers.Dense(256, activation="relu"),
            layers.Dropout(0.5),
            layers.Dense(128, activation="relu"),
            layers.Dropout(0.5),
            layers.Dense(NUM_CLASSES, activation="softmax"),
        ]
    )

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    model.summary()
    return model


def load_dataset(data_dir: Path, split: str = "train") -> tuple[np.ndarray, np.ndarray]:
    """
    Load images from a directory structure:
        data_dir/split/class_name/image.png

    Returns (images, labels) as numpy arrays.
    """
    split_dir = data_dir / split
    if not split_dir.exists():
        raise FileNotFoundError(f"Split directory not found: {split_dir}")

    images = []
    labels = []
    class_names = sorted(d.name for d in split_dir.iterdir() if d.is_dir())

    if len(class_names) == 0:
        raise ValueError(f"No class subdirectories found in {split_dir}")

    class_to_idx = {name: idx for idx, name in enumerate(class_names)}
    logger.info("Found %d classes in %s", len(class_names), split)

    for class_name in class_names:
        class_dir = split_dir / class_name
        for img_path in class_dir.glob("*.png"):
            img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            img = cv2.resize(img, (INPUT_SIZE, INPUT_SIZE))
            images.append(img)
            labels.append(class_to_idx[class_name])

    images_arr = np.array(images, dtype=np.float32) / 255.0
    images_arr = np.expand_dims(images_arr, axis=-1)  # add channel dim

    # One-hot encode labels
    import tensorflow as tf
    labels_arr = tf.keras.utils.to_categorical(labels, num_classes=NUM_CLASSES)

    return images_arr, labels_arr


def train(args):
    """Train the CNN classifier."""
    import tensorflow as tf

    data_dir = Path(args.data)

    logger.info("Loading training data...")
    X_train, y_train = load_dataset(data_dir, "train")
    logger.info("  Train: %d images", len(X_train))

    logger.info("Loading validation data...")
    X_val, y_val = load_dataset(data_dir, "val")
    logger.info("  Val: %d images", len(X_val))

    logger.info("Building model...")
    model = build_model()

    # Callbacks
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy", patience=10, restore_best_weights=True
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=5, min_lr=1e-6
        ),
    ]

    logger.info("Training for %d epochs...", args.epochs)
    history = model.fit(
        X_train,
        y_train,
        validation_data=(X_val, y_val),
        epochs=args.epochs,
        batch_size=args.batch_size,
        callbacks=callbacks,
        verbose=1,
    )

    # Evaluate on test set if available
    test_dir = data_dir / "test"
    if test_dir.exists():
        logger.info("Evaluating on test set...")
        X_test, y_test = load_dataset(data_dir, "test")
        test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
        logger.info("Test accuracy: %.4f  |  Test loss: %.4f", test_acc, test_loss)

    # Save model
    export_path = Path(args.output)
    export_path.parent.mkdir(parents=True, exist_ok=True)
    model.save(str(export_path))
    logger.info("Model saved to %s", export_path)

    return history


def main():
    parser = argparse.ArgumentParser(description="Train CNN Braille classifier")
    parser.add_argument(
        "--data", type=str, required=True, help="Path to processed dataset directory"
    )
    parser.add_argument("--epochs", type=int, default=EPOCHS)
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    parser.add_argument(
        "--output",
        type=str,
        default="app/models/cnn_classifier.h5",
        help="Path to save trained model",
    )

    args = parser.parse_args()
    train(args)


if __name__ == "__main__":
    main()
