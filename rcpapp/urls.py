from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rcpapp import views


urlpatterns = [
    path("", views.recipes, name="recipes"),
    path("recipe/<int:pk>/", views.recipe, name="recipe"),
    path("render_add_recipe_form/", views.render_add_recipe_form, name="render_add_recipe_form"),
    path("add_recipe/", views.add_recipe, name="add_recipe"),
    path("render_edit_recipe_form/<int:pk>/", views.render_edit_recipe_form, name="render_edit_recipe_form"),
    path("edit_recipe/<int:pk>/", views.edit_recipe, name="edit_recipe"),
    path("render_add_recipe_ingredient_form/<int:pk>/", views.render_add_recipe_ingredient_form, name="render_add_recipe_ingredient_form"),
    path("add_recipe_ingredient/<int:pk>/", views.add_recipe_ingredient, name="add_recipe_ingredient"),
    path("render_edit_recipe_ingredient_form/<int:pk>/", views.render_edit_recipe_ingredient_form, name="render_edit_recipe_ingredient_form"),
    path("edit_recipe_ingredient/<int:pk>/", views.edit_recipe_ingredient, name="edit_recipe_ingredient"),
    path("delete_recipe_ingredient/<int:pk>/", views.delete_recipe_ingredient, name="delete_recipe_ingredient"),





    path("ingredients/", views.ingredients, name="ingredients"),
    path("render_add_ingredient_form/", views.render_add_ingredient_form, name="render_add_ingredient_form"),
    path("add_ingredient/", views.add_ingredient, name="add_ingredient"),
    path("render_edit_ingredient_form/<int:pk>/", views.render_edit_ingredient_form, name="render_edit_ingredient_form"),
    path("edit_ingredient/<int:pk>/", views.edit_ingredient, name="edit_ingredient"),
    path("delete_ingredient/<int:pk>/", views.delete_ingredient, name="delete_ingredient"),
    path("ingredients_select/", views.ingredients_select, name="ingredients_select"),    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
