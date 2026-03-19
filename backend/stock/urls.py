from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('items',     views.StockItemViewSet,     basename='stock-item')
router.register('movements', views.StockMovementViewSet, basename='stock-movement')
router.register('categories', views.CategoryViewSet,     basename='stock-category')

urlpatterns = [path('', include(router.urls))]
