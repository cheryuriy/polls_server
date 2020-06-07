from django.db import models


class Poll(models.Model):
    """Poll that admin are creating."""

    name = models.CharField(max_length=50)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.CharField(max_length=500)

    class Meta:
        indexes = [
            models.Index(fields=['-start_date', '-end_date']),
            ]

    def __str__(self):
        return self.name


class Question(models.Model):
    # 3 types of questions:
    TEXT_ANSWER = 'TX'
    ONE_CHOICE = '1C'
    MULTIPLE_CHOICES = 'MC'
    TYPE_CHOICES = (
        (TEXT_ANSWER, 'Text answer'),
        (ONE_CHOICE, 'One choice'),
        (MULTIPLE_CHOICES, 'Multiple choices'),
    )
    type = models.CharField(
        max_length=2,
        choices=TYPE_CHOICES,
        default=TEXT_ANSWER
    )
    question_text = models.CharField(max_length=250)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='questions')

    def __str__(self):
        return self.text


class Choice(models.Model):
    """
        Choice for question.

        text is not null - if it answer by choice.
        And text is null - if it text answer - text will be in UserAnswer
    """

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.text


class UserPoll(models.Model):
    """Poll that user answered."""
    person_id = models.IntegerField(db_index=True)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)


class UserAnswer(models.Model):
    """ User's answer for question in poll.

        If it answer by choice - text will be null .
        And text is not null - if it text answer.
    """
    user_poll = models.ForeignKey(UserPoll, on_delete=models.CASCADE, related_name='choices')
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=300, null=True, blank=True)
