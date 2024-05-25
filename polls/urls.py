from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "polls"
urlpatterns = [
    # ex: /polls/
    path("", views.IndexView.as_view(), name="index"), 

    # ex: /polls/5/
    path("<int:pk>/", views.DetailView.as_view(), name="detail"), 

    # ex: /polls/5/results/
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"), 

    #ex: /polls/5/vote/
    path("<int:question_id>/vote/", views.vote, name="vote"), 

    path('auth/', views.auth_view, name='auth'), 

    path('logout/', auth_views.LogoutView.as_view(next_page='polls:index'), name='logout'), 

    path("<int:question_id>/add_comment/", views.add_comment, name="add_comment"), 
]