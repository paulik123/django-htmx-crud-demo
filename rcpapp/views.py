import json

from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Prefetch, Q
from django.http.response import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from rcpapp.forms import IngredientForm, RecipeForm, RecipeIngredientForm, RecipeFilterForm
from rcpapp.models import Ingredient, Recipe, RecipeIngredient


####### RECIPES #######
def recipes(request):
	filters = Q()

	search = request.GET.get("search", None)
	if search:
		filters &= Q(name__icontains=search) | Q(description__icontains=search)

	ingredient = request.GET.get("ingredient", None)
	if ingredient:
		filters &= Q(ingredients__ingredient=ingredient)

	order_by = request.GET.get("order_by", "-id")

	recipes = Recipe.objects.filter(filters).order_by(order_by).distinct()

	page = request.GET.get("page", 1)
	paginator = Paginator(recipes, 15)
	page_obj = paginator.get_page(page)
	min_page = min(paginator.num_pages, int(page)) if paginator.count else 1

	if "HX-Request" in request.headers:
		return render(
			request,
			"rcpapp/recipes.html#recipes_table",
			{
				"page_obj": page_obj,
				"page_range": paginator.get_elided_page_range(min_page, on_each_side=1, on_ends=1),
				"order_by": order_by,
			},
		)

	return render(
		request,
		"rcpapp/recipes.html",
		{
			"module": "Food",
			"title": "Recipes",
			"page_obj": page_obj,
			"page_range": paginator.get_elided_page_range(min_page, on_each_side=1, on_ends=1),
			"order_by": order_by,
			"filters_form": RecipeFilterForm(initial=request.GET),
		},
	)


def render_add_recipe_form(request):
	response = render(
		request,
		"rcpapp/recipes.html#add_recipe_form",
		{"form": RecipeForm()},
	)
	response["HX-Trigger"] = "open.offcanvas"
	return response


@require_http_methods(["POST"])
def add_recipe(request):
	form = RecipeForm(request.POST)
	if not form.is_valid():
		return render(request, "rcpapp/recipes.html#add_recipe_form", {"form": form})

	try:
		with transaction.atomic():
			recipe = form.save()

			response = HttpResponse("")
			response["HX-Redirect"] = reverse("recipe", kwargs={"pk": recipe.id})
			messages.success(request, "Success!")
			return response
	except Exception as e:
		import traceback

		traceback.print_exc()
		return HttpResponseBadRequest(f"{e}")


def recipe(request, pk):
	recipe = get_object_or_404(Recipe, pk=pk)

	context = {
		"recipe": recipe,
	}

	template = "rcpapp/recipe.html"
	if "HX-Request" in request.headers:
		part = request.GET.get("part", "details")
		match part:
			case "details":
				template = "rcpapp/recipe.html#details"
			case "nutrition":
				template = "rcpapp/recipe.html#nutrition"
			case "ingredients":
				template = "rcpapp/recipe.html#ingredients"
	else:
		context["module"] = f"Food"
		context["title"] = f"{recipe}"

	return render(request, template, context)


def render_edit_recipe_form(request, pk):
	recipe = get_object_or_404(Recipe, pk=pk)

	response = render(
		request,
		"rcpapp/recipe.html#edit_recipe_form",
		{"recipe": recipe, "form": RecipeForm(instance=recipe)},
	)
	response["HX-Trigger"] = "open.offcanvas"
	return response


@require_http_methods(["POST"])
def edit_recipe(request, pk):
	recipe = get_object_or_404(Recipe, pk=pk)

	form = RecipeForm(request.POST, instance=recipe)
	if not form.is_valid():
		return render(request, "rcpapp/recipe.html#edit_recipe_form", {"recipe": recipe, "form": form})
	
	try:
		with transaction.atomic():
			recipe = form.save()

			response = HttpResponse("")
			response["X-Success"] = f"Success!"
			response["HX-Trigger"] = json.dumps(
				{
					"close.offcanvas": 1,
					"refresh.recipe.details": 1,
				}
			)

			return response
	except Exception as e:
		return HttpResponseBadRequest(f"{e}")


def render_add_recipe_ingredient_form(request, pk):
	recipe = get_object_or_404(Recipe, pk=pk)
	response = render(
		request,
		"rcpapp/recipe.html#add_recipe_ingredient_form",
		{"recipe": recipe, "form": RecipeIngredientForm(initial={"recipe": recipe})},
	)
	response["HX-Trigger"] = "open.offcanvas"
	return response


@require_http_methods(["POST"])
def add_recipe_ingredient(request, pk):
	recipe = get_object_or_404(Recipe, pk=pk)

	form = RecipeIngredientForm(request.POST)
	if not form.is_valid():
		return render(request, "rcpapp/recipe.html#add_recipe_ingredient_form", {"recipe": recipe, "form": form})
	try:
		with transaction.atomic():
			recipe_ingredient = form.save()

			response = HttpResponse("")
			response["X-Success"] = f"Success!"
			response["HX-Trigger"] = json.dumps(
				{
					"close.offcanvas": 1,
					"refresh.recipe.ingredients": 1,
					"refresh.recipe.nutrition": 1
				}
			)

			return response
	except Exception as e:
		return HttpResponseBadRequest(f"{e}")


def render_edit_recipe_ingredient_form(request, pk):
	recipe_ingredient = get_object_or_404(RecipeIngredient, pk=pk)

	response = render(
		request,
		"rcpapp/recipe.html#edit_recipe_ingredient_form",
		{"recipe_ingredient": recipe_ingredient, "form": RecipeIngredientForm(instance=recipe_ingredient)},
	)
	response["HX-Trigger"] = "open.offcanvas"
	return response


