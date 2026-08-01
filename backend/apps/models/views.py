from django.db.models import Q, Count
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.core.utils.dates import get_current_season_year, get_current_week_number
from apps.models.mixins import ModelPerformance
from apps.models.models import PredictionModel, Prediction
from apps.scheduling.choices import GameStatus
from apps.scheduling.models import Week

class ModelPerformanceViewSet(ModelPerformance, viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    # Retrieves model performance metrics and insights
    # Endpoint: /api/models/performance/{model_version}/
    def retrieve(self, request, *args, **kwargs):
        model_version = kwargs.get('model_version')
        matching_models = PredictionModel.objects.filter(model_version=model_version)

        def _version_number(version):
            if not version:
                return None
            normalized = version.lower()
            if normalized.startswith("v"):
                normalized = normalized[1:]
            return int(normalized) if normalized.isdigit() else None

        current_week = Week.objects.filter(
            season__year=get_current_season_year(),
            week=get_current_week_number()
        ).first()
        if not current_week:
            return Response({
                "error": "No current week found and default week is also missing."
            }, status=404)

        current_season = current_week.season.year

        predictions_by_models = Prediction.objects.filter(model__in=matching_models)

        model_performance_summary = self.get_model_performance(
            current_week,
            model_version=model_version,
            season_year=current_season,
            week_id=current_week.id,
        )

        completed_predictions = predictions_by_models.filter(
            game__status=GameStatus.COMPLETED,
            was_correct__isnull=False,
        )
        weekly_breakdown = (
            completed_predictions
            .values("game__week__season__year", "game__week__week")
            .annotate(
                wins=Count("id", filter=Q(was_correct=True)),
                losses=Count("id", filter=Q(was_correct=False)),
            )
            .order_by("game__week__season__year", "game__week__week")
        )

        data = {}

        current_version_number = _version_number(model_version)
        available_versions = list(
            PredictionModel.objects.values_list("model_version", flat=True).distinct()
        )
        previous_versions = []
        for version in available_versions:
            if version == model_version:
                continue
            if current_version_number is None:
                previous_versions.append(version)
                continue
            version_number = _version_number(version)
            if version_number is not None and version_number < current_version_number:
                previous_versions.append(version)

        previous_overall = (
            Prediction.objects
            .filter(
                model__model_version__in=previous_versions,
                game__status=GameStatus.COMPLETED,
                was_correct__isnull=False,
            )
            .values("model__model_version")
            .annotate(
                wins=Count("id", filter=Q(was_correct=True)),
                losses=Count("id", filter=Q(was_correct=False)),
            )
            .order_by("model__model_version")
        )
        previous_overall_map = {
            row["model__model_version"]: {
                "wins": row["wins"],
                "losses": row["losses"],
            }
            for row in previous_overall
        }

        data['model_performance'] = {
            "model_version": model_version,
            "week": model_performance_summary["week"],
            "season": model_performance_summary["season"],
            "all_time": model_performance_summary["all_time"],
            "week_by_week": [
                {
                    "season": row["game__week__season__year"],
                    "week": row["game__week__week"],
                    "wins": row["wins"],
                    "losses": row["losses"],
                    "percentage": (
                        round(row["wins"] / (row["wins"] + row["losses"]), 3)
                        if (row["wins"] + row["losses"]) > 0
                        else 0.0
                    ),
                }
                for row in weekly_breakdown
            ],
            "previous_models": [
                {
                    "model_version": version,
                    "wins": previous_overall_map.get(version, {}).get("wins", 0),
                    "losses": previous_overall_map.get(version, {}).get("losses", 0),
                    "percentage": (
                        round(
                            previous_overall_map.get(version, {}).get("wins", 0)
                            / (
                                previous_overall_map.get(version, {}).get("wins", 0)
                                + previous_overall_map.get(version, {}).get("losses", 0)
                            ),
                            3,
                        )
                        if (
                            previous_overall_map.get(version, {}).get("wins", 0)
                            + previous_overall_map.get(version, {}).get("losses", 0)
                        )
                        > 0
                        else 0.0
                    ),
                }
                for version in sorted(previous_versions)
            ],
        }
        first_model = matching_models.first()
        data["Features"] = first_model.features if first_model else None
        return Response(data)