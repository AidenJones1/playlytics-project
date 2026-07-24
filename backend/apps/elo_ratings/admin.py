from rangefilter.filters import NumericRangeFilter

from django.contrib import admin

from apps.core.admin import playlytics_admin_site
from apps.core.admin_filters import DropdownRelatedFieldListFilter
from apps.elo_ratings.models import TeamELORating

@admin.register(TeamELORating, site=playlytics_admin_site)
class TeamELORatingAdmin(admin.ModelAdmin):
    list_display = ('team', 'game', 'ratings_before', 'ratings_after', 'gained', 'average_opponent_ratings', 'highest_ratings', 'lowest_ratings', 'average_gain')
    ordering = ('-game__week__season__year', 'game__week__week', 'game__game_time', 'game_id')

    search_fields = ('team__name', 'game__name')
    list_filter = (
        ('game__week__season__year', NumericRangeFilter),
        ('game__week__week', NumericRangeFilter),
        ('ratings_before', NumericRangeFilter),
        ('ratings_after', NumericRangeFilter),
        ('team', DropdownRelatedFieldListFilter),
    )
    
    readonly_fields = ('game', 'team')
    fieldsets = (
        ('Basic Information', {'fields': ('game', 'team')}),
        ('Ratings Information', {'fields': ('ratings_before', 'ratings_after', 'gained', 'average_opponent_ratings', 'highest_ratings', 'lowest_ratings', 'average_gain')}),
    )