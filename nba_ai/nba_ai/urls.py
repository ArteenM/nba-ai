from django.contrib import admin
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from predictor import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/predict_winner/', csrf_exempt(views.predict_winner), name='predict_winner'),
    path('api/matchup/', csrf_exempt(views.get_team_matchup), name='get_matchup'),
    #path('', include('predictor.urls')),
]