from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.views.generic import TemplateView
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile 
import os
import uuid
# Import Serializers
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    TranslationRequestSerializer, 
    LanguageSerializer
)

# Import Services
from .services.auth_service import AuthService
from .services.tts_service import TTSService
from .services.language_service import LanguageService
from .services.translation_service import TranslationService
from .services.ocr_service import OCRService
from .services.history_service import HistoryService
# Import Models
from .models import HistoryImage, HistoryPDF, User

# ==========================================
# 1. AUTHENTICATION (Đăng ký/Đăng nhập)
# ==========================================
class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "message": "Dữ liệu không hợp lệ", "errors": serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = AuthService.register_user(serializer.validated_data)
            return Response(
                {"success": True, "message": "Đăng ký thành công", "data": {"user_id": user.user_id, "username": user.username}},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({"success": False, "message": "Lỗi hệ thống", "detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            login_result = AuthService.login_user(serializer.validated_data)
            return Response({"success": True, "message": "Đăng nhập thành công", "data": login_result}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"success": False, "message": str(e.message)}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"success": False, "message": "Lỗi hệ thống", "detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserLogoutView(APIView):
    def post(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({"success": False, "message": "Không tìm thấy Token"}, status=status.HTTP_400_BAD_REQUEST)
        token = auth_header.split(' ')[1]
        try:
            AuthService.logout_user(token)
            return Response({"success": True, "message": "Đăng xuất thành công"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "message": "Lỗi hệ thống"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ==========================================
# 2. TEMPLATE VIEWS (Giao diện HTML)
# ==========================================
class RegisterPageView(TemplateView):
    template_name = "translate_app/register.html" 

class LoginPageView(TemplateView):
    template_name = "translate_app/login.html"

class HomePageView(TemplateView):
    template_name = "translate_app/home.html" 

class FileTranslationView(TemplateView):
    template_name = "translate_app/alt.html" # Lưu ý: Bạn đang đặt tên file là alt.html hay file.html thì sửa ở đây cho khớp

# ==========================================
# 3. CORE FEATURES (Ngôn ngữ, Dịch, TTS)
# ==========================================
class LanguageListView(APIView):
    def get(self, request):
        languages = LanguageService.get_all_languages()
        serializer = LanguageSerializer(languages, many=True)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

class TranslateTextView(APIView):
    def post(self, request):
        serializer = TranslationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        user_id = request.data.get('user_id', 1) 
        try:
            data = serializer.validated_data
            result = TranslationService.process_translation(
                user_id=user_id, text=data['text'], src_lang=data['source_lang'], target_lang=data['target_lang']
            )
            return Response({"success": True, "data": result}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TextToSpeechView(APIView):
    def post(self, request):
        text = request.data.get('text')
        lang = request.data.get('lang', 'en') 
        if not text:
            return Response({"success": False, "message": "Thiếu văn bản"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            audio_url = TTSService.generate_audio(text, lang)
            return Response({"success": True, "audio_url": audio_url}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ==========================================
# 4. FILE TRANSLATION (OCR + Dịch + Download)
# ==========================================
class FileTranslateView(APIView):
    """
    API Xử lý Upload file -> OCR -> Dịch -> Tạo file kết quả (UUID Name)
    """
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        print(">>> START FILE TRANSLATE (UUID) <<<")
        file_obj = request.FILES.get('file')
        source_lang = request.data.get('source_lang', 'en')
        target_lang = request.data.get('target_lang', 'vi')
        
        # [TODO] Lấy ID thật từ Token. Tạm thời hardcode = 1
        user_id = 1 

        if not file_obj:
            return Response({"success": False, "message": "Chưa chọn file."}, status=400)

        try:
            # 1. LƯU FILE GỐC (Uploads)
            fs = FileSystemStorage(location='media/uploads/')
            filename = fs.save(file_obj.name, file_obj)
            original_file_path = f"uploads/{filename}"

            # 2. OCR (Trích xuất text)
            full_path = os.path.join('media/uploads/', filename)
            with open(full_path, 'rb') as f:
                extracted_text = OCRService.extract_text_from_file(f, source_lang)

            if not extracted_text:
                return Response({"success": False, "message": "Không tìm thấy nội dung trong file."}, status=400)

            # 3. DỊCH (save_history=False)
            translation_result = TranslationService.process_translation(
                user_id=user_id,
                text=extracted_text,
                src_lang=source_lang,
                target_lang=target_lang,
                save_history=False 
            )
            translated_text = translation_result['translated_text']

            # ========================================================
            # 4. [CẬP NHẬT] TẠO FILE KẾT QUẢ VỚI UUID
            # ========================================================
            # Tạo chuỗi ngẫu nhiên (Ví dụ: 8f4a2c09...)
            random_name = uuid.uuid4().hex 
            result_filename = f"translated_{random_name}.txt"
            
            fs_result = FileSystemStorage(
                location='media/translations/', 
                base_url='/media/translations/' 
            )
            
            # Lưu file (Không cần check exists vì UUID không bao giờ trùng)
            saved_result_name = fs_result.save(
                result_filename, 
                ContentFile(translated_text.encode('utf-8'))
            )
            
            # Lấy URL download
            download_url = fs_result.url(saved_result_name) 
            print(f"DEBUG: Download URL = {download_url}")

            # ========================================================
            # 5. LƯU DATABASE
            # ========================================================
            user = User.objects.get(pk=user_id)
            
            # Đường dẫn tương đối lưu vào DB
            translated_relative_path = f"translations/{saved_result_name}"

            if filename.lower().endswith('.pdf'):
                HistoryPDF.objects.create(
                    user=user,
                    source_lang_id=source_lang,
                    target_lang_id=target_lang,
                    original_pdf_path=original_file_path,
                    translated_pdf_path=translated_relative_path # <--- Lưu đường dẫn mới
                )
            else:
                HistoryImage.objects.create(
                    user=user,
                    source_lang_id=source_lang,
                    target_lang_id=target_lang,
                    image_file_path=original_file_path,
                    extracted_text=extracted_text,
                    translated_text=translated_text
                    # Nếu sau này bạn thêm cột translated_file_path cho ảnh thì thêm vào đây
                )

            # 6. TRẢ VỀ KẾT QUẢ
            return Response({
                "success": True,
                "data": {
                    "extracted_text": extracted_text,
                    "translated_text": translated_text,
                    "download_url": download_url
                }
            }, status=200)

        except Exception as e:
            print(f"ERROR: {str(e)}")
            return Response({"success": False, "message": str(e)}, status=500)
        
# File: translate_app/views.py

# Import thêm
# File: translate_app/views.py

# Import thêm UserSession để tra cứu token
from .models import UserSession

# File: translate_app/views.py

# Đảm bảo đã import UserSession
from .models import UserSession, HistoryText, HistoryImage, HistoryPDF
from .services.history_service import HistoryService

# ... (Các view khác giữ nguyên)

class HistoryListView(APIView):
    """
    API lấy danh sách lịch sử (Bảo mật theo Token)
    GET /api/v1/history/
    Header: Authorization: Bearer <token>
    """
    def get(self, request):
        # 1. Lấy Token từ Header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response(
                {"success": False, "message": "Bạn chưa đăng nhập (Thiếu Token)."}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

        token = auth_header.split(' ')[1]

        try:
            # 2. Tra cứu Token trong Database để tìm User ID
            # (Logic: Token -> Session -> User)
            session = UserSession.objects.filter(session_token=token).first()
            
            if not session:
                return Response(
                    {"success": False, "message": "Phiên đăng nhập không hợp lệ hoặc đã hết hạn."}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Lấy ID của người dùng sở hữu token này
            current_user_id = session.user.user_id

            # 3. Gọi Service lấy lịch sử của CHÍNH USER ĐÓ
            history_data = HistoryService.get_user_history(current_user_id)
            
            return Response({
                "success": True,
                "data": history_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"success": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # [QUAN TRỌNG] Đã XÓA hàm get() thứ 2 ở đây đi rồi