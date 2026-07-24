from rangefilter.filters import NumericRangeFilter

from django.contrib import admin

from apps.core.admin import playlytics_admin_site
from apps.core.admin_filters import (
    ConferenceDivisionDropdownFilter,
    DropdownChoicesFieldListFilter,
    DropdownRelatedFieldListFilter
)
from apps.teams.models import Team, TeamInjuryReport

@admin.register(Team, site=playlytics_admin_site)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('abbreviation', 'fullname', 'conference', 'division', 'color_1', 'color_2', 'logo')
    ordering = ('abbreviation',)

    search_fields = ('abbreviation', 'fullname')
    list_filter = (ConferenceDivisionDropdownFilter, )

    readonly_fields = ('abbreviation',)
    fieldsets = [
        ('Team Identification', {
            'fields': ('abbreviation', 'fullname', 'nickname', 'logo')}),
        ('Team Colors', {
            'fields': ('color_1', 'color_2', 'color_3', 'color_4')}),
        ('Team Affiliation', {
            'fields': ('conference', 'division')})
    ]


@admin.register(TeamInjuryReport, site=playlytics_admin_site)
class TeamInjuryReportAdmin(admin.ModelAdmin):
    list_display = ('player_name', 'team', 'week', 'injury_status')
    ordering = ('week', 'team')

    search_fields = ('player_name', 'team__abbreviation')
    list_filter = (
        ("week__season__year", NumericRangeFilter),
        ('week__week', NumericRangeFilter),
        ('injury_status', DropdownChoicesFieldListFilter),
        ('team', DropdownRelatedFieldListFilter),
    )

    readonly_fields = ('player_id', 'player_name', 'team', 'week')
    fieldsets = [
        ('Player Information', {
            'fields': ('player_id', 'player_name', 'team', 'week')}),
        ('Injury Information', {
            'fields': ('injury_status',)}),
    ]