@require_http_methods(["POST"])
def edit_recipe_ingredient(request, pk):
	recipe_ingredient = get_object_or_404(RecipeIngredient, pk=pk)

	form = RecipeIngredientForm(request.POST, instance=recipe_ingredient)
	if not form.is_valid():
		return render(
			request,
			"rcpapp/recipe.html#edit_recipe_ingredient_form",
			{"recipe_ingredient": recipe_ingredient, "form": form},
		)
	try:
		with transaction.atomic():
			recipe_ingredient = form.save()

			response = HttpResponse("")
			response["X-Success"] = f"Success!"
			response["HX-Trigger"] = json.dumps(
				{
					"close.offcanvas": 1,
					"refresh.recipe.ingredients": 1,
					"refresh.recipe.nutrition": 1
				}
			)

			return response
	except Exception as e:
		return HttpResponseBadRequest(f"{e}")

@require_http_methods(["DELETE"])
def delete_recipe_ingredient(request, pk):
	recipe_ingredient = get_object_or_404(RecipeIngredient, pk=pk)

	try:
		recipe_ingredient.delete()

		response = HttpResponse("")
		response["X-Success"] = "Success!"
		response["HX-Trigger"] = json.dumps(
			{
				"refresh.recipe.ingredients": 1,
				"refresh.recipe.nutrition": 1
			}
		)
		return response
	except Exception as e:
		return HttpResponseBadRequest(f"{e}")
	

####### INGREDIENTS #######
def ingredients(request):
	filters = Q()

	search = request.GET.get("search", None)
	if search:
		filters &= Q(name__icontains=search) | Q(description__icontains=search)

	order_by = request.GET.get("order_by", "-id")

	ingredients = Ingredient.objects.filter(filters).order_by(order_by)

	page = request.GET.get("page", 1)
	paginator = Paginator(ingredients, 15)
	page_obj = paginator.get_page(page)
	min_page = min(paginator.num_pages, int(page)) if paginator.count else 1

	if "HX-Request" in request.headers:
		return render(
			request,
			"rcpapp/ingredients.html#ingredients_table",
			{
				"page_obj": page_obj,
				"page_range": paginator.get_elided_page_range(min_page, on_each_side=1, on_ends=1),
				"order_by": order_by,
			},
		)

	return render(
		request,
		"rcpapp/ingredients.html",
		{
			"module": "Food",
			"title": "Ingredients",
			"page_obj": page_obj,
			"page_range": paginator.get_elided_page_range(min_page, on_each_side=1, on_ends=1),
			"order_by": order_by,
			# "filters_form": OfferFilterForm(initial=request.GET),
		},
	)


def render_add_ingredient_form(request):
	response = render(
		request,
		"rcpapp/ingredients.html#add_ingredient_form",
		{"form": IngredientForm()},
	)
	response["HX-Trigger"] = "open.offcanvas"
	return response


@require_http_methods(["POST"])
def add_ingredient(request):
	form = IngredientForm(request.POST)
	if not form.is_valid():
		return render(request, "rcpapp/ingredients.html#add_ingredient_form", {"form": form})
	try:
		with transaction.atomic():
			ingredient = form.save()

			response = HttpResponse("")
			response["X-Success"] = f"Success!"

			response["HX-Trigger"] = json.dumps(
				{
					"close.offcanvas": 1,
					"refresh.ingredients": 1,
				}
			)

			return response
	except Exception as e:
		return HttpResponseBadRequest(f"{e}")


def render_edit_ingredient_form(request, pk):
	ingredient = get_object_or_404(Ingredient, pk=pk)

	response = render(
		request,
		"rcpapp/ingredients.html#edit_ingredient_form",
		{"ingredient": ingredient, "form": IngredientForm(instance=ingredient)},
	)
	response["HX-Trigger"] = "open.offcanvas"
	return response


@require_http_methods(["POST"])
def edit_ingredient(request, pk):
	ingredient = get_object_or_404(Ingredient, pk=pk)

	form = IngredientForm(request.POST, instance=ingredient)
	if not form.is_valid():
		return render(request, "rcpapp/ingredients.html#edit_ingredient_form", {"ingredient": ingredient, "form": form})
	try:
		with transaction.atomic():
			ingredient = form.save()

			response = HttpResponse("")
			response["X-Success"] = f"Success!"
			response["HX-Trigger"] = json.dumps(
				{
					"close.offcanvas": 1,
					"refresh.ingredients": 1,
				}
			)

			return response
	except Exception as e:
		return HttpResponseBadRequest(f"{e}")

@require_http_methods(["DELETE"])
def delete_ingredient(request, pk):
	ingredient = get_object_or_404(Ingredient, pk=pk)

	return HttpResponseBadRequest("Deleting ingredients is not allowed in this demo but you get the idea.")

	try:
		ingredient.delete()

		response = HttpResponse("")
		response["X-Success"] = "Success!"
		response["HX-Trigger"] = json.dumps(
			{
				"refresh.ingredients": 1,
			}
		)
		return response
	except Exception as e:
		return HttpResponseBadRequest(f"{e}")


def ingredients_select(request):
	search = request.GET.get("q", "")

	ingredients = Ingredient.objects.filter(Q(name__icontains=search) | Q(description__icontains=search))

	page = request.GET.get("page", 1)
	paginator = Paginator(ingredients, 10)
	page = paginator.get_page(page)
	return JsonResponse(
		{
			"results": [{"text": client.name, "value": client.id} for client in page.object_list],
			"page": page.number,
			"has_more": page.has_next(),
		}
	)
