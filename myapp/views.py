from django.shortcuts import render,HttpResponse
from django.shortcuts import render
from django.db.models import Q
from .models import Product
from django.db.models import Count  
import time
import json
from django.http import Http404
# Create your views here.
def home(request):
    
    #background_images = ['background1.jpg', 'background2.jpg', 'background3.jpg', 'background4.jpg', 'background5.jpg', 'background6.jpg']
    background_image= 'image (6).png'
    excellent_products = Product.objects.filter(average_rating__gte=4.5).order_by('-average_rating')[:7]
    cache_bust = int(time.time())
    context = {
        'excellent_products': excellent_products,
        'background_image': background_image,
    }
    return render(request,'home.html',context)


def product_search(request):
    query = request.GET.get('q', '')
    products = []
    
    if query:
        products = Product.objects.filter(
            Q(title__icontains=query) |
            Q(store__icontains=query)
        ).order_by('-rating_number')
        
    context = { 
        'query': query,
        'products': products,
    }
    return render(request, 'search.html', context)
def stores_view(request):
    # Get a list of all the unique stores
    stores = Product.objects.values('store').annotate(num_products=Count('id')).order_by('-num_products')

    # Handle search functionality
    query = request.GET.get('q', '')
    if query:
        stores = stores.filter(store__icontains=query)

    context = {
        'stores': stores,
        'query': query,
    }
    return render(request, 'stores.html', context)

def categories_view(request):
    categories = Product.get_categories()
    print("Categories:", json.dumps(categories, indent=2))
    
    query = request.GET.get('q', '')
    if query:
        categories = [
            category for category in categories 
            if query.lower() in category['main_category'].lower()
        ]
    
    context = {
        'categories': categories,
        'query': query,
    }
    return render(request, 'categories.html', context)
def products_view(request):
    top_products = Product.objects.order_by('-average_rating')[:50]
    context = {
        'products': top_products
    }
    return render(request, 'products.html', context)
def product_details(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        reviews = product.get_reviews()
        
        context = {
            'product': product,
            'reviews': reviews,
        }
        return render(request, 'product_details.html', context)
    except Product.DoesNotExist:
        raise Http404("Product does not exist")

