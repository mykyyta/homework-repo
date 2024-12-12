from django.urls import path

from . import views

urlpatterns = [
    path('', views.trainers, name='trainers'),
    path('<trainer_id>/', views.specific_trainer, name='specific_trainer'),
    path('<trainer_id>/<service_id>/', views.specific_service, name='specific_service'),
    path('<trainer_id>/<service_id>/booking/', views.service_booking, name='service_booking'),
]