from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.HomeView, name="home"),
    path('home/', views.HomeView, name='index'),
    path("accounts/", include("django.contrib.auth.urls")),
    path("logout/", views.logout_view, name="logout"),
    path('ingredient/', views.IngredientListView.as_view(), name='ingredient'),
    path('menu/', views.MenuListView.as_view(), name='menu'),
    path('purchase/', views.PurchaseListView.as_view(), name='purchase'),
    path('reports/', views.ReportsView.as_view(), name='report'),
    path('recipe_requirements/<int:menu_item_id>/', views.RecipeRequirementView.as_view(), name='recipe_requirements'),
    path('recipe_requirements/<pk>/delete/', views.DeleteRecipeRequirement.as_view(), name='delete_recipe'),
    path('ingredients/new', views.IngredientCreate.as_view(), name='create_ingredient'),
    path('menu/new', views.MenuCreate.as_view(), name='create_menu'),
    path('recipe/new', views.RecipeRequirementCreate.as_view(), name='create_recipe'),
    path('purchase/new', views.PurchaseCreate.as_view(), name='create_purchase'),
    path('ingredient/<pk>/update/', views.IngredientUpdate.as_view(), name='update_ingredient'),
    path('menu/<pk>/update/', views.MenuUpdate.as_view(), name='update_menu'),
    

]