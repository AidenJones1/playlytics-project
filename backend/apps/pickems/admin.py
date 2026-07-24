from rangefilter.filters import NumericRangeFilter, DateRangeFilter

from django.contrib import admin

from apps.core.admin import playlytics_admin_site
from apps.core.admin_filters import DropdownChoicesFieldListFilter, DropdownRelatedFieldListFilter
from apps.pickems.models import GamePickem, UserPick, PickemGroup, PickemGroupMember

@admin.register(GamePickem, site=playlytics_admin_site)
class GamePickemAdmin(admin.ModelAdmin):
    list_display = ('game', 'status', 'opens_at', 'closes_at')
    ordering = ('-game__week__season__year', 'game__week__week', 'game__game_time')

    search_fields = ('game__id',)
    list_filter = (
        ('game__week__season__year', NumericRangeFilter),
        ('game__week__week', NumericRangeFilter),
        ('status', DropdownChoicesFieldListFilter),
        ('game__home_team', DropdownRelatedFieldListFilter),
        ('game__away_team', DropdownRelatedFieldListFilter),
    )

    readonly_fields = ('game',)
    fieldsets = (
        ('Game Pickem Info', {
            'fields': ('game', 'status', 'opens_at', 'closes_at')}),
    )


@admin.register(UserPick, site=playlytics_admin_site)
class UserPickAdmin(admin.ModelAdmin):
    list_display = ('id', 'pickem__game', 'user', 'team', 'created_at', 'updated_at')
    ordering = ('-pickem__game__week__season__year', 'pickem__game__week__week', 'pickem__game__game_time')

    search_fields = ('pickem__game__id', 'user__username', 'team__name')
    list_filter = (
        ('pickem__game__week__season__year', NumericRangeFilter),
        ('pickem__game__week__week', NumericRangeFilter),
        ('pickem__status', DropdownChoicesFieldListFilter),
        ('team', DropdownRelatedFieldListFilter),
    )

    readonly_fields = ('pickem', 'created_at', 'updated_at')
    fieldsets = (
        ('User Pick Info', {
            'fields': ('pickem', 'user', 'team', 'created_at', 'updated_at')}),
    )


@admin.register(PickemGroup, site=playlytics_admin_site)
class PickemGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'group_key', 'is_private', 'invite_code', 'max_members', 'created_at')
    ordering = ('-created_at',)

    search_fields = ('name', 'invite_code')
    list_filter = (('created_at', DateRangeFilter),)

    readonly_fields = ('created_at','group_key', 'invite_code',)
    fieldsets = (
        ("Pickem Group Information", {
            'fields': ('name','invite_code', 'group_key', 'max_members')}),
        ("Privacy Settings", {
            'fields': ('is_private',)}),
        ("Dates", {
            'fields': ('created_at',)}),
    )


@admin.register(PickemGroupMember, site=playlytics_admin_site)
class PickemGroupMemberAdmin(admin.ModelAdmin):
    list_display = ('group', 'user', 'role', 'joined_at')
    ordering = ('-joined_at',)

    search_fields = ('group__name', 'user__username', 'role')
    list_filter = (
        ('role', DropdownChoicesFieldListFilter),
        ('joined_at', DateRangeFilter),
    )

    readonly_fields = ('joined_at', 'group', 'user', 'role')
    fieldsets = (
        ("Pickem Group Member Information", {
            'fields': ('group', 'user', 'role', 'joined_at')}),
    )