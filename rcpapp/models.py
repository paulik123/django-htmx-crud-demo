from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.core.exceptions import ValidationError

from decimal import Decimal


class Ingredient(models.Model):
	name = models.CharField(max_length=255, unique=True, verbose_name="Name")
	description = models.CharField(max_length=255, blank=True, null=True, verbose_name="Description")

	carbohydrates_per_100_gr = models.DecimalField(
		max_digits=10,
		decimal_places=2,
		validators=[MinValueValidator(Decimal("0.0")), MaxValueValidator(Decimal("100.0"))],
		verbose_name="Carbohydrates / 100gr",
	)
	sugars_per_100_gr = models.DecimalField(
		max_digits=10,
		decimal_places=2,
		validators=[MinValueValidator(Decimal("0.0")), MaxValueValidator(Decimal("100.0"))],
		verbose_name="Sugars / 100gr",
	)
	lipids_per_100_gr = models.DecimalField(
		max_digits=10,
		decimal_places=2,
		validators=[MinValueValidator(Decimal("0.0")), MaxValueValidator(Decimal("100.0"))],
		verbose_name="Lipids / 100gr",
	)
	fatty_acids_per_100_gr = models.DecimalField(
		max_digits=10,
		decimal_places=2,
		validators=[MinValueValidator(Decimal("0.0")), MaxValueValidator(Decimal("100.0"))],
		verbose_name="Fatty acids / 100gr",
	)
	proteins_per_100_gr = models.DecimalField(
		max_digits=10,
		decimal_places=2,
		validators=[MinValueValidator(Decimal("0.0")), MaxValueValidator(Decimal("100.0"))],
		verbose_name="Proteins / 100gr",
	)
	fiber_per_100_gr = models.DecimalField(
		max_digits=10,
		decimal_places=2,
		validators=[MinValueValidator(Decimal("0.0")), MaxValueValidator(Decimal("100.0"))],
		verbose_name="Fiber / 100gr",
	)
	salt_per_100_gr = models.DecimalField(
		max_digits=10,
		decimal_places=2,
		validators=[MinValueValidator(Decimal("0.0")), MaxValueValidator(Decimal("100.0"))],
		verbose_name="Salt / 100gr",
	)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = "Ingredient"
		verbose_name_plural = "Ingredients"
		ordering = ["name"]


class Recipe(models.Model):
	name = models.CharField(max_length=255, unique=True, verbose_name="Name")
	description = models.CharField(max_length=255, blank=True, null=True, verbose_name="Description")

	carbohydrates = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"), editable=False)
	sugars = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"), editable=False)
	lipids = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"), editable=False)
	fatty_acids = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"), editable=False)
	proteins = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"), editable=False)
	fiber = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"), editable=False)
	salt = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"), editable=False)
	calories = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"), editable=False)

	def save(self, *args, **kwargs):
		if self.id:
			totals = self.ingredients.aggregate(
				carbohydrates=Coalesce(Sum("carbohydrates"), Decimal('0')),
				fatty_acids=Coalesce(Sum("fatty_acids"), Decimal('0')),
				proteins=Coalesce(Sum("proteins"), Decimal('0')),
				lipids=Coalesce(Sum("lipids"), Decimal('0')),
				sugars=Coalesce(Sum("sugars"), Decimal('0')),
				fiber=Coalesce(Sum("fiber"), Decimal('0')),
				salt=Coalesce(Sum("salt"), Decimal('0')),
				calories=Coalesce(Sum("calories"), Decimal('0')),
			)

			self.carbohydrates = totals["carbohydrates"]
			self.fatty_acids = totals["fatty_acids"]
			self.proteins = totals["proteins"]
			self.lipids = totals["lipids"]
			self.sugars = totals["sugars"]
			self.fiber = totals["fiber"]
			self.salt = totals["salt"]
			self.calories = totals["calories"]

		super().save(*args, **kwargs)

	def __str__(self):
		return self.name

	class Meta:
		ordering = ["name"]
		verbose_name = "Produs"
		verbose_name_plural = "Produse"


class RecipeIngredient(models.Model):
	recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="ingredients")
	ingredient = models.ForeignKey(
		Ingredient, on_delete=models.PROTECT, related_name="recipes", verbose_name="Ingredient"
	)
	grams = models.DecimalField(
		max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))], verbose_name="Grams"
	)

	carbohydrates = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
	sugars = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
	lipids = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
	fatty_acids = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
	proteins = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
	fiber = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
	salt = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
	calories = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

	def save(self, *args, **kwargs):
		self.carbohydrates = self.grams / Decimal("100.0") * self.ingredient.carbohydrates_per_100_gr
		self.fatty_acids = self.grams / Decimal("100.0") * self.ingredient.fatty_acids_per_100_gr
		self.proteins = self.grams / Decimal("100.0") * self.ingredient.proteins_per_100_gr
		self.lipids = self.grams / Decimal("100.0") * self.ingredient.lipids_per_100_gr
		self.sugars = self.grams / Decimal("100.0") * self.ingredient.sugars_per_100_gr
		self.fiber = self.grams / Decimal("100.0") * self.ingredient.fiber_per_100_gr
		self.salt = self.grams / Decimal("100.0") * self.ingredient.salt_per_100_gr
		self.calories = (
			self.lipids * Decimal("9.00")
			+ self.carbohydrates * Decimal("4.00")
			+ self.fiber * Decimal("2.00")
			+ self.proteins * Decimal("4.00")
		)

		super().save(*args, **kwargs)

		if hasattr(self, 'recipe'):
			self.recipe.save()

	def delete(self, *args, **kwargs):
		super().delete(*args, **kwargs)

		self.recipe.save()

	def clean(self):
		duplicate_query = RecipeIngredient.objects.filter(recipe=self.recipe, ingredient=self.ingredient)
		if self.id:
			duplicate_query = duplicate_query.exclude(id=self.id)
		if duplicate_query.exists():
			raise ValidationError({"ingredient": "You cannot add the same ingredient twice."})

	def __str__(self):
		return f"{self.ingredient}"

	class Meta:
		ordering = ["-grams"]
		verbose_name = "Recipe ingredient"
		verbose_name_plural = "Recipe ingredients"
