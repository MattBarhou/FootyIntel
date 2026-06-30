#!/usr/bin/env python3
"""Train the Random Forest match prediction model."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ml.train import train_and_save


def main() -> None:
    metadata = train_and_save()
    test = metadata["test_metrics"]
    print("\nTraining complete.")
    print(f"Test accuracy: {test['accuracy']:.3f}")
    print(f"Test log loss: {test['log_loss']:.3f}")
    print(f"Baseline (always home): {test['baseline_always_home']:.3f}")
    print(f"Baseline (bookmaker): {test['baseline_bookmaker']:.3f}")


if __name__ == "__main__":
    main()
