from rangefilter.filters import NumericRangeFilter

from django.contrib import admin

from apps.core.admin import playlytics_admin_site
from apps.core.admin_filters import DropdownRelatedFieldListFilter, ChoiceDropdownFilter, FieldListFilter
from apps.models.models import Prediction, PredictionModel

@admin.register(Prediction, site=playlytics_admin_site)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ("model", "game", "home_win", "home_win_probability", "was_correct")
    ordering = ("-game__week__season__year", "game__week__week", "game__game_time")

    search_fields = ("model__model_name", "game__home_team__name", "game__away_team__name")
    list_filter = (
        ("model", DropdownRelatedFieldListFilter),
        ("game__week__season__year", NumericRangeFilter),
        ("game__week__week", NumericRangeFilter),
        "was_correct",
    )

    readonly_fields = ("model", "game", "home_win", "home_win_probability", "was_correct")
    fieldsets = (
        ("Prediction Model", {
            "fields": ("model",)}),
        ("Game", {
            "fields": ("game",)}),
        ("Prediction", {
            "fields": ("home_win", "home_win_probability",)}),
        ("Result", {
            "fields": ("was_correct",)}),
    )

@admin.register(PredictionModel, site=playlytics_admin_site)
class PredictionModelAdmin(admin.ModelAdmin):
    list_display = ("model_name", "model_version")

    search_fields = ("model_name", "model_version")

    readonly_fields = ("model_name", "model_version")
    fieldsets = (
        ("Prediction Model Information", {
            "fields": ("model_name", "model_version", "features")}),
    )