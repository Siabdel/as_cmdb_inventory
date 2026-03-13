from django.urls import path
from . import views

urlpatterns = [
    path('scan/<uuid:uuid_token>/',       views.resolve_qr,    name='resolve-qr'),
    path('assets/<int:asset_id>/regen-qr/', views.regenerate_qr, name='regenerate-qr'),
]