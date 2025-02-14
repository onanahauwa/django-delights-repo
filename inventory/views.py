import random
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError
from .models import Ingredient, MenuItem, RecipeRequirement, Purchase
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db.models import Sum, F, DecimalField
from django.utils.timezone import now
from .forms import IngredientForm, MenuItemForm, RecipeRequirementForm, PurchaseForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout


# Create your views here.
def logout_view(request):
  logout(request)
  return redirect("/accounts/login/")

@login_required
def HomeView(request):
    menu_items = list(MenuItem.objects.all())  # Convert QuerySet to list
    random_items = random.sample(menu_items, min(len(menu_items), 8))  # Pick 6 random items (or less if not enough)
    return render(request, 'inventory/index.html', {'menu_items': random_items})

class IngredientListView(LoginRequiredMixin, ListView):
    model = Ingredient
    template_name = "inventory/ingredients.html"
    context_object_name = "items" 

class MenuListView(LoginRequiredMixin, ListView):
    model = MenuItem
    template_name = "inventory/menu.html"
    context_object_name = "menus" 

    def get_queryset(self):
        return MenuItem.objects.prefetch_related("recipe_requirements")
    
class PurchaseListView(LoginRequiredMixin, ListView):
    model = Purchase
    template_name = "inventory/purchases.html"
    context_object_name = "purchased_items"

class RecipeRequirementView(LoginRequiredMixin, ListView):
    model = RecipeRequirement
    template_name = "inventory/recipe_req.html"
    context_object_name = "recipe_requirement"

    def get_queryset(self):
        menu_item_id = self.kwargs.get("menu_item_id")  # Get menu_item_id from URL
        return RecipeRequirement.objects.filter(menu_item_id=menu_item_id)  # Filter for that menu item

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        menu_item_id = self.kwargs.get("menu_item_id")
        context["menu_item"] = MenuItem.objects.get(id=menu_item_id)  # Pass menu item to template
        return context


class DeleteRecipeRequirement(LoginRequiredMixin, DeleteView):
    model = RecipeRequirement
    template_name = "inventory/delete_recipe.html"
    success_url = "/menu"


class IngredientCreate(LoginRequiredMixin, CreateView):
    model = Ingredient
    template_name = "inventory/add_ingredient.html"
    form_class = IngredientForm

class MenuCreate(LoginRequiredMixin, CreateView):
    model = MenuItem
    template_name = "inventory/add_menu.html"
    form_class = MenuItemForm

class RecipeRequirementCreate(LoginRequiredMixin, CreateView):
    model = RecipeRequirement
    template_name = "inventory/add_recipe_req.html"
    form_class = RecipeRequirementForm

class PurchaseCreate(LoginRequiredMixin, CreateView):
    model = Purchase
    template_name = "inventory/add_purchase.html"
    form_class = PurchaseForm
    success_url = reverse_lazy("purchase")

    def form_valid(self, form):
        purchase = form.save(commit=False)  # Don't save yet
        menu_item = purchase.menu_item  # Get selected menu item

        # Check if enough ingredients are available
        recipe_requirements = RecipeRequirement.objects.filter(menu_item=menu_item)
        insufficient_ingredients = []

        for req in recipe_requirements:
            if req.ingredient.quantity_available < req.quantity_required:
                insufficient_ingredients.append(req.ingredient.name)

        if insufficient_ingredients:
            error_message = f"Not enough stock for: {', '.join(insufficient_ingredients)}."
            form.add_error(None, error_message)  # Add error to form
            messages.error(self.request, error_message)  # Display error message
            return self.form_invalid(form)  # Re-render the form with error

        # Deduct ingredients from stock
        for req in recipe_requirements:
            req.ingredient.quantity_available -= req.quantity_required
            req.ingredient.save()

        purchase.save()  # Now save purchase
        return redirect(self.success_url)  #Redirect to purchase list after success
        
class IngredientUpdate(LoginRequiredMixin, UpdateView):
    model = Ingredient
    template_name = "inventory/update_ingredient.html"
    form_class = IngredientForm

class MenuUpdate(LoginRequiredMixin, UpdateView):
    model = MenuItem
    template_name = "inventory/update_menu.html"
    form_class = MenuItemForm

class ReportsView(LoginRequiredMixin, View):
    template_name = "inventory/reports.html"

    def get(self, request):
        today = now().date()  # Get today's date

        # Calculate total inventory cost
        total_inventory_cost = Ingredient.objects.aggregate(
            total_cost=Sum(F('quantity_available') * F('price_per_unit'), output_field=DecimalField())
        )['total_cost'] or 0  # Default to 0 if None

        # Calculate total revenue (sum of prices of today's purchases)
        total_revenue = Purchase.objects.filter(timestamp__date=today).aggregate(
            total_revenue=Sum('menu_item__price')
        )['total_revenue'] or 0  # Default to 0 if no sales

        # Calculate total cost of ingredients used for today's purchases
        total_cost_of_ingredients = RecipeRequirement.objects.filter(
            menu_item__purchases__timestamp__date=today
        ).aggregate(
            total_cost=Sum(F('quantity_required') * F('ingredient__price_per_unit'), output_field=DecimalField())
        )['total_cost'] or 0  # Default to 0 if None

        # Calculate profit (Revenue - Cost of Ingredients)
        total_profit = total_revenue - total_cost_of_ingredients

        # Get only today's purchase history
        purchases_today = Purchase.objects.filter(timestamp__date=today).select_related('menu_item').order_by('-timestamp')

        context = {
            'total_inventory_cost': total_inventory_cost,
            'total_revenue': total_revenue,
            'total_profit': total_profit,  # New Profit Calculation
            'purchases_today': purchases_today,
        }
        return render(request, self.template_name, context)