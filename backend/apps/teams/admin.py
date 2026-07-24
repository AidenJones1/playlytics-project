from django.contrib import admin

from apps.core.admin import playlytics_admin_site
from apps.core.admin_filters import ConferenceDivisionDropdownFilter
from apps.teams.models import Team

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
