
from django.urls import path

from data.views import topic_detail, topic_list, quiz_generate, quiz_evaluate

urlpatterns = [
    path('topic/list/', topic_list, name='topic_list'),
    path('topic/<int:topic_id>/', topic_detail, name='topic_detail'),

    path('quiz/generate/', quiz_generate, name='generate_quiz'),
    path('quiz/evaluate/', quiz_evaluate, name='quiz_evaluate'),
]

