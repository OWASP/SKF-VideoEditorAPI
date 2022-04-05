from rest_framework import viewsets, filters
from api import models, permissions, serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from api.subviews.utils.constants import APIConstants as constants

class DeveloperViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.DeveloperSerializer
    queryset = models.DeveloperModel.objects.all()
    permission_classes = (permissions.UpdateDeveloper,)
    authentication_classes = (TokenAuthentication,)
    filter_backends = (filters.SearchFilter,)
    search_backends = ('name', 'email', 'organisation')
    
    def create(self, request):
        serializer = self.serializer_class(data = request.data, context={'request': request})
        if serializer.is_valid():
            email = serializer.validated_data['email']
            name = serializer.validated_data['name']
            organisation = serializer.validated_data['organisation']
            serializer.save()
            return Response({
                'message': constants.DeveloperAPIMessages.DEVELOPER_API_RESPONSE_MESSAGE.value,
                'email': email,
                'name': name,
                'organisation': organisation
            })
        else:
            return Response(
                serializer.errors,
                status = status.HTTP_400_BAD_REQUEST,
            )
