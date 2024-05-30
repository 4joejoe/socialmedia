# Create serializer for User model

#         """Fetch and return all users paginated to 20 per request"""


from authapp.models import CustomUser
from rest_framework.serializers import ModelSerializer


class UserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        # fields = "__all__"
        fields = [
            f.name
            for f in CustomUser._meta.fields
            if f.name
            not in [
                "is_superuser",
                "is_staff",
                "is_active",
                "groups",
                "user_permissions",
            ]
        ]

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep.pop("password", None)  # remove password from the serialized data
        return rep


from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["user_id"] = user.id
        print("User_ID", token["user_id"])
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Add user_id to the response
        data["user_id"] = self.user.id
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
