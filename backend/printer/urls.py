from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.viewsets import PrintLabelViewSet
from printer  import views
from printer.api import viewsets as api_views

router = DefaultRouter()
router.register(r'labels', PrintLabelViewSet, basename='print-label')

urlpatterns = [
    path('', include(router.urls)),
    # GET  /api/printer/labels/          → list (optionnel)
    # POST /api/printer/labels/          → create (imprimer)
    # GET  /api/printer/labels/status/   → status (diagnostic)
 # Print Management
    ## Admin URLs for print management
    ##path('admin/print-templates/', api_views.PrintTemplateListView.as_view(), name='admin_print_templates'),
    # API URLs for print management
    path('templates/', api_views.PrintTemplateViewSet.as_view({'get': 'list', 'post': 'create'}), name='print-templates'),
    path('templates/<int:pk>/', api_views.PrintTemplateViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='print-template-detail'),

    path('printers/', api_views.PrinterViewSet.as_view({'get': 'list', 'post': 'create'}), name='printers'),
    path('printers/<int:pk>/', api_views.PrinterViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='printer-detail'),
    path('jobs/', api_views.PrintJobViewSet.as_view({'get': 'list', 'post': 'create'}), name='print-jobs'),
    path('jobs/<int:pk>/', api_views.PrintJobViewSet.as_view({'get': 'retrieve'}), name='print-job-detail'),
    path('print-labels/', views.print_labels, name='print-labels'),
    #
]