from django.urls import path
from .views import *

app_name="products"

urlpatterns = [
    path("product-list/<int:store_id>/", product_list, name="product-list"),
    path("product-create/<int:store_id>/", product_create, name="product-create"),
    path("product-update/<int:product_id>/", product_update, name="product-update"),
    path("product-delete/<int:product_id>/", product_delete, name="product-delete"),
]