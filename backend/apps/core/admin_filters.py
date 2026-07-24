from django.contrib import admin
from django.contrib.admin.filters import ChoicesFieldListFilter, FieldListFilter

from apps.teams.choices import CONFERENCE_DIVISION_CHOICES, Conferences, Divisions


class DropdownChoicesFieldListFilter(ChoicesFieldListFilter):
	"""Force dropdown rendering for all choice-based admin field filters."""

	template = "admin/dropdown_filter.html"


FieldListFilter.register(
	lambda field: bool(getattr(field, "flatchoices", ())),
	DropdownChoicesFieldListFilter,
	take_priority=True,
)


class DropdownRelatedFieldListFilter(admin.RelatedFieldListFilter):
	"""Force dropdown rendering for related-field admin filters."""

	template = "admin/dropdown_filter.html"


FieldListFilter.register(
	lambda field: bool(getattr(field, "remote_field", None)),
	DropdownRelatedFieldListFilter,
	take_priority=True,
)

class ChoiceDropdownFilter(admin.SimpleListFilter):
	"""Render choice-based admin filters as a dropdown in every case."""

	template = "admin/dropdown_filter.html"

	def lookups(self, request, model_admin):
		field = model_admin.model._meta.get_field(self.parameter_name)
		return field.flatchoices

	def queryset(self, request, queryset):
		if self.value() is None:
			return queryset

		return queryset.filter(**{self.parameter_name: self.value()})


class ConferenceDivisionDropdownFilter(ChoiceDropdownFilter):
	title = "conference/division"
	parameter_name = "conference_division"

	def lookups(self, request, model_admin):
		return CONFERENCE_DIVISION_CHOICES

	def queryset(self, request, queryset):
		selected_value = self.value()
		if selected_value is None:
			return queryset

		conference_values = {value for value, _label in Conferences.choices}
		division_values = {value for value, _label in Divisions.choices}

		if selected_value in conference_values:
			return queryset.filter(conference=selected_value)

		if selected_value in division_values:
			return queryset.filter(division=selected_value)

		return queryset
