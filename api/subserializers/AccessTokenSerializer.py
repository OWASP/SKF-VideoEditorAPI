from rest_framework import serializers
from rest_framework.authentication import authenticate
from api.subviews.utils.constants import APIConstants as constants


class AccessTokenSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, args):
        email = args.get('email')
        password = args.get('password')

        developer = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )

        if not developer:
            msg = constants.AccessTokenMessages.CREDENTIAL_NOT_FOUND
            raise serializers.ValidationError(msg, code='authorization')

        args['user'] = developer
        args['is_staff'] = developer.is_staff
        return args
