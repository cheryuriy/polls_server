from django.utils import timezone
from rest_framework import generics, viewsets, mixins
from rest_framework.permissions import IsAdminUser, AllowAny

from polls.serializers import *


class UserPollListView(generics.ListAPIView):
    """List of user's polls."""

    lookup_field = 'person_id'
    queryset = UserPoll.objects.order_by('-id').all()
    serializer_class = GetUserPollSerializer

    def get_queryset(self):
        person_id = self.kwargs[self.lookup_field]
        self.queryset = self.queryset.filter(person_id=person_id).only('poll__name')  # Optimized query
        return self.queryset


class UserPollDetailView(generics.ListAPIView):
    """User's poll with answers and questions."""

    queryset = UserAnswer.objects.all()
    serializer_class = FullUserAnswerSerializer

    def get_queryset(self):
        user_poll_id = self.kwargs[self.lookup_field]
        self.queryset = self.queryset.filter(user_poll_id=user_poll_id).select_related('choice').prefetch_related(
            'choice__question')  # Optimized query
        return self.queryset


class UserPollCreateView(generics.CreateAPIView):
    """Post User Poll's answers"""

    queryset = UserPoll.objects.all()
    serializer_class = CreateUserPollSerializer


class ActivePollsListView(generics.ListAPIView):
    """List of active( by date) polls."""

    queryset = Poll.objects.filter(start_date__lte=timezone.now().date(), end_date__gte=timezone.now().date()).all()
    serializer_class = PollSerializer
    permission_classes = (AllowAny,)


class PollViewSet(viewsets.ModelViewSet):
    """POST will create new Poll... All questions that you PUT will be created and added."""

    queryset = Poll.objects.all().order_by('-start_date')
    serializer_class = AdminPollSerializer
    permission_classes = (IsAdminUser,)


class QuestionViewSet(mixins.UpdateModelMixin,
                      mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):
    """All choices that you PUT will be created and added."""

    queryset = Question.objects.all()
    serializer_class = AdminQuestionSerializer
    permission_classes = (IsAdminUser,)


class ChoiceViewSet(mixins.UpdateModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    """Get or edit Choice."""

    queryset = Choice.objects.all()
    serializer_class = AdminChoiceSerializer
    permission_classes = (IsAdminUser,)
