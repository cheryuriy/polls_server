from django.urls import path
from polls import views


urlpatterns = [
    path('active_polls/', views.ActivePollsListView.as_view(), name='active_polls'),
    path('user_polls/<int:person_id>/', views.UserPollListView.as_view(), name='user_polls'),
    path('user_poll_detail/<int:pk>/', views.UserPollDetailView.as_view(), name='userpoll-detail'),
    path('user_poll_create/', views.UserPollCreateView.as_view(), name='userpoll-create'),
]
