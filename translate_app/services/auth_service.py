import uuid
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from typing import Dict, Any

# Import Models
from translate_app.models import User, UserSetting, UserSession

class AuthService:
    """
    Service xử lý logic đăng ký và đăng nhập.
    """

    @staticmethod
    def register_user(user_data: Dict[str, Any]) -> User:
        with transaction.atomic():
            raw_password = user_data.pop('password')
            hashed_password = make_password(raw_password)

            user = User(
                username=user_data['username'],
                email=user_data.get('email'),
                password=hashed_password,
                role=User.Role.CUSTOMER
            )
            user.save()

            UserSetting.objects.create(
                user=user,
                theme_color='light',
                website_language='vi',
                audio_speed=1.0
            )
            return user

    @staticmethod
    def login_user(login_data: dict) -> dict:
        username = login_data.get('username')
        raw_password = login_data.get('password')

        # 1. Tìm User
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise ValidationError("Tài khoản không tồn tại.")

        # 2. Kiểm tra Pass
        if not check_password(raw_password, user.password):
            raise ValidationError("Mật khẩu không chính xác.")

        # 3. Tạo Session
        token = str(uuid.uuid4())
        expires_at = timezone.now() + timedelta(days=1)

        UserSession.objects.create(
            session_token=token,
            user=user,
            expires_at=expires_at
        )

        return {
            "token": token,
            "user_id": user.user_id,
            "username": user.username,
            "role": user.role
        }
    @staticmethod
    def logout_user(token: str):
        """
        Xóa phiên đăng nhập khỏi Database
        """
        if not token:
            return
        
        # Dùng filter().delete() an toàn hơn get().delete()
        # Vì nếu token không tồn tại, nó không báo lỗi, chỉ đơn giản là không xóa gì.
        UserSession.objects.filter(session_token=token).delete()