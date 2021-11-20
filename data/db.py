from django.db import connection


def query_random_questions_of_topic(topic_id: str, size: int):
    if size < 1:
        size = 1

    query_str = """
        SELECT id, title, description, img_url
        
        FROM data_question 

        WHERE topic_id=%s
        ORDER BY RANDOM()
        LIMIT %s
    """

    with connection.cursor() as cursor:
        cursor.execute(query_str, [topic_id, size])
        rawAll = cursor.fetchall()
        elements = []
        for raw in rawAll:
            elements.append({
                'id': raw[0],
                'title': raw[1],
                'description': raw[2],
                'img_url': raw[3],
            })
        return elements