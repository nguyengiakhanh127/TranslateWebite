from googletrans import Translator
from translate_app.models import HistoryText, User, Language
from django.core.exceptions import ObjectDoesNotExist

class TranslationService:
    _translator = Translator()

    # Bảng map mã riêng cho Google (Database -> Google API)
    GOOGLE_LANG_MAP = {
        'zh': 'zh-cn', 
    }

    @staticmethod
    def process_translation(user_id: int, text: str, src_lang: str, target_lang: str, save_history: bool = True) -> dict:
        
        print(f"\n>>> [DEBUG] DỊCH: {src_lang} -> {target_lang} | User: {user_id}")

        # 1. CHUẨN BỊ MÃ CHO GOOGLE API
        api_src = TranslationService.GOOGLE_LANG_MAP.get(src_lang, src_lang)
        api_dest = TranslationService.GOOGLE_LANG_MAP.get(target_lang, target_lang)

        # 2. GỌI API DỊCH
        try:
            translation = TranslationService._translator.translate(
                text, src=api_src, dest=api_dest
            )
            translated_text = translation.text
        except Exception as e:
            print(f">>> [ERROR] Google API: {e}")
            raise Exception(f"Lỗi kết nối dịch vụ dịch: {str(e)}")

        # 3. LƯU VÀO DATABASE (CÓ CƠ CHẾ TỰ SỬA LỖI THIẾU NGÔN NGỮ)
        if save_history:
            try:
                # --- [LOGIC MỚI] TỰ ĐỘNG THÊM NGÔN NGỮ NẾU THIẾU ---
                # Kiểm tra Nguồn
                if not Language.objects.filter(pk=src_lang).exists():
                    print(f"⚠️ Thiếu ngôn ngữ '{src_lang}' -> Đang tự động thêm...")
                    Language.objects.create(lang_code=src_lang, lang_name=src_lang.upper())
                
                # Kiểm tra Đích
                if not Language.objects.filter(pk=target_lang).exists():
                    print(f"⚠️ Thiếu ngôn ngữ '{target_lang}' -> Đang tự động thêm...")
                    Language.objects.create(lang_code=target_lang, lang_name=target_lang.upper())

                # --- LƯU LỊCH SỬ ---
                user = User.objects.get(pk=user_id)
                HistoryText.objects.create(
                    user=user,
                    source_lang_id=src_lang,
                    target_lang_id=target_lang,
                    original_text=text,
                    translated_text=translated_text
                )
                print(">>> [SUCCESS] ĐÃ LƯU LỊCH SỬ THÀNH CÔNG!")

            except User.DoesNotExist:
                print(f">>> [ERROR] User ID {user_id} không tồn tại. (Hãy kiểm tra lại Token/Login)")
            except Exception as db_error:
                print(f">>> [ERROR] Lỗi Database: {str(db_error)}")

        return {
            "original_text": text,
            "translated_text": translated_text,
            "src": src_lang,
            "dest": target_lang
        }