from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from predictor import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/predict_winner/', csrf_exempt(views.predict_winner), name='predict_winner'),
    path('api/injuries/', views.get_injuries, name='get_injuries'),
]