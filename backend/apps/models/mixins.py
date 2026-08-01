from django.db.models import Q, Count, QuerySet

from apps.models.models import Prediction
from apps.scheduling.choices import GameStatus

class ModelPredictionMixin:
    def get_latest_prediction(self, obj):
        if not hasattr(obj, "_latest_model_prediction"):
            obj._latest_model_prediction = (
                Prediction.objects
                .select_related("model")
                .filter(game_id=obj.id)
                .order_by("-generated_at")
                .first()
            )
        return obj._latest_model_prediction
    
    def get_model_prediction(self, obj):
        prediction = self.get_latest_prediction(obj)
        if not prediction:
            return {
                "home": None,
                "away": None,
            }
        return {
            "home": prediction.home_win_probability,
            "away": 1 - prediction.home_win_probability,
        }
    
class ModelPerformance:
    context: dict

    def _get_request(self):
        context = getattr(self, "context", {})
        return context.get("request") or getattr(self, "request", None)

    def _resolve_scope_game(self, obj):
        if obj is None:
            return None
        if isinstance(obj, QuerySet):
            return obj.first()
        return obj

    def _resolve_model_version(self, obj, model_version=None):
        if model_version:
            return model_version

        request = self._get_request()

        if request:
            request_model_version = (
                request.query_params.get("model_version")
                or request.query_params.get("model_name")
            )
            if request_model_version:
                return request_model_version

        scope_game = self._resolve_scope_game(obj)
        if not scope_game:
            return None
            
        latest_prediction = (
            Prediction.objects
            .select_related("model")
            .filter(game_id=scope_game.id)
            .order_by("-generated_at")
            .first()
        )
        return latest_prediction.model.model_name if latest_prediction else None
    
    def _resolve_season_year_and_week_id(self, obj):
        scope_obj = self._resolve_scope_game(obj)
        if not scope_obj:
            return None, None

        # Game-like object
        if hasattr(scope_obj, "week") and hasattr(scope_obj, "week_id"):
            return scope_obj.week.season.year, scope_obj.week_id

        # Week-like object
        if hasattr(scope_obj, "season") and hasattr(scope_obj, "id"):
            return scope_obj.season.year, scope_obj.id

        return None, None

    def get_model_performance(self, obj=None, model_version=None, season_year=None, week_id=None):
        model_version = self._resolve_model_version(obj, model_version=model_version)
        empty_record = {"wins": 0, "losses": 0, "percentage": 0.0}
        if not model_version:
            return {
                "model_version": None,
                "week": empty_record,
                "season": empty_record,
                "all_time": empty_record,
            }
        
        completed_filter = Q(game__status=GameStatus.COMPLETED)
        
        def _record(queryset):
            stats = queryset.aggregate(
                wins=Count("id", filter=completed_filter & Q(was_correct=True)),
                losses=Count("id", filter=completed_filter & Q(was_correct=False)),
            )
            wins = stats["wins"] or 0
            losses = stats["losses"] or 0
            total = wins + losses
            return {
                "wins": wins,
                "losses": losses,
                "percentage": round(wins / total, 3) if total > 0 else 0,
            }

        model_version = model_version.split("_")[0]  # Format "v1_2024"
        base_qs = Prediction.objects.filter(model__model_version=model_version)

        resolved_season_year = season_year
        resolved_week_id = week_id
        if resolved_season_year is None or resolved_week_id is None:
            fallback_season_year, fallback_week_id = self._resolve_season_year_and_week_id(obj)
            if resolved_season_year is None:
                resolved_season_year = fallback_season_year
            if resolved_week_id is None:
                resolved_week_id = fallback_week_id

        if resolved_season_year is not None:
            season_qs = base_qs.filter(game__week__season__year=resolved_season_year)
            if resolved_week_id is not None:
                week_qs = season_qs.filter(game__week_id=resolved_week_id)
            else:
                week_qs = Prediction.objects.none()
        else:
            season_qs = Prediction.objects.none()
            week_qs = Prediction.objects.none()

        return {
            "model_version": model_version,
            "week": _record(week_qs),
            "season": _record(season_qs),
            "all_time": _record(base_qs),
        }