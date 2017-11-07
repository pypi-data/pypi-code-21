'''
Created on Nov 14, 2015

@author: panweif
'''
from rest_framework.response import Response
from rest_framework import status

def request_data_serializer_parse(serializerClass, many=False):
    def wrapper_func(func):
        def newFunc(request, *args, **kwargs):
            serializer = serializerClass(data=request.data, many=many)
            if serializer.is_valid():
                return func(request, serializer.validated_data, *args, **kwargs)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        setattr(newFunc, '__doc__', getattr(func, '__doc__'))
        return newFunc
    return wrapper_func
