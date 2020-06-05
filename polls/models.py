from django.db import models


class Poll(models.Model):
    """Poll that admin created."""
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.CharField(max_length=500)

    def __str__(self):
        return self.name


class Question(models.Model):
    # 3 types of questions:
    TEXT_ANSWER = 'TX'
    ONE_CHOICE = '1C'
    MULTIPLE_CHOIUCES = 'MC'
    TYPE_CHOICES = (
        (TEXT_ANSWER, 'Text answer'),
        (ONE_CHOICE, 'One choice'),
        (MULTIPLE_CHOIUCES, 'Multiple choices'),
    )
    type = models.CharField(
        max_length=2,
        choices=TYPE_CHOICES,
        default=TEXT_ANSWER
    )
    text = models.CharField(max_length=250)
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
    text = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.text


class UserPoll(models.Model):
    """Poll that user answered."""
    person_id = models.IntegerField()
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)


class UserAnswer(models.Model):
    """ User's answer for question in poll.

        If it answer by choice - text will be null .
        And text is not null - if it text answer.
    """
    user_poll = models.ForeignKey(UserPoll, on_delete=models.CASCADE, related_name='choices')
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    text = models.CharField(max_length=300, null=True, blank=True)
