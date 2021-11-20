from django.db import models


class Topic(models.Model):
    title = models.CharField('title', max_length=250)
    description = models.TextField('description', blank=True, null=True)
    img_url = models.CharField('img_url', max_length=4096, blank=True, null=True)

    updated = models.DateTimeField('updated', auto_now=True)
    created = models.DateTimeField('created', auto_now_add=True)

    def __str__(self):
        return f'Topic ({self.title})'


class Question(models.Model):
    topic = models.ForeignKey(Topic, null=False, on_delete=models.CASCADE)

    text = models.CharField('name', max_length=1000)
    description = models.TextField('description', blank=True, null=True)
    img_url = models.CharField('img_url', max_length=4096, blank=True, null=True)

    answer_detail = models.CharField('answer_detail', max_length=4096, blank=True, null=True)
    answer_img_url = models.CharField('answer_img_url', max_length=4096, blank=True, null=True)

    updated = models.DateTimeField('updated', auto_now=True)
    created = models.DateTimeField('created', auto_now_add=True)

    def __str__(self):
        return f'Question ({self.text})'


class Answer(models.Model):
    question = models.ForeignKey(Question, null=False, on_delete=models.CASCADE)

    text = models.CharField('text', max_length=1000)
    correct = models.BooleanField('correct', blank=False, null=False, default=False)

    updated = models.DateTimeField('updated', auto_now=True)
    created = models.DateTimeField('created', auto_now_add=True)

    def __str__(self):
        return f'Answer ({self.text})'
