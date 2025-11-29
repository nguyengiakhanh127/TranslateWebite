document.addEventListener('DOMContentLoaded', () => {
    const registerBtn = document.getElementById('registerBtn');
    const msgElement = document.getElementById('registerMsg');

    // Hàm lấy CSRF Token từ Cookie của Django (Bắt buộc bảo mật)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Hàm xử lý đăng ký
    async function handleRegister() {
        // 1. Reset thông báo cũ
        msgElement.innerText = '';
        msgElement.style.color = 'black';
        registerBtn.disabled = true; // Chặn bấm liên tục
        registerBtn.innerText = 'Đang xử lý...';

        // 2. Lấy dữ liệu từ Input
        const username = document.getElementById('username').value.trim();
        const email = document.getElementById('regEmail').value.trim();
        const password = document.getElementById('regPassword').value;
        const confirmPassword = document.getElementById('regPasswordConfirm').value;

        // 3. Validation phía Client (Nhanh)
        if (!username || !email || !password) {
            msgElement.innerText = "⚠️ Vui lòng điền đầy đủ thông tin.";
            msgElement.style.color = 'red';
            registerBtn.disabled = false;
            registerBtn.innerText = 'Đăng ký';
            return;
        }

        if (password !== confirmPassword) {
            msgElement.innerText = "⚠️ Mật khẩu xác nhận không khớp.";
            msgElement.style.color = 'red';
            registerBtn.disabled = false;
            registerBtn.innerText = 'Đăng ký';
            return;
        }

        // 4. Chuẩn bị gửi Request
        // Lưu ý: Thay đổi URL này cho đúng với urls.py của bạn
        const apiUrl = '/api/v1/register/'; 
        
        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken') // Gắn thẻ bài bảo mật
                },
                body: JSON.stringify({
                    username: username,
                    email: email,
                    password: password
                })
            });

            const data = await response.json();

            // 5. Xử lý phản hồi từ Server
            if (response.ok) {
                // HTTP 201 Created
                msgElement.innerText = "✅ " + data.message;
                msgElement.style.color = 'green';
                
                // Tùy chọn: Chuyển hướng sang trang đăng nhập sau 2 giây
                setTimeout(() => {
                    window.location.href = '/login/'; // Sửa lại đường dẫn trang login của bạn
                }, 2000);
            } else {
                // HTTP 400 Bad Request
                // Backend trả về lỗi chi tiết trong data.errors (nếu có) hoặc data.message
                let errorMsg = data.message || "Đăng ký thất bại.";
                
                // Nếu Serializer trả về lỗi cụ thể từng trường (Ví dụ: Username trùng)
                if (data.errors) {
                    // Lấy lỗi đầu tiên tìm thấy để hiển thị
                    const firstKey = Object.keys(data.errors)[0];
                    errorMsg = `${data.errors[firstKey][0]}`;
                }
                
                msgElement.innerText = "❌ " + errorMsg;
                msgElement.style.color = 'red';
            }

        } catch (error) {
            console.error('Error:', error);
            msgElement.innerText = "❌ Lỗi kết nối Server.";
            msgElement.style.color = 'red';
        } finally {
            // Mở lại nút bấm
            registerBtn.disabled = false;
            registerBtn.innerText = 'Đăng ký';
        }
    }

    // Gắn sự kiện click
    registerBtn.addEventListener('click', handleRegister);
});