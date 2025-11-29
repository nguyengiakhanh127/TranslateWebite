from django.urls import path
from .views import UserRegistrationView, UserLoginView
from translate_app.views import RegisterPageView, LoginPageView, LanguageListView, TranslateTextView, TextToSpeechView, FileTranslateView, UserLogoutView, HistoryListView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register_api'),
    path('login/', UserLoginView.as_view(), name='login_api'),
    path('logout/', UserLogoutView.as_view(), name='logout_api'),
    path('languages/', LanguageListView.as_view(), name='language_list_api'),
    path('translate/', TranslateTextView.as_view(), name='translate_api'),
    path('tts/', TextToSpeechView.as_view(), name='tts_api'),
    path('ocr-translate/', FileTranslateView.as_view(), name='ocr_translate_api'),
    path('history/', HistoryListView.as_view(), name='history_list_api'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)