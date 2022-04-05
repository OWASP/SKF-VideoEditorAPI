from rest_framework import serializers
from api import models
from api.submodels import DeveloperModel

class DeveloperSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DeveloperModel
        fields = ('id', 'email', 'name', 'organisation', 'password')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {
                    'input_type': 'password',
                }
            }
        }
    
    def create(self, validated_data):
        developer_identity = DeveloperModel.objects.create_user(
            email = validated_data['email'],
            name = validated_data['name'],
            organisation = validated_data['organisation'],
            password = validated_data['password']
        )
        return developer_identity
