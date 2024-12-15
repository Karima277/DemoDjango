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
    excellent_products = Product.objects.filter(product_average_rating__gte=4.5).order_by('-product_average_rating')[:7]
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
            Q(product_title__icontains=query) |
            Q(store__icontains=query)
        ).order_by('-product_average_rating')
        
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
    
    top_products = Product.objects.order_by('-product_average_rating')[:50]
    context = {
        'products': top_products
    }
    return render(request, 'products.html', context)
from db_connection import db  
from django.shortcuts import render, get_object_or_404

from django.core.paginator import Paginator


from django.shortcuts import render
from db_connection import db

def product_details(request, product_id):
    # Use the 'sample' collection for products
    product_collection = db['sample']
    
    # Retrieve product details
    product = product_collection.find_one({"product_id": product_id}, {"_id": 0})
    
    if not product:
        return render(request, 'error.html', {
            'message': f'Product with ID {product_id} not found.'
        }, status=404)
    
    # Retrieve reviews for the product (assuming reviews are in the same collection)
    reviews = list(product_collection.find(
        {
            "product_id": product_id,
            "review_title": {"$exists": True}  # Ensure it's a review document
        },
        {
            "_id": 0, 
            "review_title": 1, 
            "review_text": 1, 
            "Sentiment": 1,
            "user_rating": 1
        }
    ))
    
    # Sentiment breakdown
    reviews_count = len(reviews)
    positive_reviews_count = len([r for r in reviews if r.get('Sentiment') == 'positive'])
    neutral_reviews_count = len([r for r in reviews if r.get('Sentiment') == 'neutral'])
    negative_reviews_count = len([r for r in reviews if r.get('Sentiment') == 'negative'])
    
    context = {
        'product': product,
        'reviews': reviews,
        'reviews_count': reviews_count,
        'positive_reviews_count': positive_reviews_count,
        'neutral_reviews_count': neutral_reviews_count,
        'negative_reviews_count': negative_reviews_count,
    }
    
    return render(request, 'product_details.html', context)