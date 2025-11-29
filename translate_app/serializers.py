# File: translate_app/serializers.py
from rest_framework import serializers
from .models import User
import re

class UserRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate_username(self, value: str) -> str:
        """Kiểm tra Username"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Tên đăng nhập này đã được sử dụng.")
        
        if not re.match(r'^\w+$', value):
            raise serializers.ValidationError("Tên đăng nhập không được chứa khoảng trắng hoặc ký tự đặc biệt.")
        return value

    def validate_email(self, value: str) -> str:
        """
        [MỚI] Kiểm tra Email duy nhất
        """
        # Chuẩn hóa email về chữ thường để so sánh chính xác (Test@mail.com == test@mail.com)
        normalized_email = value.lower()
        
        if User.objects.filter(email=normalized_email).exists():
            raise serializers.ValidationError("Email này đã được đăng ký bởi tài khoản khác.")
        
        return normalized_email

    def validate_password(self, value: str) -> str:
        """
        [NÂNG CẤP] Kiểm tra độ mạnh mật khẩu
        """
        errors = []

        if len(value) < 8:
            errors.append("Mật khẩu phải dài ít nhất 8 ký tự.")
        
        if not any(char.isdigit() for char in value):
            errors.append("Phải chứa ít nhất 1 chữ số.")
            
        if not any(char.isupper() for char in value):
            errors.append("Phải chứa ít nhất 1 chữ in hoa.")
            
        if not any(char.islower() for char in value):
            errors.append("Phải chứa ít nhất 1 chữ thường.")

        # Nếu muốn chặt chẽ hơn: Ký tự đặc biệt
        # if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
        #    errors.append("Phải chứa ký tự đặc biệt (!@#...).")

        if errors:
            # Nối các lỗi lại thành 1 câu
            raise serializers.ValidationError(" ".join(errors))
            
        return value
    
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    
class LanguageSerializer(serializers.Serializer):
    lang_code = serializers.CharField()
    lang_name = serializers.CharField()
    
class TranslationRequestSerializer(serializers.Serializer):
    text = serializers.CharField(required=True, allow_blank=False)
    source_lang = serializers.CharField(required=True, max_length=10)
    target_lang = serializers.CharField(required=True, max_length=10)
    
