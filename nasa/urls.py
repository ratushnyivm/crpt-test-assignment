from django.urls import path

from nasa import views

urlpatterns = [
    path('neo_id/', views.TaskIdView.as_view()),
    path('neo_result/', views.TaskResultView.as_view()),
]
