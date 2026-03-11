from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import Customer, UserProfile


class CustomerSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="name", required=False)
    username = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = ["id", "name", "full_name", "email", "phone", "address", "username"]
        extra_kwargs = {"name": {"required": False}}

    def get_username(self, obj):
        profile = getattr(obj, "userprofile", None)
        if profile and profile.user:
            return profile.user.username
        return None

    def update(self, instance, validated_data):
        # Allow updating via full_name (mapped to name)
        if "name" in validated_data:
            instance.name = validated_data["name"]
        if "email" in validated_data:
            instance.email = validated_data["email"]
        if "phone" in validated_data:
            instance.phone = validated_data["phone"]
        if "address" in validated_data:
            instance.address = validated_data["address"]
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=6)
    email = serializers.EmailField()
    name = serializers.CharField(max_length=255)
    role = serializers.ChoiceField(choices=UserProfile.ROLE_CHOICES, default=UserProfile.ROLE_CUSTOMER)

    def create(self, validated_data):
        username = validated_data["username"]
        email = validated_data["email"]
        password = validated_data["password"]
        name = validated_data["name"]
        role = validated_data["role"]

        user = User.objects.create_user(username=username, email=email, password=password)

        customer = None
        if role == UserProfile.ROLE_CUSTOMER:
            customer = Customer.objects.create(name=name, email=email)

        profile = UserProfile.objects.create(user=user, role=role, customer=customer)
        return user, profile


class RoleTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        role = UserProfile.ROLE_CUSTOMER
        customer_id = None

        profile = getattr(user, "profile", None)
        if profile is not None:
            role = profile.role
            if profile.customer_id is not None:
                customer_id = profile.customer_id

        token["role"] = role
        token["user_id"] = user.id
        token["username"] = user.username
        token["customer_id"] = customer_id
        return token
