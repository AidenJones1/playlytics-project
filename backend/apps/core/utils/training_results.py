import numpy as np
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    roc_auc_score,
    log_loss,
    brier_score_loss,
    confusion_matrix,
    classification_report
)

def print_metrics(command, label: str, y_true: pd.Series, y_pred: np.ndarray, y_proba: np.ndarray):
    accuracy = accuracy_score(y_true, y_pred)
    try:
        auc = roc_auc_score(y_true, y_proba)
        auc_text = f"{auc:.4f}"
    except ValueError:
        auc_text = "N/A (single class in y_true)"

    model_log_loss = log_loss(y_true, y_proba, labels=[0, 1])
    brier = brier_score_loss(y_true, y_proba)
    cm = confusion_matrix(y_true, y_pred)
    report = classification_report(y_true, y_pred, zero_division=0)

    command.stdout.write(command.style.SUCCESS(f"\n[{label}]"))
    command.stdout.write(f"Accuracy: {accuracy:.4f}")
    command.stdout.write(f"ROC-AUC: {auc_text}")
    command.stdout.write(f"Log Loss: {model_log_loss:.4f}")
    command.stdout.write(f"Brier Score: {brier:.4f}")
    command.stdout.write(f"Confusion Matrix:\n{cm}")
    command.stdout.write(f"Classification Report:\n{report}")

    return (accuracy, auc_text, model_log_loss, brier, cm, report)