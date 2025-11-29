from translate_app.models import Language

class LanguageService:
    @staticmethod
    def get_all_languages():
        # Lấy tất cả ngôn ngữ, sắp xếp theo tên
        return Language.objects.all().order_by('lang_name')