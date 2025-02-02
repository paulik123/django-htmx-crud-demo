from django.forms.models import ModelChoiceIterator
from django import forms
from django.urls import reverse
from django.db.models import Q
import json


class TomSelectAjaxWidget(forms.Select):
    def __init__(self, url, create=None, dependent_fields = [], url_params=None, get_params=None, **kwargs,):
        self.url_params=url_params
        self.get_params=get_params
        self.url = url
        self.create = create
        self.dependent_fields = dependent_fields
        super().__init__(**kwargs)

    def optgroups(self, name, value, attrs=None):
        """Return only selected options and set QuerySet from `ModelChoicesIterator`."""
        default = (None, [], 0)
        groups = [default]
        has_selected = False
        selected_choices = {str(v) for v in value}
        if not self.is_required and not self.allow_multiple_selected:
            default[1].append(self.create_option(name, "", "", False, 0))
        if not isinstance(self.choices, ModelChoiceIterator):
            return super().optgroups(name, value, attrs=attrs)
        selected_choices = {
            c for c in selected_choices if c not in self.choices.field.empty_values
        }
        field_name = self.choices.field.to_field_name or "pk"
        query = Q(**{"%s__in" % field_name: selected_choices})
        for obj in self.choices.queryset.filter(query):
            option_value = self.choices.choice(obj)[0]
            option_label = str(obj)

            selected = str(option_value) in value and (
                has_selected is False or self.allow_multiple_selected
            )
            if selected is True and has_selected is False:
                has_selected = True
            index = len(default[1])
            subgroup = default[1]
            subgroup.append(
                self.create_option(
                    name, option_value, option_label, selected_choices, index
                )
            )

        return groups

    def get_autocomplete_url(self):
        """Hook to specify the autocomplete URL."""
        if self.url_params:
            return reverse(self.url, kwargs=self.url_params)
        return reverse(self.url)
    
    def build_attrs(self, base_attrs, extra_attrs=None):
        """Build HTML attributes for the widget."""
        attrs = super().build_attrs(base_attrs, extra_attrs)

        attrs.update({
            "is-tomselect": True,
            "data-autocomplete-url": self.get_autocomplete_url(),
            "data-value-field": "value",
            "data-label-field": "text"
        })
        if self.create:
            attrs["data-create"] = "true"
        if self.dependent_fields:
            attrs["data-dependent-fields"] = "__".join(self.dependent_fields)
        if self.get_params:
            attrs['data-get-params'] = json.dumps(self.get_params)
        return attrs
    

class MultipleSelectionMixin:
    """Enable multiple selection with TomSelect."""

    def build_attrs(self, base_attrs, extra_attrs=None):
        """Build HTML attributes for the widget."""
        attrs = super().build_attrs(base_attrs, extra_attrs)  # noqa
        attrs["is-multiple"] = True
        return attrs


class TomSelectMultipleAjaxWidget(MultipleSelectionMixin, TomSelectAjaxWidget, forms.SelectMultiple):
    ...
