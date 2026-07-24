from rangefilter.filters import NumericRangeFilter

from django.contrib import admin

from apps.core.admin import playlytics_admin_site
from apps.core.admin_filters import DropdownRelatedFieldListFilter, DropdownChoicesFieldListFilter
from apps.scheduling.models import Season, Week, Game

@admin.register(Season, site=playlytics_admin_site)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('year', 'season_type', 'start_date', 'end_date')
    ordering = ('year', 'season_type')

    list_filter = (
        ('year', NumericRangeFilter),
        ('season_type', DropdownChoicesFieldListFilter),
    )

    readonly_fields = ('year', 'season_type',)
    fieldsets = (
        ('Season Indentification', {
            'fields': ('year', 'season_type')}),
        ('Season Dates', {
            'fields': ('start_date', 'end_date')})
    )


@admin.register(Week, site=playlytics_admin_site)
class WeekAdmin(admin.ModelAdmin):
    list_display = ('season', 'week', 'start_date', 'end_date')
    ordering = ('-season__year', 'week')

    list_filter = (
        ('season__year', NumericRangeFilter),
        ('week', NumericRangeFilter),
        ('season__season_type', DropdownChoicesFieldListFilter),
    )

    readonly_fields = ('season', 'week')
    fieldsets = (
        ('Week Identification', {
            'fields': ('season', 'week')}),
        ('Week Dates', {
            'fields': ('start_date', 'end_date')})
    )


@admin.register(Game, site=playlytics_admin_site)
class GameAdmin(admin.ModelAdmin):
    list_display = ("id", "week", "away_team", "away_score", "home_team", "home_score", "result", "status",)
    ordering = ("-week__season__year", "week__week", "game_time")

    search_fields = ("id", "home_team__name", "away_team__name",)
    list_filter = (
        ('week__season__year', NumericRangeFilter),
        ('week__week', NumericRangeFilter),
        ('week__season__season_type', DropdownChoicesFieldListFilter),
        ('status', DropdownChoicesFieldListFilter),
        ('home_team', DropdownRelatedFieldListFilter),
        ('away_team', DropdownRelatedFieldListFilter),
    )

    readonly_fields = ("id", "week", "home_team", "away_team", "result")
    fieldsets = (
        ("Game Identification", {
            "fields": ("id", "home_team", "away_team")}),
        ("Scores", {
            "fields": ("home_score", "away_score", "result")}),
        ("Game Time", {
            "fields": ("week", "game_time", "status")}),
        ("Location", {
            "fields": ("location", "venue")}),
        ("Team Rest Days", {
            "fields": ("home_rest_days", "away_rest_days")}),
    )