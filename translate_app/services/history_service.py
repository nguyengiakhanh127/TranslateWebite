# File: translate_app/services/history_service.py
from translate_app.models import HistoryText, HistoryImage, HistoryPDF
from django.conf import settings

class HistoryService:
    
    @staticmethod
    def get_user_history(user_id: int):
        combined_history = []

        # 1. TEXT (Giữ nguyên)
        texts = HistoryText.objects.filter(user_id=user_id).select_related('source_lang', 'target_lang')
        for item in texts:
            combined_history.append({
                "type": "text",
                "id": item.trans_id,
                "source_lang": item.source_lang.lang_name,
                "target_lang": item.target_lang.lang_name,
                "original": item.original_text,
                "translated": item.translated_text,
                "created_at": item.created_at
            })

        # 2. ẢNH (CẬP NHẬT LỚN)
        # Thay vì trả về link tải, ta trả về TEXT đã lưu trong DB
        images = HistoryImage.objects.filter(user_id=user_id).select_related('source_lang', 'target_lang')
        for item in images:
            combined_history.append({
                "type": "image",
                "id": item.ocr_id,
                "source_lang": item.source_lang.lang_name,
                "target_lang": item.target_lang.lang_name,
                
                # [QUAN TRỌNG] Lấy nội dung text từ DB ra
                "original": item.extracted_text if item.extracted_text else "[Không có text trích xuất]",
                "translated": item.translated_text if item.translated_text else "[Chưa có bản dịch]",
                
                "created_at": item.created_at
            })

        # 3. PDF (Vẫn giữ logic cũ vì DB chưa lưu text của PDF)
        # File: translate_app/services/history_service.py

        # ... (các phần trên giữ nguyên)

        # 3. Lịch sử PDF (SỬA LẠI ĐOẠN NÀY)
        pdfs = HistoryPDF.objects.filter(user_id=user_id).select_related('source_lang', 'target_lang')
        for item in pdfs:
            # Xử lý đường dẫn file kết quả
            if item.translated_pdf_path:
                trans_filename = item.translated_pdf_path.split('/')[-1]
                trans_url = f"{settings.MEDIA_URL}{item.translated_pdf_path}"
            else:
                trans_filename = "Đang xử lý..."
                trans_url = ""

            combined_history.append({
                "type": "pdf",
                "id": item.pdf_id,
                "source_lang": item.source_lang.lang_name,
                "target_lang": item.target_lang.lang_name,
                
                # Box 1: Tên file gốc
                "original": item.original_pdf_path.split('/')[-1],
                
                # Box 2: Tên file dịch (để hiển thị)
                "translated": trans_filename,
                
                # [QUAN TRỌNG] Gửi kèm link tải
                "download_url": trans_url,
                
                "created_at": item.created_at
            })

        # ... (phần sort và return giữ nguyên)

        # 4. Sắp xếp
        combined_history.sort(key=lambda x: x['created_at'], reverse=True)

        return combined_history