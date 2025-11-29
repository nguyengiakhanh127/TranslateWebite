from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# [QUAN TRỌNG] Import RedirectView để xử lý chuyển hướng
from django.views.generic import RedirectView 

from translate_app.views import (
    LoginPageView, 
    RegisterPageView, 
    HomePageView, 
    FileTranslationView
)

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='login_page', permanent=False), name='root'),
    path('admin/', admin.site.urls),
    path('login/', LoginPageView.as_view(), name='login_page'),       # <--- Nó sẽ nhảy vào đây
    path('register/', RegisterPageView.as_view(), name='register_page'),
    path('home/', HomePageView.as_view(), name='home_page'),
    path('file/', FileTranslationView.as_view(), name='file_page'),
    path('api/v1/', include('translate_app.urls')), 
]

# Cấu hình Media (như đã làm ở bài trước)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)