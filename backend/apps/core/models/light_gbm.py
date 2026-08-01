import numpy as np
import pandas as pd

from lightgbm import LGBMClassifier

from apps.core.utils.training_results import print_metrics

class LightGBMModel(LGBMClassifier):
    def fit(self, X_train, y_train, X_test, y_test, *args, **kwargs):
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test

        super().fit(X_train, y_train, *args, **kwargs)

        self.pred = np.asarray(super().predict(X_test)).astype(int).ravel()

        pred_proba_raw = np.asarray(super().predict_proba(X_test))
        if pred_proba_raw.ndim == 2 and pred_proba_raw.shape[1] >= 2:
            self.pred_proba = pred_proba_raw[:, 1].ravel()
        else:
            self.pred_proba = pred_proba_raw.ravel()

        self.feature_importances = pd.DataFrame(
            {
                "Feature": X_test.columns,
                "Importance": super().feature_importances_
            }
        ).sort_values("Importance", ascending=False)

    def print_metrics_feature_importances(self, command):
        print_metrics(command, "LightGBM", self.y_test, self.pred, self.pred_proba)
        if command is not None:
            command.stdout.write(str(self.feature_importances.head(15)))