from django.db import transaction
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from polls.models import *


class GetUserPollSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for List of answered polls for 1 user."""

    poll = serializers.SerializerMethodField()

    def get_poll(self, user_poll):
        return str(user_poll.poll.name)

    class Meta:
        model = UserPoll
        fields = ['url', 'poll']


# ===============================================
#   Serializers for getting list of active polls:
# ===============================================

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


# ========================================================================
#   Serializers for getting detail user's poll with questions and answers:
# ========================================================================

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
        fields = ['answer_text', 'choice']


# ====================================================
#   Serializers for creating user's poll with answers:
# ====================================================

class CreateUserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = ['answer_text', 'choice']


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
                raise ValidationError('Specific choice can be only one for one poll.')
            choices_dict[choice_id] = choice_data
        choices = Choice.objects.filter(id__in=choices_dict.keys()).only(
            'id', 'question__type', 'question__id').all()
        questions_set = set()
        for choice in choices:
            # Checking types of questions and answers:
            if choices_dict[choice.id].get("choice_text") is not None and choice.question.type != Question.TEXT_ANSWER:
                raise ValidationError('Text given for not text type question.')
            if choices_dict[choice.id].get("choice_text") is None and choice.question.type == Question.TEXT_ANSWER:
                raise ValidationError('No text given for text type question.')
            if choice.question.id in questions_set and choice.question.type != Question.MULTIPLE_CHOICES:
                raise ValidationError('Too many choices for Not MULTIPLE CHOICES type question.')
            questions_set.add(choice.question.id)
        with transaction.atomic():
            # Creating UserPoll and UserAnswers:
            user_poll = UserPoll.objects.create(**validated_data)
            UserAnswer.objects.bulk_create(
                [UserAnswer(user_poll=user_poll, **answer) for answer in choices_dict.values()])
        return user_poll


# ================================================
#   Serializers for admins CRUD methods for Polls:
# ================================================

class AdminChoiceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Choice
        exclude = ['question']

    def update(self, instance, validated_data):
        if validated_data.get('choice_text') and instance.question.type == Question.TEXT_ANSWER:
            raise ValidationError("You can not add choice for text_type question.")
        super().update(instance, validated_data)
        return instance


class AdminQuestionSerializer(serializers.HyperlinkedModelSerializer):
    choices = AdminChoiceSerializer(many=True)

    class Meta:
        model = Question
        exclude = ['poll']

    def update(self, instance, validated_data):
        """Updating simple question's fields and creating new choices."""

        choices = None
        if 'choices' in validated_data:
            choices = validated_data.pop('choices')
        if instance.poll.start_date:
            raise ValidationError('You can not change questions, start_date is set.')
        question_type = validated_data.get("type", instance.type)
        if question_type != Question.TEXT_ANSWER:
            for choice in choices:
                if not choice["choice_text"]:
                    raise ValidationError('No text provided for choice.')
        old_instance_type = instance.type

        with transaction.atomic():
            super().update(instance, validated_data)
            # Deleting choices for text type question:
            if validated_data.get("type") == Question.TEXT_ANSWER and old_instance_type != Question.TEXT_ANSWER:
                if instance.choices:
                    instance.choices.all().delete()
                Choice.objects.create(question=instance)
            if choices and question_type != Question.TEXT_ANSWER:
                # Delete Text choice if type was TEXT_ANSWER:
                if old_instance_type == Question.TEXT_ANSWER:
                    instance.choices.all().delete()
                # Adding choices for question by choices:
                Choice.objects.bulk_create([Choice(question=instance, **choice) for choice in choices])
        return instance


class AdminPollSerializer(serializers.HyperlinkedModelSerializer):
    questions = AdminQuestionSerializer(many=True, required=False)

    class Meta:
        model = Poll
        fields = '__all__'

    @staticmethod
    def check_start_date_not_greater_than_end_date(validated_data: dict, instance: Poll = None):
        """Check start_date <= end_date"""

        if instance:
            start_date = validated_data.get("start_date", instance.start_date)
            end_date = validated_data.get("end_date", instance.end_date)
        else:
            start_date = validated_data.get("start_date")
            end_date = validated_data.get("end_date")
        if start_date and end_date and start_date > end_date:
            raise ValidationError('Wrong: start_date > end_date')

    @staticmethod
    def create_questions(questions, poll):
        """Creating questions with choices"""

        for question in questions:
            choices = question.pop('choices')
            if question.get('type') == Question.TEXT_ANSWER:
                choices = [{'choice_text': None}]
            if not choices:
                raise ValidationError('choices field must be not empty.')
            if question.get('type') != Question.TEXT_ANSWER:
                for choice in choices:
                    if not choice["choice_text"]:
                        raise ValidationError('No text provided for choice.')
            new_question = Question.objects.create(poll=poll, **question)
            Choice.objects.bulk_create([Choice(question=new_question, **choice) for choice in choices])

    @transaction.atomic
    def create(self, validated_data):
        """Creating Choices, Questions and Poll."""

        questions = validated_data.pop('questions')
        # Check start_date <= end_date:
        self.check_start_date_not_greater_than_end_date(validated_data)
        poll = Poll.objects.create(**validated_data)
        self.create_questions(questions, poll)
        return poll

    def update(self, instance, validated_data):
        """Updating simple poll's fields and creating new questions."""

        questions = None
        if 'questions' in validated_data:
            questions = validated_data.pop('questions')
        if questions and getattr(instance, "start_date"):
            raise ValidationError('You can not change questions, start_date is set.')
        # Check start_date <= end_date:
        self.check_start_date_not_greater_than_end_date(validated_data, instance)
        with transaction.atomic():
            super().update(instance, validated_data)
            if questions:
                self.create_questions(questions, instance)
        return instance
