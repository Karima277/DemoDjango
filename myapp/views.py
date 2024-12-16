from django.shortcuts import render,HttpResponse
from django.shortcuts import render
from django.db.models import Q
from .models import Product
from django.db.models import Count  
import time
import json
from django.http import Http404
from pymongo import MongoClient
# Create your views here.

from db_connection import db  # Ensure this is your MongoDB connection
import json

def home(request):
    # Retrieve from MongoDB directly
    product_collection = db['sample']  # Your MongoDB collection
    
    # Find excellent products directly in MongoDB
    excellent_products_cursor = product_collection.find({
        'product_average_rating': {'$gte': 4.5}
    }).sort('product_average_rating', -1).limit(7)
    
    # Convert cursor to list and process images
    excellent_products = []
    for product in excellent_products_cursor:
        # Process product images
        try:
            if isinstance(product.get('product_images'), str):
                import ast
                product_images = ast.literal_eval(product['product_images'])
            else:
                product_images = product.get('product_images', {})
            
            # Get main image
            main_image = ''
            if isinstance(product_images, dict):
                if product_images.get('hi_res'):
                    main_image = product_images['hi_res'][0]
                elif product_images.get('large'):
                    main_image = product_images['large'][0]
            elif isinstance(product_images, list) and product_images:
                main_image = product_images[0]
            
            # Determine rating status
            rating = product.get('product_average_rating', 0)
            if rating >= 4.5:
                rating_status = "Excellent"
            elif rating >= 4.0:
                rating_status = "Good"
            elif rating >= 3.0:
                rating_status = "Average"
            else:
                rating_status = "Poor"
            
            # Prepare product dictionary
            processed_product = {
                'product_title': product.get('product_title', 'Unnamed Product'),
                'product_average_rating': rating,
                'rating_status': rating_status,
                'main_image': main_image or '/static/default-product.jpg',
                'category': product.get('category', 'Uncategorized'),
                'price': product.get('price', 'N/A')
            }
            
            excellent_products.append(processed_product)
        
        except Exception as e:
            print(f"Error processing product: {e}")
    
    context = {
        'excellent_products': excellent_products,
        'background_image': 'image (6).png',
    }
    
    return render(request, 'home.html', context)

from django.shortcuts import render
from .models import product_collection

def product_search(request):
    query = request.GET.get('q', '')
    products = []

    if query:
        # MongoDB aggregation pipeline to find the number of reviews for each product and order by review count
        pipeline = [
            {
                "$match": {
                    "$or": [
                        {"product_title": {"$regex": query, "$options": "i"}},
                        {"store": {"$regex": query, "$options": "i"}}
                    ]
                }
            },
            {
                "$group": {
                    "_id": "$product_id",  # Group by product_id
                    "product_title": {"$first": "$product_title"},
                    "product_image": {"$first": "$product_images.large"},
                    "category": {"$first": "$category"},
                    "average_rating": {"$first": "$product_average_rating"},
                    "store": {"$first": "$store"},
                    "reviews_count": {"$sum": 1}  # Count the number of reviews for each product
                }
            },
            {
                "$sort": {
                    "reviews_count": -1  # Sort by reviews count in descending order
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "product_id": "$_id",
                    "product_title": 1,
                    "product_image": 1,
                    "category": 1,
                    "average_rating": 1,
                    "store": 1,
                    "reviews_count": 1
                }
            }
        ]
        
        # Execute the aggregation pipeline
        products = list(product_collection.aggregate(pipeline))

    context = {
        'query': query,
        'products': products,
    }
    return render(request, 'search.html', context)

def stores_view(request):
    # Get a list of all the unique stores
    stores = Product.objects.values('store').annotate(num_products=Count('store')).order_by('-num_products')

    # Handle search functionality
    query = request.GET.get('q', '')
    if query:
        stores = stores.filter(store__icontains=query)

    context = {
        'stores': stores,
        'query': query,
    }
    return render(request, 'stores.html', context)

from django.db.models import Count

def categories_view(request):
    # Retrieve all categories, annotating with the number of products in each category
    categories = (
        Product.objects.values('category')  # Use the 'category' field to group products
        .annotate(num_products=Count('category')) # Count the number of products in each category
        .order_by('-num_products')  # Optionally, order categories by the number of products
    )

    context = {
        'categories': categories,
        'query': request.GET.get('search', ''),  # Handle search query if applicable
    }

    return render(request, 'categories.html', context)

import math

def products_view(request):
    top_products = list(product_collection.find().sort('product_average_rating', -1).limit(50))
    client.close()

    # Convert MongoDB documents to a format that can be easily used in the template
    products = []
    for product in top_products:
        try:
            # Clean the price field to handle NaN values
            price = product.get('price', 'N/A')
            if isinstance(price, float) and math.isnan(price):
                price = None  # Replace NaN with None or a default value like 0.0
            
            # Process the product dictionary
            processed_product = {
                'product_id': str(product.get('product_id', product.get('_id'))),  # Handle MongoDB ObjectId
                'product_title': product.get('product_title', 'Unnamed Product'),
                'product_average_rating': product.get('product_average_rating', 0),
                'product_images': product.get('product_images', {}),
                'category': product.get('category', 'Uncategorized'),
                'price': price,  # Pass cleaned price
            }
            products.append(processed_product)
        except Exception as e:
            print(f"Error processing product: {e}")

    context = {
        'products': products
    }
    return render(request, 'products.html', context)




# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['Products']  # Replace 'Products' with your actual DB name
product_collection = db['sample']  # Replace 'sample' with your actual collection name

def product_details(request, product_id):
    # MongoDB aggregation pipeline to calculate sentiment counts and fetch product data
    pipeline = [
        {
            "$match": {
                "product_id": product_id  # Filter by the product_id
            }
        },
        {
            "$group": {
                "_id": "$product_id",  # Group by product_id (unique product identifier)
                "product_title": {"$first": "$product_title"},  # Get the product title
                "product_images": {"$first": "$product_images.large"},  # Get the large product images
                "category": {"$first": "$category"},  # Get the category
                "average_rating": {"$first": "$product_average_rating"},  # Get the average rating
                "store": {"$first": "$store"},  # Get the store
                "positive_reviews": {
                    "$sum": {"$cond": [{"$eq": ["$Sentiment", "positive"]}, 1, 0]}
                },
                "neutral_reviews": {
                    "$sum": {"$cond": [{"$eq": ["$Sentiment", "neutral"]}, 1, 0]}
                },
                "negative_reviews": {
                    "$sum": {"$cond": [{"$eq": ["$Sentiment", "negative"]}, 1, 0]}
                },
            }
        },
        {
            "$project": {
                "_id": 0,  # Exclude the MongoDB `_id` field
                "product_id": "$_id",  # Rename `_id` to `product_id`
                "product_title": 1,
                "product_images": 1,
                "category": 1,
                "average_rating": 1,
                "store": 1,
                "positive_reviews": 1,
                "neutral_reviews": 1,
                "negative_reviews": 1,
            }
        }
    ]
    
    # Apply the aggregation pipeline to get product details and sentiment counts
    product_data = list(product_collection.aggregate(pipeline))

    if not product_data:
        return render(request, '404.html', status=404)  # Optional: handle not found
    
    product = product_data[0]  # Extract the first (and only) product

    # Fetch the reviews for this product
    reviews = list(product_collection.find(
        {"product_id": product_id},
        {"_id": 0, "review_title": 1, "review_text": 1, "Sentiment": 1}
    ))

    return render(request, 'product_details.html', {"product": product, "reviews": reviews})
