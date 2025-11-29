let currentDownloadUrl = "";
let allLanguages = [];
async function speakText() {
    // 1. Chỉ lấy văn bản đích
    const textToSpeak = getTargetText();
    
    // 2. Luôn luôn dùng ngôn ngữ ĐÍCH (Target Lang) để đọc
    const langToSpeak = document.getElementById('toLang').value;

    if (!textToSpeak || !textToSpeak.trim()) {
        alert("⚠️ Chưa có bản dịch để đọc.");
        return;
    }

    try {
        // Hiệu ứng UX
        const btn = document.querySelector('button[onclick="speakText()"]');
        btn.innerText = "⏳ Đang tải...";
        btn.disabled = true;

        // Gọi API TTS
        const response = await fetch('/api/v1/tts/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                text: textToSpeak,
                lang: langToSpeak 
            })
        });

        const result = await response.json();

        if (response.ok && result.success) {
            const audio = new Audio(result.audio_url);
            audio.play();
        } else {
            console.error("Lỗi TTS:", result.message);
            alert("❌ Không thể tạo âm thanh.");
        }

    } catch (error) {
        console.error("Lỗi kết nối:", error);
    } finally {
        // Reset nút bấm
        const btn = document.querySelector('button[onclick="speakText()"]');
        btn.innerText = "🔊 Nghe";
        btn.disabled = false;
    }
}


// 1. Hàm khởi tạo: Gọi API lấy ngôn ngữ khi tải trang
document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('authToken');
    const username = localStorage.getItem('username');

    // --- KIỂM TRA BẢO MẬT ---
    // Nếu không có token (chưa đăng nhập), đuổi về trang login ngay
    if (!token) {
        alert("⚠️ Bạn chưa đăng nhập!");
        window.location.href = '/login/'; // Đảm bảo đường dẫn này đúng với urls.py
        return; 
    }

    // --- HIỂN THỊ TÊN ---
    if (username) {
        const userDisplay = document.getElementById('userDisplay');
        if (userDisplay) {
            userDisplay.innerText = `👤 Xin chào, ${username}`;
        }
    }
    try {
        // 1. Gọi API lấy danh sách ngôn ngữ
        const response = await fetch('/api/v1/languages/');
        const result = await response.json();
        
        if (result.success) {
            // Lưu dữ liệu vào biến toàn cục để dùng cho tính năng tìm kiếm
            allLanguages = result.data;

            // 2. Vẽ danh sách bên TRÁI (Nguồn)
            renderLanguages(allLanguages, 'sourceList', 'selectedSourceLang', 'fromLang');

            // 3. [QUAN TRỌNG] Vẽ danh sách bên PHẢI (Đích)
            // Lỗi của bạn nằm ở đây: Dòng này có thể đang bị thiếu hoặc bị comment
            renderLanguages(allLanguages, 'targetList', 'selectedTargetLang', 'toLang'); 
        }
    } catch (error) {
        console.error("Lỗi tải ngôn ngữ:", error);
    }
});

// 2. Hàm vẽ danh sách HTML
function renderLanguages(data, listId, displayId, hiddenInputId) {
    const listElement = document.getElementById(listId);
    listElement.innerHTML = ''; 

    data.forEach(lang => {
        // Lọc bỏ 'auto' (như bài trước đã làm)
        if (lang.lang_code === 'auto') return;

        const li = document.createElement('li');
        li.innerText = lang.lang_name; 
        
        // --- SỰ KIỆN KHI NGƯỜI DÙNG CHỌN NGÔN NGỮ ---
        li.onclick = () => {
            // 1. Cập nhật giao diện (Hiển thị tên ngôn ngữ mới)
            document.getElementById(displayId).innerText = lang.lang_name;
            
            // 2. Cập nhật giá trị input ẩn (để gửi xuống Backend)
            document.getElementById(hiddenInputId).value = lang.lang_code;
            
            // 3. Đóng dropdown
            const dropdownId = listId === 'sourceList' ? 'sourceDropdown' : 'targetDropdown';
            toggleDropdown(dropdownId);

            // ======================================================
            // [TÍNH NĂNG MỚI] TỰ ĐỘNG DỊCH KHI ĐỔI NGÔN NGỮ
            // ======================================================
            const currentInputText = document.getElementById('inputText').value.trim();
            
            // Chỉ gọi API dịch nếu ô nhập liệu ĐANG CÓ CHỮ
            // Điều này tránh việc gọi API vô nghĩa khi trang vừa load hoặc ô input rỗng
            if (currentInputText.length > 0) {
                // Gọi hàm dịch ngay lập tức
                translateText();
            }
        };
        
        listElement.appendChild(li);
    });
}

