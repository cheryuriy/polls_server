from django.db import transaction
from rest_framework import serializers

from polls.models import *


class GetUserPollSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for List of answered polls for 1 user."""

    poll = serializers.SerializerMethodField()

    def get_poll(self, user_poll):
        return str(user_poll.poll.name)

    class Meta:
        model = UserPoll
        fields = ['url', 'poll']


# ==========================================
#   Serializers to get list of active polls:
# ==========================================

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        exclude = ['question']


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        exclude = ['poll']


class PollSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Poll
        fields = '__all__'


# ===================================================================
#   Serializers to get detail user's poll with questions and answers:
# ===================================================================

class PartQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        exclude = ['poll', 'id']


class FullChoiceSerializer(serializers.ModelSerializer):
    question = PartQuestionSerializer()

    class Meta:
        model = Choice
        exclude = ['id']


class FullUserAnswerSerializer(serializers.ModelSerializer):
    choice = FullChoiceSerializer()

    class Meta:
        model = UserAnswer
        fields = ['text', 'choice']


# =================================================
#   Serializers to create user's poll with answers:
# =================================================

class CreateUserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = ['text', 'choice']


class CreateUserPollSerializer(serializers.ModelSerializer):
    choices = CreateUserAnswerSerializer(many=True)

    class Meta:
        model = UserPoll
        fields = '__all__'

    def create(self, validated_data):
        """Creating UserPoll and UserAnswers after checking types of questions."""

        choices = validated_data.pop('choices')
        choices_dict = {}
        for choice_data in choices:
            choice_id = choice_data["choice"].id
            if choice_id in choices_dict:
                raise serializers.ValidationError('Specific choice can be only one for one poll.')
            choices_dict[choice_id] = {**choice_data}
        choices = Choice.objects.filter(id__in=choices_dict.keys()).only(
            'id', 'question__type', 'question__id').all()
        questions_set = set()
        for choice in choices:
            # Checking types of questions and answers:
            if choices_dict[choice.id].get("text") is not None and choice.question.type != Question.TEXT_ANSWER:
                raise serializers.ValidationError('Text given for not text type question.')
            if choices_dict[choice.id].get("text") is None and choice.question.type == Question.TEXT_ANSWER:
                raise serializers.ValidationError('No text given for text type question.')
            if choice.question.id in questions_set and choice.question.type != Question.MULTIPLE_CHOICES:
                raise serializers.ValidationError('Too many choices for Not MULTIPLE CHOICES type question.')
            questions_set.add(choice.question.id)
        with transaction.atomic():
            # Creating UserPoll and UserAnswers:
            user_poll = UserPoll.objects.create(**validated_data)
            for answer in choices_dict.values():
                answer['user_poll'] = user_poll
            UserAnswer.objects.bulk_create([UserAnswer(**answer) for answer in choices_dict.values()])
        return user_poll
