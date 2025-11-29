# File: translate_app/services/tts_service.py
import os
import uuid
from gtts import gTTS
from django.conf import settings

class TTSService:
    @staticmethod
    def generate_audio(text: str, lang_code: str) -> str:
        """
        Sinh file âm thanh từ văn bản.
        Trả về: Đường dẫn URL tương đối của file (ví dụ: /media/audio/xyz.mp3)
        """
        try:
            # 1. Tạo thư mục lưu trữ nếu chưa có
            save_dir = os.path.join(settings.MEDIA_ROOT, 'audio')
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            # 2. Tạo tên file ngẫu nhiên (tránh trùng lặp khi nhiều người cùng nghe)
            filename = f"{uuid.uuid4()}.mp3"
            file_path = os.path.join(save_dir, filename)

            # 3. Gọi thư viện gTTS
            # lang_code phải chuẩn (vi, en, ja, ko...)
            tts = gTTS(text=text, lang=lang_code)
            tts.save(file_path)

            # 4. Trả về đường dẫn URL để Frontend gọi
            return f"{settings.MEDIA_URL}audio/{filename}"

        except Exception as e:
            raise Exception(f"Lỗi tạo âm thanh: {str(e)}")