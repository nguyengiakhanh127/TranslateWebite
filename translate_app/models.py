# File: translate_app/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _

# ==========================================
# 1. DANH MỤC NGÔN NGỮ
# ==========================================
class Language(models.Model):
    # SQL: lang_code VARCHAR(10) NOT NULL PRIMARY KEY
    lang_code = models.CharField(max_length=10, primary_key=True)
    lang_name = models.CharField(max_length=50)

    class Meta:
        db_table = 'languages'
        verbose_name = _('Language')
        verbose_name_plural = _('Languages')

    def __str__(self) -> str:
        return f"{self.lang_name} ({self.lang_code})"


# ==========================================
# 2. NGƯỜI DÙNG (Custom User Model)
# ==========================================
class User(models.Model):
    # Định nghĩa ENUM cho Role để code sạch hơn
    class Role(models.TextChoices):
        ADMIN = 'admin', _('Admin')
        CUSTOMER = 'customer', _('Customer')

    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)  # Lưu hash bcrypt
    email = models.CharField(max_length=100, null=True, blank=True)
    
    # Sử dụng choices để đảm bảo chỉ nhận 'admin' hoặc 'customer'
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.CUSTOMER
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'

    def __str__(self) -> str:
        return self.username


# ==========================================
# 3. CÀI ĐẶT NGƯỜI DÙNG (1-1 Relationship)
# ==========================================
class UserSetting(models.Model):
    # Quan hệ 1:1: Một User chỉ có 1 Setting và ngược lại
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='user_id',
        related_name='settings' # Cho phép truy cập ngược: user.settings
    )
    theme_color = models.CharField(max_length=20, default='light')
    website_language = models.CharField(max_length=10, default='vi')
    audio_speed = models.FloatField(default=1.0)

    class Meta:
        db_table = 'user_settings'

    def __str__(self) -> str:
        return f"Settings of {self.user.username}"


# ==========================================
# 4. PHIÊN ĐĂNG NHẬP (Session)
# ==========================================
class UserSession(models.Model):
    session_token = models.CharField(max_length=255, primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_sessions'


# ==========================================
# 5. LỊCH SỬ: DỊCH VĂN BẢN
# ==========================================
class HistoryText(models.Model):
    trans_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='text_history')
    
    # Liên kết tới bảng Language
    source_lang = models.ForeignKey(
        Language, 
        on_delete=models.DO_NOTHING, 
        db_column='source_lang_code',
        related_name='source_texts'
    )
    target_lang = models.ForeignKey(
        Language, 
        on_delete=models.DO_NOTHING, 
        db_column='target_lang_code',
        related_name='target_texts'
    )
    
    original_text = models.TextField()
    translated_text = models.TextField()
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'history_text'


# ==========================================
# 6. LỊCH SỬ: DỊCH & OCR ẢNH (Đã sửa lỗi E304)
# ==========================================
class HistoryImage(models.Model):
    ocr_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='image_history')
    
    # Thêm related_name='source_images' để phân biệt
    source_lang = models.ForeignKey(
        Language, 
        on_delete=models.DO_NOTHING, 
        db_column='source_lang_code',
        related_name='source_images' 
    )
    # Thêm related_name='target_images' để phân biệt
    target_lang = models.ForeignKey(
        Language, 
        on_delete=models.DO_NOTHING, 
        db_column='target_lang_code',
        related_name='target_images'
    )
    
    image_file_path = models.CharField(max_length=255)
    extracted_text = models.TextField(null=True, blank=True)
    translated_text = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'history_image'


# ==========================================
# 7. LỊCH SỬ: DỊCH PDF (Đã sửa lỗi E304)
# ==========================================
class HistoryPDF(models.Model):
    pdf_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pdf_history')
    
    # Thêm related_name='source_pdfs'
    source_lang = models.ForeignKey(
        Language, 
        on_delete=models.DO_NOTHING, 
        db_column='source_lang_code',
        related_name='source_pdfs'
    )
    # Thêm related_name='target_pdfs'
    target_lang = models.ForeignKey(
        Language, 
        on_delete=models.DO_NOTHING, 
        db_column='target_lang_code',
        related_name='target_pdfs'
    )
    
    original_pdf_path = models.CharField(max_length=255)
    translated_pdf_path = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'history_pdf'