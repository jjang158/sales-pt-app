from rest_framework.response import Response
from rest_framework import status

def response_suc(data={}):
    response_data = {"status": 200,
                    "message": "Success",
                    "data": data}
    return Response(response_data, status=status.HTTP_200_OK)
    
def response_err(status_code, message, data={}):
    response_data = {"status": status_code,
                    "message": message,
                    "data": data}
    return Response(response_data, status=status.HTTP_200_OK)