// 3. Hàm Bật/Tắt Dropdown
function toggleDropdown(dropdownId) {
    const dropdown = document.getElementById(dropdownId);
    // Đóng tất cả dropdown khác trước khi mở cái này (UX)
    document.querySelectorAll('.custom-options-container').forEach(el => {
        if (el.id !== dropdownId) el.classList.remove('show-dropdown');
    });
    dropdown.classList.toggle('show-dropdown');
}

// 4. Hàm Tìm kiếm (Search)
function filterLanguages(keyword, listId) {
    const lowerKeyword = keyword.toLowerCase();
    
    // Lọc trong mảng gốc
    const filtered = allLanguages.filter(lang => 
        lang.lang_name.toLowerCase().includes(lowerKeyword)
    );

    // Vẽ lại danh sách dựa trên listId
    // Lưu ý: Cần xác định đúng displayId và hiddenInputId tương ứng
    // Ở đây tôi ví dụ logic đơn giản, thực tế bạn nên truyền tham số đầy đủ
    if (listId === 'sourceList') {
        renderLanguages(filtered, 'sourceList', 'selectedSourceLang', 'fromLang');
    }
}

// 5. Đóng dropdown khi click ra ngoài (UX chuẩn)
window.onclick = function(event) {
    if (!event.target.closest('.lang-selector-wrapper')) {
        document.querySelectorAll('.custom-options-container').forEach(el => {
            el.classList.remove('show-dropdown');
        });
    }
}


// ============================================
// CHỨC NĂNG SAO CHÉP (COPY TEXT)
// ============================================
function getTargetText() {
    const outputBox = document.getElementById('output');
    
    // 1. Ưu tiên tìm cột "Bản dịch" trong giao diện File/OCR (Cấu trúc 2 cột)
    const translationCol = outputBox.querySelector('.translation-target .result-content');
    if (translationCol) {
        return translationCol.innerText;
    }
    
    // 2. Nếu không có cột chia (Giao diện Home/Text), lấy toàn bộ text trong output
    return outputBox.innerText;
}

// ============================================
// 1. CHỨC NĂNG SAO CHÉP (CHỈ OUTPUT)
// ============================================
async function copyText() {
    // Chỉ lấy văn bản từ kết quả dịch
    const textToCopy = getTargetText();

    // Kiểm tra: Nếu rỗng thì báo lỗi, TUYỆT ĐỐI KHÔNG lấy input
    if (!textToCopy || !textToCopy.trim()) {
        alert("⚠️ Chưa có bản dịch để sao chép!");
        return;
    }

    try {
        await navigator.clipboard.writeText(textToCopy);
        // Hiệu ứng UX: Đổi chữ nút bấm tạm thời
        const btn = document.querySelector('button[onclick="copyText()"]');
        const oldText = btn.innerText;
        btn.innerText = "✅ Đã chép";
        setTimeout(() => btn.innerText = oldText, 2000);
        
    } catch (err) {
        console.error('Lỗi sao chép:', err);
        alert("❌ Trình duyệt không hỗ trợ sao chép tự động.");
    }
}

function toggleTheme() {
  document.body.classList.toggle("dark-mode");
  localStorage.setItem(
    "theme",
    document.body.classList.contains("dark-mode") ? "dark" : "light"
  );
}

