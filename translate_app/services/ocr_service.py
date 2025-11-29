# File: translate_app/services/ocr_service.py
import pytesseract
from PIL import Image, ImageOps
import pdfplumber  # <--- THƯ VIỆN MỚI
import os

# Cấu hình Tesseract (Giữ nguyên như cũ)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class OCRService:
    
    LANG_MAP = {
        'vi': 'vie',
        'en': 'eng',
        # ... (các ngôn ngữ khác giữ nguyên)
    }

    @staticmethod
    def extract_text_from_file(file_obj, lang_code='en') -> str:
        """
        Hàm thông minh: Tự động phát hiện PDF hoặc Ảnh để xử lý.
        """
        # 1. Lấy đuôi file (ví dụ: .pdf, .jpg)
        file_name = file_obj.name.lower()
        
        try:
            # === TRƯỜNG HỢP 1: XỬ LÝ PDF ===
            if file_name.endswith('.pdf'):
                return OCRService._process_pdf(file_obj)
            
            # === TRƯỜNG HỢP 2: XỬ LÝ ẢNH ===
            else:
                return OCRService._process_image(file_obj, lang_code)

        except Exception as e:
            print(f"Extraction Error: {str(e)}")
            raise Exception("Lỗi không thể đọc file. Hãy đảm bảo file không bị hỏng.")

    # --- HÀM CON XỬ LÝ ẢNH (Logic cũ chuyển vào đây) ---
    @staticmethod
    def _process_image(image_file, lang_code):
        img = Image.open(image_file)
        img = ImageOps.grayscale(img) # Tối ưu ảnh
        tess_lang = OCRService.LANG_MAP.get(lang_code, 'eng+vie')
        text = pytesseract.image_to_string(img, lang=tess_lang)
        return text.strip()

    # --- HÀM CON XỬ LÝ PDF (Mới) ---
    @staticmethod
    def _process_pdf(pdf_file):
        text_content = []
        
        # pdfplumber có thể đọc trực tiếp từ file object
        with pdfplumber.open(pdf_file) as pdf:
            # Duyệt qua từng trang của PDF
            for page in pdf.pages:
                # Trích xuất text của trang đó
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)
        
        # Nối các trang lại với nhau
        full_text = "\n\n".join(text_content)
        
        if not full_text.strip():
            raise Exception("PDF này là dạng ảnh scan (không có text). Hệ thống chưa hỗ trợ OCR cho PDF scan.")
            
        return full_text