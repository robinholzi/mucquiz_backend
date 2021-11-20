from random import random, randint

from django.core.paginator import Paginator
from rest_framework.decorators import api_view
from rest_framework.utils import json

from data.models import Topic, Question, Answer
from data.utils import error_response, success


@api_view(['GET'])
def topic_list(request, *args, **kwargs):
    try:
        page_size = int(request.GET.get('page_size', 10))
        page_no = int(request.GET.get('page_no', 1))
    except ValueError:
        return error_response(400, 0, "error passing params.")

    try:
        query = Topic.objects.all().order_by('id')
        paginator = Paginator(query, page_size)

        res_data = []
        for item in paginator.page(page_no):
            res_data.append({
                'id': item.id,
                'title': item.title,
                'description': item.description,
                'img_url': item.img_url,
            })

        return success(200, 0, "topic list retrieved successfully.", data=res_data)
    except Exception as ex:
        print(ex)
        return error_response(500, 0, "internal error.", )


@api_view(['GET'])
def topic_detail(request, topic_id, *args, **kwargs):
    query = Topic.objects.filter(id=topic_id)

    if not query.exists():
        return error_response(400, 0, "not existing")

    try:
        item = query.first()
        return success(200, 0, "topic detail retrieved successfully.", data={
                'id': item.id,
                'title': item.title,
                'description': item.description,
                'img_url': item.img_url,
            })

    except:
        return error_response(500, 0, "internal error.", )


@api_view(['GET'])
def quiz_generate(request, *args, **kwargs):
    try:
        topic_id = int(request.GET.get('topic_id', -1))
        if topic_id <= 0:
            # select random topic
            topic_query = Topic.objects.all()
            randIdx = randint(0, len(topic_query)-1)
            topic_id = list(topic_query.values_list('id', flat=True))[randIdx]

        size = int(request.GET.get('size', 4))
        if size < 1:
            size = 4

    except ValueError as err:
        print("err: ", err)
        return error_response(400, 0, "error passing params.")

    try:
        # check if topic exists
        topic_query = Topic.objects.filter(id=topic_id)
        if not topic_query.exists():
            return error_response(400, 1, "topic not existing")

        topic = topic_query.first()

        # construct random quiz
        query = Question.objects.filter(topic_id=topic_id).order_by("?")  # random ordering
        if not query.exists():
            return error_response(400, 2, "not enough questions found.")

        questions = []
        for item in query:
            # we avoid to use raw sql join queries ;)
            answers_query = Answer.objects.filter(question_id=item.id)
            if not answers_query.exists():
                continue  # skip this question (min. 1 answers required)

            answers = []
            for ans in answers_query:
                answers.append({
                    'id': ans.id,
                    'text': ans.text,
                })

            questions.append({
                'id': item.id,
                'title': item.text,
                'description': item.description,
                'img_url': item.img_url,
                'answers': answers,
            })

            # check if desired size already reached
            if len(query) >= size:
                break

        if len(questions) < 1:
            return error_response(400, 2, "not enough questions found.")

        return success(200, 0, "quiz retrieved successfully.", data={
            'topic': {
                'id': topic.id,
                'title': topic.title,
                'description': topic.description,
                'img_url': topic.img_url,
            },
            'questions': questions,
        })

    except:
        return error_response(500, 0, "internal error.", )


# helper question:{id, ans_ids, ans_detail}
def _eval_question(question):
    # we avoid to use raw sql join queries ;)
    correct_answers_query = Answer.objects.filter(question_id=question['id'], correct=True)

    todo_answers = list(question['ans_ids'])
    incorrect_answers = []
    for correctAns in correct_answers_query:
        if correctAns.id in todo_answers:
            # as it should be correct answer chosen:
            todo_answers.remove(correctAns.id)
        else:  # correct answer not marked as correct
            incorrect_answers.append({
                'id': correctAns.id,
                'text': correctAns.text,
                'correct': correctAns.correct,
            })


    # rest: marked as correct, but actually false
    for falsePositive in todo_answers:
        ans_query = Answer.objects.filter(id=falsePositive, question_id=question['id'])
        if not ans_query.exists():
            incorrect_answers.append({
                'id': falsePositive,
                'text': "answer not available for this question",
                'correct': False,
            })
            continue
        incorrect_answers.append({
            'id': ans_query.first().id,
            'text': ans_query.first().text,
            'correct': ans_query.first().correct,
        })

    # todo_answers.clear()  # not used anymore

    return {
            'question_id': question['id'],
            'answer_correct': len(incorrect_answers) < 1,
            'incorrect_answers': incorrect_answers,
            'answer_detail': question['ans_detail'],
        }


@api_view(['POST'])
def quiz_evaluate(request, *args, **kwargs):
    try:
        req_data = json.loads(request.body)
        question_id = int(req_data['question_id'])
        ans_ids = []
        for ans_id in list(req_data['chosen_answer_ids']):
            ans_ids.append(int(ans_id))

    except ValueError as err:
        return error_response(400, 0, "error parsing request data.")

    try:
        # check if topic exists
        question_query = Question.objects.filter(id=question_id)
        if not question_query.exists():
            return error_response(400, 1, "question not existing")

        return success(200, 0, "answer evaluated successfully.", data=_eval_question({
            'id': question_id,
            'ans_ids': ans_ids,
            'ans_detail': question_query.first().answer_detail,
        }))

    except Exception as ex:
        return error_response(500, 0, "internal error.", )


@api_view(['POST'])
def quiz_evaluate_total(request, *args, **kwargs):
    questions = []

    try:
        req_data = json.loads(request.body)
        req_questions = list(req_data)

        for quest in req_questions:
            question_id = int(quest['question_id'])
            chosen_answer_ids = []
            for ans_id in list(quest['chosen_answer_ids']):
                chosen_answer_ids.append(int(ans_id))

            questions.append({
                'id': question_id,
                'ans_ids': chosen_answer_ids,
            })

    except ValueError as err:
        return error_response(400, 0, "error parsing request data.")

    try:
        questions_results = []

        # check if topic exists
        for quest in questions:
            question_query = Question.objects.filter(id=question_id)
            if not question_query.exists():
                questions_results.append({
                    "question_id": quest['id'],
                    "answer_correct": False,
                    "answer_detail": "this question does not exist!",
                })
                continue

            updated_quest: map = quest
            updated_quest.update({'ans_detail': question_query.first().answer_detail})
            questions_results.append(_eval_question(updated_quest))

        return success(200, 0, "answers evaluated successfully.", data=questions_results)

    except Exception as ex:
        return error_response(500, 0, "internal error.", )
