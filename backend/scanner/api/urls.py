# backend/scanner/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from scanner.views import PrinterViewSet, print_labels
from scanner.api.views import PrintTemplateViewSet, PrintJobViewSet, PrintLogViewSet

router = DefaultRouter()
router.register(r'printers', PrinterViewSet, basename='printer')
router.register(r'templates', PrintTemplateViewSet, basename='print-template')
router.register(r'print-jobs', PrintJobViewSet, basename='print-job')

urlpatterns = [
    path('', include(router.urls)),
    ## Logs d'impression (lecture seule)
    path('logs/', PrintLogViewSet.as_view({'get': 'list'}), name='print-logs'),
    path('print-logs/', PrintLogViewSet.as_view({'get': 'list'}), name='print-logs'),
]
