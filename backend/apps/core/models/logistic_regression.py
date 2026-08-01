import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

from apps.core.utils.training_results import print_metrics

class LogisticRegressionModel:
    def __init__(self, command):
        self.scaler = StandardScaler()
        self.model = LogisticRegression(max_iter=10000, random_state=42)
        self.command = command

    def train(self, X_train, X_test, y_train, y_test):
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test

        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        self.model.fit(X_train_scaled, y_train)
        self.pred = self.model.predict(X_test_scaled)
        self.pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]

    def print_metrics_and_coefficients(self):
        if hasattr(self, 'model'):
            coef_df = pd.DataFrame({
                'Feature': range(len(self.model.coef_[0])),
                'Coefficient': self.model.coef_[0]
            })
            coef_df["Absolute Coefficient"] = coef_df["Coefficient"].abs()
            coef_df = coef_df.sort_values(by="Absolute Coefficient", ascending=False)
            if coef_df.empty:
                self.command.stdout.write(self.command.style.WARNING("No coefficients to display."))
                return
            self.command.stdout.write(self.command.style.SUCCESS("[Top Logistic Regression coefficients by magnitude]"))
            self.command.stdout.write(str(coef_df[["Feature", "Coefficient", "Absolute Coefficient"]].head(15)))

            print_metrics(self.command, "Logistic Regression", self.y_test, self.pred, self.pred_proba)