from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product
from .forms import ProductForm
from stores.models import Store

# 상품 목록
@login_required
def product_list(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    products = store.products.all()
    
    return render(request, "products/product-list.html", {
        "store": store,
        "products": products,
    })

# 상품 생성
@login_required
def product_create(request, store_id):
    store = get_object_or_404(Store, id=store_id, owner=request.user)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.store = store
            product.save()
            return redirect("products:product-list", store_id=store.id)
    else:
        form = ProductForm()
    return render(request, "products/product-create.html", {"form": form, "store": store})

# 상품 수정
@login_required
def product_update(request, product_id):
    product = get_object_or_404(Product, id=product_id, store__owner=request.user)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect("products:product-list", store_id=product.store.id)
    else:
        form = ProductForm(instance=product)
    return render(request, "products/product-update.html", {"form": form, "store": product.store})

# 상품 삭제
@login_required
def product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id, store__owner=request.user)
    
    if request.method == "POST":
        store_id = product.store.id
        product.delete()
        return redirect("products:product-list", store_id=store_id)
    
    # 삭제 확인 페이지
    return render(request, "products/product-delete.html", {"product": product})

