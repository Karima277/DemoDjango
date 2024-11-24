from django.urls import path
from . import views
# urlpatterns=[
#     path("", views.home,name="home")
# ]

urlpatterns = [
    path('', views.product_search, name='product_search'),
]