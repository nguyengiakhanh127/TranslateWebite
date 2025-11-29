// File: static/js/login.js

// ===============================================
// 1. TỰ ĐỘNG KIỂM TRA ĐĂNG NHẬP (Auto-Login Check)
// ===============================================
document.addEventListener('DOMContentLoaded', () => {
    // Kiểm tra xem trong túi có "vé" chưa
    const token = localStorage.getItem('authToken');

    if (token) {
        // Nếu đã có Token, người dùng không cần đăng nhập lại
        // Chuyển hướng ngay lập tức sang trang chủ
        window.location.href = '/home/'; 
    }
});
// Hàm lấy CSRF Token từ Cookie của Django
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Kiểm tra xem cookie này có bắt đầu bằng tên mình cần không
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

async function login() {
    // 1. Lấy các phần tử giao diện
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const msgElement = document.getElementById('loginMsg');
    const btnElement = document.querySelector('button'); // Nút đăng nhập

    // 2. Reset trạng thái
    msgElement.innerText = '';
    btnElement.disabled = true;
    btnElement.innerText = 'Đang kiểm tra...';

    // 3. Lấy giá trị input
    const username = usernameInput.value.trim();
    const password = passwordInput.value;

    // Validate sơ bộ
    if (!username || !password) {
        msgElement.innerText = "⚠️ Vui lòng nhập tên đăng nhập và mật khẩu.";
        msgElement.style.color = "red";
        btnElement.disabled = false;
        btnElement.innerText = 'Đăng nhập';
        return;
    }

    try {
        // 4. Gửi Request lên Backend
        // LƯU Ý: Đường dẫn phải khớp với cấu hình trong urls.py
        const response = await fetch('/api/v1/login/', { 
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken') // Thẻ bài bảo mật
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });

        const data = await response.json();

        // 5. Xử lý kết quả
        if (response.ok && data.success) {
            // --- THÀNH CÔNG ---
            msgElement.innerText = "✅ Đăng nhập thành công! Đang chuyển hướng...";
            msgElement.style.color = "green";

            // [QUAN TRỌNG] Lưu Token vào LocalStorage
            // Đây là "chiếc vé" để dùng cho các tính năng sau này (Dịch, OCR...)
            localStorage.setItem('authToken', data.data.token);
            localStorage.setItem('username', data.data.username);

            // Chuyển hướng sang trang chủ (Ví dụ: index.html hoặc dashboard)
            setTimeout(() => {
                window.location.href = '/home'; 
            }, 1000);

        } else {
            // --- THẤT BẠI ---
            // Hiển thị thông báo lỗi từ Backend trả về
            msgElement.innerText = "❌ " + (data.message || "Đăng nhập thất bại.");
            msgElement.style.color = "red";
        }

    } catch (error) {
        console.error("Lỗi:", error);
        msgElement.innerText = "❌ Không thể kết nối đến Server.";
        msgElement.style.color = "red";
    } finally {
        // Mở lại nút bấm
        btnElement.disabled = false;
        btnElement.innerText = 'Đăng nhập';
    }
}