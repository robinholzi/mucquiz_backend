
from rest_framework.views import exception_handler
from rest_framework.response import Response


def error_response(status, code, title, message=None, data=None):
    context = {'code': code, 'title': title, 'message': message, 'data': data, }
    return Response(context, status=status)


def success(status, code, title, message=None, data=None):
    context = {'code': code, 'title': title, 'message': message, 'data': data, }
    return Response(context, status=status)


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        # response.data['status_code'] = response.status_code
        print("-> ", response.context_data)
        return error_response(response.status_code, "123?", "ERR",
                              data=response.data)

    return error_response(500, 0, "unknown error",
      message="Un unexpected or unhandled error occured during your request!")