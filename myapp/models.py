
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