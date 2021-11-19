from django.contrib import admin

from data.models import Topic, Question, Answer

admin.site.register(Topic)
admin.site.register(Question)
admin.site.register(Answer)
