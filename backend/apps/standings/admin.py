from rangefilter.filters import NumericRangeFilter

from django.contrib import admin

from apps.core.admin import playlytics_admin_site
from apps.core.admin_filters import DropdownRelatedFieldListFilter
from apps.standings.models import TeamStandings

@admin.register(TeamStandings, site=playlytics_admin_site)
class TeamStandingsAdmin(admin.ModelAdmin):
    list_display = ("team", "week", "wins", "losses", "percentage", "point_differential", "streak")
    ordering = ("-week__season__year", "week__week", "-wins", "losses",)

    search_fields = ("team__name", "team__abbreviation",)
    list_filter = (
        ('week__season__year', NumericRangeFilter),
        ('week__week', NumericRangeFilter),
        ("team", DropdownRelatedFieldListFilter),
    )

    readonly_fields = ("percentage", "team", "week")
    fieldsets = (
        ("Team and Week", {
            "fields": ("team", "week")}),
        ("Overall Record", {
            "fields": ("wins", "losses", "ties", "percentage", "point_differential", "streak")}),
        ("Conference Record", {
            "fields": ("conference_wins", "conference_losses", "conference_ties")}),
        ("Division Record", {
            "fields": ("division_wins", "division_losses", "division_ties")}),
        ("Home Record", {
            "fields": ("home_wins", "home_losses", "home_ties")}),
        ("Away Record", {
            "fields": ("away_wins", "away_losses", "away_ties")}),
    )