function handleFileSelect() {
    const fileInput = document.getElementById('fileInput');
    const fileNameDisplay = document.getElementById('fileNameDisplay');
            
            // Icon hiển thị cho đẹp
    const dropZone = document.querySelector('.file-drop-zone');
            
    if(fileInput.files.length > 0) {
        const file = fileInput.files[0];
        fileNameDisplay.innerText = "✅ Đã chọn: " + file.name;
                
        // Kiểm tra loại file (Ảnh hay PDF)
        if (file.type.startsWith('image/')) {
        // Có thể hiển thị preview ảnh nhỏ ở đây nếu muốn
        }
    }
}

// Hàm lấy CSRF Token (Dùng lại từ script chung)
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

async function translateFile() {
            const fileInput = document.getElementById('fileInput');
            const sourceLang = document.getElementById('fromLang').value;
            const targetLang = document.getElementById('toLang').value;
            const outputBox = document.getElementById('output');
            const btnTranslate = document.querySelector('.btn-translate');

            // Reset link download cũ mỗi khi bấm dịch mới
            currentDownloadUrl = null; 

            if (fileInput.files.length === 0) {
                alert("⚠️ Vui lòng chọn một file ảnh hoặc PDF trước!");
                return;
            }

            // UX Loading
            btnTranslate.innerText = "⏳ Đang xử lý...";
            btnTranslate.disabled = true;
            outputBox.innerHTML = "<i>Đang tải file lên và dịch...</i>";

            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            formData.append('source_lang', sourceLang);
            formData.append('target_lang', targetLang);

            try {
                const response = await fetch('/api/v1/ocr-translate/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: formData
                });

                const result = await response.json();

                if (response.ok && result.success) {
                    // [QUAN TRỌNG] Lưu link tải từ Server vào biến toàn cục
                    console.log("Link tải về:", result.data.download_url); // Debug xem có link không
                    currentDownloadUrl = result.data.download_url;

                    // Hiển thị kết quả 2 cột
                    outputBox.innerHTML = `
                        <div class="result-container">
                            <div class="result-col ocr-source">
                                <div class="result-label"><span>📷 Trích xuất</span></div>
                                <div class="result-content">${result.data.extracted_text}</div>
                            </div>
                            <div class="result-col translation-target">
                                <div class="result-label"><span>🌐 Bản dịch</span></div>
                                <div class="result-content">${result.data.translated_text}</div>
                            </div>
                        </div>
                    `;
                    outputBox.removeAttribute("data-placeholder");
                } else {
                    outputBox.innerHTML = `<p style="color: red;">❌ ${result.message || "Lỗi xử lý"}</p>`;
                }

            } catch (error) {
                console.error(error);
                outputBox.innerText = "❌ Lỗi kết nối Server.";
            } finally {
                btnTranslate.innerText = "🚀 Trích xuất & Dịch";
                btnTranslate.disabled = false;
            }
        }

function downloadResult() {
            if (!currentDownloadUrl) {
                alert("⚠️ Chưa có file kết quả từ server (Hãy bấm Dịch trước)!");
                return;
            }
            
            // Tạo thẻ a ảo để tải file thật từ Server
            const link = document.createElement('a');
            link.href = currentDownloadUrl;
            link.setAttribute('download', ''); // Gợi ý trình duyệt tải về thay vì mở tab mới
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }

async function logout() {
    if (!confirm("Bạn có chắc muốn đăng xuất?")) {
        return;
    }

    const token = localStorage.getItem('authToken');

    if (token) {
        try {
            // 1. Gọi API báo Server xóa token trong DB
            await fetch('/api/v1/logout/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                    // Gửi token lên để Server biết xóa cái nào
                    'Authorization': `Bearer ${token}` 
                }
            });
            console.log("✅ Server đã xóa session.");
        } catch (error) {
            console.error("Lỗi logout server:", error);
            // Dù server lỗi thì Client vẫn phải logout để bảo vệ người dùng
        }
    }

    // 2. Xóa sạch dấu vết ở Client (Như cũ)
    localStorage.removeItem('authToken');
    localStorage.removeItem('username');
    
    // 3. Chuyển hướng
    window.location.href = '/login/';
}