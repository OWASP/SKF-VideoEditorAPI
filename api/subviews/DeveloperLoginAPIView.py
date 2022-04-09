from api import serializers
from rest_framework.settings import api_settings
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token


class DeveloperLoginApiView(ObtainAuthToken):
    serializer_class = serializers.AccessTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            developer = serializer.validated_data['user']
            token, check = Token.objects.get_or_create(user=developer)
            return Response({
                'token': token.key,
                'is_staff': developer.is_staff,
                'first_time_generated': check
            })
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
