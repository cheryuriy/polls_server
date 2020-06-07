from django.urls import path, include
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.routers import DefaultRouter

from polls import views


router = DefaultRouter()
router.register(r'polls', views.PollViewSet)
router.register(r'questions', views.QuestionViewSet)
router.register(r'choices', views.ChoiceViewSet)
router.get_api_root_view().cls.__name__ = "Admin API"
router.get_api_root_view().cls.__doc__ = "CRUD methods for Polls"


@api_view(['GET'])
def api_root(request, format=None):
    """Start page, representing user's views."""

    urls = {
        'Active Polls': reverse('active_polls', request=request, format=format),
        'User Answered Polls': reverse('user_polls', kwargs={'person_id': 1}, request=request, format=format),
        'User Detailed Poll': reverse('userpoll-detail', kwargs={'pk': 1}, request=request, format=format),
        'Complete a Poll': reverse('userpoll-create', request=request, format=format),
        }
    return Response(urls)


urlpatterns = [
    path('', api_root),
    path('admin_api/', include(router.urls)),
    # user's views:
    path('active_polls/', views.ActivePollsListView.as_view(), name='active_polls'),
    path('user_polls/<int:person_id>/', views.UserPollListView.as_view(), name='user_polls'),
    path('user_poll_detail/<int:pk>/', views.UserPollDetailView.as_view(), name='userpoll-detail'),
    path('user_poll_create/', views.UserPollCreateView.as_view(), name='userpoll-create'),
]
