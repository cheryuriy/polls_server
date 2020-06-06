from django.utils import timezone
from rest_framework import generics

from polls.serializers import *


class UserPollListView(generics.ListAPIView):
    """List of user's polls."""

    lookup_field = 'person_id'
    queryset = UserPoll.objects.order_by('-id').all()
    serializer_class = GetUserPollSerializer

    def get_queryset(self):
        person_id = self.kwargs[self.lookup_field]
        # Optimized query:
        self.queryset = self.queryset.filter(person_id=person_id).only('poll__name')
        return self.queryset


class UserPollDetailView(generics.ListAPIView):
    """User's poll with answers and questions."""

    queryset = UserAnswer.objects.all()
    serializer_class = FullUserAnswerSerializer

    def get_queryset(self):
        user_poll_id = self.kwargs[self.lookup_field]
        # Optimized query:
        self.queryset = self.queryset.filter(user_poll_id=user_poll_id).select_related('choice').prefetch_related(
            'choice__question')
        return self.queryset


class UserPollCreateView(generics.CreateAPIView):
    """Post User Poll's answers"""

    queryset = UserPoll.objects.all()
    serializer_class = CreateUserPollSerializer


class ActivePollsListView(generics.ListAPIView):
    """List of active( by date) polls."""

    queryset = Poll.objects.filter(end_date__gte=timezone.now().date()).all()
    serializer_class = PollSerializer
