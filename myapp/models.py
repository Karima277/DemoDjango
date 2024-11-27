
from django.db import models
import json

class Product(models.Model):
    main_category = models.CharField(max_length=100)
    title = models.CharField(max_length=500)
    average_rating = models.FloatField(null=True)
    rating_number = models.IntegerField(null=True)
    price = models.CharField(max_length=50, null=True)
    store = models.CharField(max_length=200, null=True)
    details = models.JSONField(null=True)
    parent_asin = models.CharField(max_length=50)
    images = models.JSONField(null=True)

    def get_rating_status(self):
        if self.average_rating is None:
            return "No ratings"
        elif self.average_rating >= 4.5:
            return "Excellent"
        elif self.average_rating >= 4.0:
            return "Good"
        elif self.average_rating >= 3.0:
            return "Average"
        else:
            return "Poor"
    
    #images


    def get_main_image(self):
        """Get the main image URL"""
        try:
            if not self.images:
                return None

            
            for img_type in ['hi_res', 'large', 'thumb']:
                if self.images.get(img_type) and len(self.images[img_type]) > 0:
                    return self.images[img_type][0]

            return None
        except Exception as e:
            print(f"Error getting main image: {str(e)}")
            return None

    def get_all_images(self):
        """Get all available images"""
        try:
            if not self.images:
                return []

            all_images = set() 
            
            # to display all images
            for img_type in ['hi_res', 'large', 'thumb']:
                if self.images.get(img_type):
                    all_images.update(self.images[img_type])

            return list(all_images)
        except Exception as e:
            print(f"Error getting all images: {str(e)}")
            return []
        
    @classmethod
    def get_categories(cls):
        """
        Retrieve unique categories with their product counts and first product's image
        """
        # Get unique categories and their counts
        categories = cls.objects.values('main_category') \
            .annotate(num_products=models.Count('id')) \
            .order_by('-num_products')
        
        # Enhance each category with the first product's image
        for category in categories:
            # Find the first product in this category
            first_product = cls.objects.filter(
                main_category=category['main_category']
            ).first()
            
            # Get the image for the first product
            category_image = first_product.get_main_image() if first_product else None
            
            # Add image to the category dictionary
            category['category_image'] = category_image
        
        return list(categories)
    def get_reviews(self, limit=5):
        """
        Retrieve up to 5 reviews for the product
        Uses parent_asin to match reviews
        """
        return Review.objects.filter(parent_asin=self.parent_asin).order_by('-helpful_vote')[:limit]
class Review(models.Model):
    rating = models.FloatField()
    title = models.CharField(max_length=500, null=True)
    text = models.TextField()
    images = models.JSONField(null=True)
    asin = models.CharField(max_length=50)
    parent_asin = models.CharField(max_length=50)
    user_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField()
    helpful_vote = models.IntegerField(default=0)
    verified_purchase = models.BooleanField(default=False)

    class Meta:
        ordering = ['-helpful_vote']
