import os
import requests
from rest_framework import serializers
from .models import Staff

CUSTOMER_SERVICE_URL = "http://customer-service:8000"

class StaffSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=6)
    
    class Meta:
        model = Staff
        fields = ["id", "username", "name", "email", "department", "position", "is_active", "password"]
        read_only_fields = ["id"]
    
    def validate_username(self, value):
        """Ensure username is provided when creating new staff"""
        if not value or not value.strip():
            raise serializers.ValidationError("Username is required")
        return value.strip()
    
    def create(self, validated_data):
        # Extract password
        password = validated_data.pop('password')
        
        # Create Staff record
        staff = Staff.objects.create(**validated_data)
        
        # Create User account in customer-service with role="staff"
        try:
            response = requests.post(
                f"{CUSTOMER_SERVICE_URL}/auth/register/",
                json={
                    "username": staff.username,
                    "email": staff.email,
                    "password": password,
                    "name": staff.name,
                    "role": "staff"
                },
                timeout=5
            )
            if response.status_code != 201:
                # If user creation fails, delete staff and raise error
                staff.delete()
                raise serializers.ValidationError({
                    "error": f"Failed to create user account: {response.text}"
                })
        except requests.RequestException as e:
            # If service unavailable, delete staff and raise error
            staff.delete()
            raise serializers.ValidationError({
                "error": f"Customer service unavailable: {str(e)}"
            })
        
        return staff
