from django.shortcuts import render,HttpResponse
from django.shortcuts import render
from django.db.models import Q
from .models import Product

# Create your views here.
def home(request):
    return render(request,'home.html')


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


