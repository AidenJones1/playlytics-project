from django.contrib import admin

from apps.core.admin import playlytics_admin_site
from apps.core.admin_filters import DropdownRelatedFieldListFilter
from apps.dashboard.models import GameOfTheWeek

@admin.register(GameOfTheWeek, site=playlytics_admin_site)
class GameOfTheWeekAdmin(admin.ModelAdmin):
    list_display = ('week', 'game',)
    list_filter = (
        ('week', DropdownRelatedFieldListFilter),
        ('game', DropdownRelatedFieldListFilter),
    )
    search_fields = ('week__season__year', 'week__week', 'game__home_team__name', 'game__away_team__name')

    readonly_fields = ('week',)
    fieldsets = (
        ('Game of the Week Identification', {
            'fields': ('week', 'game')}),
    )