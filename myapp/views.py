from django.shortcuts import render,HttpResponse
from django.shortcuts import render
from django.db.models import Q
from .models import Product
from django.db.models import Count  
# Create your views here.
def home(request):
    excellent_products = Product.objects.filter(average_rating__gte=4.5).order_by('-average_rating')[:7]
    context = {
        'excellent_products': excellent_products
    }
    return render(request,'home.html',context)


def product_search(request):
    query = request.GET.get('q', '')
    products = []
    
    if query:
        products = Product.objects.filter(
            Q(title__icontains=query) |
            Q(store__icontains=query)
        ).order_by('-average_rating')
        
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
    # Get a list of all the unique categories
    categories = Product.objects.values('main_category').annotate(num_products=Count('id')).order_by('-num_products')

    # Handle search functionality
    query = request.GET.get('q', '')
    if query:
        categories = categories.filter(main_category__icontains=query)

    context = {
        'categories': categories,
        'query': query,
    }
    return render(request, 'categories.html', context)

