from django.urls import path

from nasa import views

urlpatterns = [
    # API
    path('api/v1/neo_id/', views.TaskIdView.as_view(), name='neo_id'),
    path(
        'api/v1/neo_result/', views.TaskResultView.as_view(), name='neo_result'
    ),

    # forms
    path('id/', views.FormIdView.as_view()),
    path('result/', views.FormResultView.as_view()),
]
