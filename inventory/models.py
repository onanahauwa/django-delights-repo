from django.db import models

# Create your models here.
class Ingredient(models.Model):
    name = models.CharField(max_length=30, unique=True)
    quantity_available= models.FloatField()  # Assuming quantity is measured in consistent units (e.g., kg, liters, etc.)
    unit = models.CharField(max_length=30)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)

    def get_absolute_url(self):
        return "/ingredient"

    def __str__(self):
        return f"{self.name} ({self.quantity_available} {self.unit} units available)"

class MenuItem(models.Model):
    name = models.CharField(max_length=30, unique=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    image = models.CharField(max_length=255, default='default.jpg')

    def get_absolute_url(self):
        return "/menu"

    def __str__(self):
        return self.name

class RecipeRequirement(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name="recipe_requirements")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name="used_in_recipes")
    quantity_required = models.FloatField()

    def get_absolute_url(self):
        return "/menu"

    def __str__(self):
        return f"{self.quantity_required} {self.ingredient.unit} of {self.ingredient.name} for {self.menu_item.name}"

class Purchase(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name="purchases")
    timestamp = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return "/purchase"

    def __str__(self):
        return f"Purchased {self.menu_item.name} on {self.timestamp}"
    

