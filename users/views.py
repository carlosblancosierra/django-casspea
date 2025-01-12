from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from users.models import CustomUser
from users.serializers import UserSerializer


class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie('access')
        response.delete_cookie('refresh')
        return response


@api_view(['GET'])
def get_user_profile(request):
    try:
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)
    except CustomUser.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
