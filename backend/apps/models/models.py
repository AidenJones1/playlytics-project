import uuid

from django.db import models

class PredictionModel(models.Model):
    model_name = models.CharField(primary_key=True, max_length=255)
    model_version = models.CharField(max_length=5)
    features = models.JSONField(default=list)

    class Meta:
        verbose_name = "Prediction Model"
        verbose_name_plural = "Prediction Models"
        db_table = "prediction_models"

    def __str__(self):
        return self.model_name


class Prediction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model = models.ForeignKey('models.PredictionModel', on_delete=models.CASCADE)
    game = models.ForeignKey('scheduling.Game', on_delete=models.CASCADE)
    home_win = models.BooleanField()
    home_win_probability = models.FloatField()
    generated_at = models.DateTimeField(auto_now_add=True)
    was_correct = models.BooleanField(null=True, blank=True)

    class Meta:
        verbose_name = "Prediction"
        verbose_name_plural = "Predictions"
        db_table = "predictions"

    def __str__(self):
        return f"Prediction for {self.game} by {self.model}"