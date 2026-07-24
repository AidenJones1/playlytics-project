from rangefilter.filters import NumericRangeFilter

from django.contrib import admin

from apps.core.admin import playlytics_admin_site
from apps.core.admin_filters import DropdownRelatedFieldListFilter, DropdownChoicesFieldListFilter
from apps.stats.models import TeamGameStats

@admin.register(TeamGameStats, site=playlytics_admin_site)
class TeamGameStatsAdmin(admin.ModelAdmin):
    list_display = ('game', 'team', 'rushing_attempts', 'rushing_yards', 'passing_attempts', 'completed_passes', 'passing_yards', 'rushing_touchdowns', 'passing_touchdowns', 'sacks_allowed', 'interceptions_thrown', 'fumbles_lost', 'total_epa_gained', 'successful_plays')
    ordering = ('-game__week__season__year', 'game__week__week', 'game__game_time')

    list_filter = (
        ('game__week__season__year', NumericRangeFilter),
        ('game__week__week', NumericRangeFilter),
        ('team', DropdownRelatedFieldListFilter),
    )

    readonly_fields = ("game", "team")
    fieldsets = [
        ("Game and Team Information", {
            "fields": ("game", "team")}),
        ("Stats", {
            "fields": ("rushing_attempts", "rushing_yards", "passing_attempts", "completed_passes", "passing_yards", "rushing_touchdowns", "passing_touchdowns", "sacks_allowed", "interceptions_thrown", "fumbles_lost", "total_epa_gained", "successful_plays")})
    ]