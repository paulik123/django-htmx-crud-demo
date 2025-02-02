from django import forms

from rcpapp.models import Ingredient, Recipe, RecipeIngredient
from rcpapp.widgets import TomSelectAjaxWidget


class RecipeForm(forms.ModelForm):
	class Meta:
		fields = '__all__'
		model = Recipe

class RecipeFilterForm(forms.Form):
	ingredient = forms.ModelChoiceField(
		queryset=Ingredient.objects.all(),
		required=False,
		label="Contains ingredient",
		widget=TomSelectAjaxWidget(
			url="ingredients_select"
		)
	)


class IngredientForm(forms.ModelForm):
	class Meta:
		fields = '__all__'
		model = Ingredient



class RecipeIngredientForm(forms.ModelForm):
	class Meta:
		fields ='__all__'
		model = RecipeIngredient

		widgets = {
			"recipe": forms.HiddenInput(),
			"ingredient": TomSelectAjaxWidget(
				url="ingredients_select"
			)
		}