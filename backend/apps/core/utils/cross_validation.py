import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import accuracy_score, roc_auc_score, log_loss, brier_score_loss

def build_cross_week_folds(
        df,
        season_column='season',
        week_column='week',
        min_training_week=5,
        val_horizon_weeks=1,
        gap_weeks=0,
):
    folds = []
    for season in sorted(df[season_column].dropna().unique()):
        season_df = df[df[season_column] == season]
        weeks = sorted(season_df[week_column].dropna().unique())
        if len(weeks) < min_training_week + val_horizon_weeks:
            continue

        start_idx = min_training_week - 1
        end_idx = len(weeks) - val_horizon_weeks - 1 - gap_weeks

        for i in range(start_idx, end_idx + 1):
            train_weeks = weeks[: i + 1]
            val_start = i + 1 + gap_weeks
            val_end = val_start + val_horizon_weeks
            val_weeks = weeks[val_start:val_end]

            train_idx = df.index[(df[season_column] == season) & (df[week_column].isin(train_weeks))]
            val_idx = df.index[(df[season_column] == season) & (df[week_column].isin(val_weeks))]

            if len(train_idx) > 0 and len(val_idx) > 0:
                folds.append((train_idx, val_idx, season, train_weeks[-1], val_weeks))

    return folds

def evaluate_model_on_folds(model, X: pd.DataFrame, y: pd.Series, folds):
    rows = []
    for fold_num, (tr_idx, va_idx, season, train_end_week, val_weeks) in enumerate(folds, start=1):
        m = clone(model)
        m.fit(X.loc[tr_idx], y.loc[tr_idx])

        proba_raw = np.asarray(m.predict_proba(X.loc[va_idx]))
        if proba_raw.ndim == 2 and proba_raw.shape[1] >= 2:
            proba = proba_raw[:, 1]
        else:
            proba = proba_raw.ravel()
        pred = (proba >= 0.5).astype(int)

        y_true = y.loc[va_idx]
        row = {
            "fold": fold_num,
            "season": season,
            "train_end_week": int(train_end_week),
            "val_weeks": list(map(int, val_weeks)),
            "accuracy": accuracy_score(y_true, pred),
            "roc_auc": roc_auc_score(y_true, proba) if y_true.nunique() > 1 else np.nan,
            "log_loss": log_loss(y_true, proba, labels=[0, 1]),
            "brier": brier_score_loss(y_true, proba),
        }
        rows.append(row)

    fold_df = pd.DataFrame(rows)
    summary = fold_df[["accuracy", "roc_auc", "log_loss", "brier"]].mean(numeric_only=True)
    return fold_df, summary