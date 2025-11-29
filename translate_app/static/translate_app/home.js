// ============================================
// 1. CÁC CHỨC NĂNG GIAO DIỆN CƠ BẢN
// ============================================

function toggleTheme() {
    document.body.classList.toggle("dark-mode");
    localStorage.setItem(
        "theme",
        document.body.classList.contains("dark-mode") ? "dark" : "light"
    );
}

function clearAll() {
    const inputArea = document.getElementById('inputText');
    const outputArea = document.getElementById('output');
    inputArea.value = "";
    outputArea.innerText = "";
    inputArea.focus();
}

async function copyText() {
    const outputArea = document.getElementById('output');
    const textToCopy = outputArea.innerText;

    if (!textToCopy.trim()) {
        alert("⚠️ Chưa có nội dung dịch để sao chép!");
        return;
    }

    try {
        await navigator.clipboard.writeText(textToCopy);
        alert("✅ Đã sao chép văn bản thành công!");
    } catch (err) {
        console.error('Lỗi sao chép:', err);
        alert("❌ Trình duyệt không hỗ trợ sao chép tự động.");
    }
}

// ============================================
// 2. KHỞI TẠO VÀ SỰ KIỆN TẢI TRANG (MAIN)
// ============================================

let allLanguages = [];
let currentDownloadUrl = "";

document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('authToken');
    const username = localStorage.getItem('username');

    // --- KIỂM TRA BẢO MẬT ---
    if (!token) {
        alert("⚠️ Bạn chưa đăng nhập!");
        window.location.href = '/login/';
        return;
    }

    // --- HIỂN THỊ TÊN ---
    if (username) {
        const userDisplay = document.getElementById('userDisplay');
        if (userDisplay) {
            userDisplay.innerText = `👤 Xin chào, ${username}`;
        }
    }

    // --- [MỚI] TẢI LỊCH SỬ NGAY KHI VÀO TRANG ---
    loadHistory();

    // --- TẢI DANH SÁCH NGÔN NGỮ ---
    try {
        const response = await fetch('/api/v1/languages/');
        const result = await response.json();
        
        if (result.success) {
            allLanguages = result.data;
            // Vẽ danh sách bên TRÁI (Nguồn)
            renderLanguages(allLanguages, 'sourceList', 'selectedSourceLang', 'fromLang');
            // Vẽ danh sách bên PHẢI (Đích)
            renderLanguages(allLanguages, 'targetList', 'selectedTargetLang', 'toLang'); 
        }
    } catch (error) {
        console.error("Lỗi tải ngôn ngữ:", error);
    }
});

// ============================================
// 3. XỬ LÝ DROPDOWN & NGÔN NGỮ
// ============================================

function renderLanguages(data, listId, displayId, hiddenInputId) {
    const listElement = document.getElementById(listId);
    if (!listElement) return; // Phòng trường hợp trang không có dropdown
    
    listElement.innerHTML = ''; 

    data.forEach(lang => {
        if (lang.lang_code === 'auto') return;

        const li = document.createElement('li');
        li.innerText = lang.lang_name; 
        
        li.onclick = () => {
            document.getElementById(displayId).innerText = lang.lang_name;
            document.getElementById(hiddenInputId).value = lang.lang_code;
            
            const dropdownId = listId === 'sourceList' ? 'sourceDropdown' : 'targetDropdown';
            toggleDropdown(dropdownId);

            // Tự động dịch khi đổi ngôn ngữ
            const currentInputText = document.getElementById('inputText');
            if (currentInputText && currentInputText.value.trim().length > 0) {
                translateText();
            }
        };
        listElement.appendChild(li);
    });
}

function toggleDropdown(dropdownId) {
    const dropdown = document.getElementById(dropdownId);
    document.querySelectorAll('.custom-options-container').forEach(el => {
        if (el.id !== dropdownId) el.classList.remove('show-dropdown');
    });
    dropdown.classList.toggle('show-dropdown');
}

function filterLanguages(keyword, listId) {
    const lowerKeyword = keyword.toLowerCase();
    const filtered = allLanguages.filter(lang => 
        lang.lang_name.toLowerCase().includes(lowerKeyword)
    );
    if (listId === 'sourceList') {
        renderLanguages(filtered, 'sourceList', 'selectedSourceLang', 'fromLang');
    } else if (listId === 'targetList') {
        renderLanguages(filtered, 'targetList', 'selectedTargetLang', 'toLang');
    }
}

window.onclick = function(event) {
    if (!event.target.closest('.lang-selector-wrapper')) {
        document.querySelectorAll('.custom-options-container').forEach(el => {
            el.classList.remove('show-dropdown');
        });
    }
}

// ============================================
// 4. CHỨC NĂNG DỊCH THUẬT (TEXT)
// ============================================

// Biến hẹn giờ debounce
let timeoutId;
const inputTextBox = document.getElementById('inputText');

// Chỉ gắn sự kiện nếu phần tử tồn tại (để tránh lỗi ở trang file.html)
if (inputTextBox) {
    inputTextBox.addEventListener('input', () => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
            const text = inputTextBox.value.trim();
            if (text.length > 0) { 
                translateText();
            }
        }, 1000); 
    });
}

async function translateText() {
    const textInput = document.getElementById('inputText');
    if (!textInput) return; // Nếu không có ô input (ví dụ trang khác) thì thoát

    const text = textInput.value.trim();
    const sourceLang = document.getElementById('fromLang').value;
    const targetLang = document.getElementById('toLang').value;
    const outputArea = document.getElementById('output');
    const btnTranslate = document.querySelector('.btn-translate');

    if (!text) {
        alert("⚠️ Vui lòng nhập văn bản cần dịch.");
        return;
    }
    if (sourceLang === targetLang) {
        alert("⚠️ Ngôn ngữ nguồn và đích không được giống nhau.");
        return;
    }

    btnTranslate.innerText = "⏳ Đang dịch...";
    btnTranslate.disabled = true;
    outputArea.innerText = "Đang xử lý...";
    outputArea.style.opacity = "0.5";

    try {
        const response = await fetch('/api/v1/translate/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                text: text,
                source_lang: sourceLang,
                target_lang: targetLang,
                user_id: localStorage.getItem('user_id') || 1
            })
        });

        const result = await response.json();

        if (response.ok && result.success) {
            outputArea.innerText = result.data.translated_text;
            // [MỚI] Tải lại lịch sử ngay sau khi dịch xong để cập nhật danh sách
            loadHistory();
        } else {
            outputArea.innerText = "Lỗi: " + (result.message || "Không thể dịch.");
        }

    } catch (error) {
        console.error("Lỗi dịch:", error);
        outputArea.innerText = "❌ Lỗi kết nối Server.";
    } finally {
        btnTranslate.innerText = "🌐 Dịch ngay";
        btnTranslate.disabled = false;
        outputArea.style.opacity = "1";
    }
}

// ============================================
// 5. CHỨC NĂNG TTS & UTILS
// ============================================

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

async function speakText() {
    const outputElement = document.getElementById('output');
    const inputElement = document.getElementById('inputText');
    
    // Ưu tiên đọc output, nếu không có thì đọc input
    const outputText = outputElement ? outputElement.innerText : "";
    const textToSpeak = outputText ? outputText : (inputElement ? inputElement.value : "");
    
    const targetLang = document.getElementById('toLang').value;
    const sourceLang = document.getElementById('fromLang').value;
    const langToSpeak = outputText ? targetLang : sourceLang;

    if (!textToSpeak.trim()) {
        alert("⚠️ Không có nội dung để đọc.");
        return;
    }

    try {
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
            alert("❌ Không thể tạo âm thanh.");
        }
    } catch (error) {
        console.error("Lỗi kết nối:", error);
    }
}

// ============================================
// 6. CHỨC NĂNG LOGOUT
// ============================================

async function logout() {
    if (!confirm("Bạn có chắc muốn đăng xuất?")) {
        return;
    }

    const token = localStorage.getItem('authToken');

    if (token) {
        try {
            await fetch('/api/v1/logout/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Authorization': `Bearer ${token}` 
                }
            });
            console.log("✅ Server đã xóa session.");
        } catch (error) {
            console.error("Lỗi logout server:", error);
        }
    }

    localStorage.removeItem('authToken');
    localStorage.removeItem('username');
    localStorage.removeItem('user_id'); // Xóa cả ID
    
    window.location.href = '/login/';
}

// ============================================
// 7. CHỨC NĂNG LỊCH SỬ (HISTORY) - MỚI
// ============================================

async function loadHistory() {
    const historyList = document.getElementById('historyList');
    if (!historyList) return; 

    const token = localStorage.getItem('authToken');
    if (!token) {
        historyList.innerHTML = '<p style="text-align: center;">Vui lòng đăng nhập để xem lịch sử.</p>';
        return;
    }

    try {
        // Gọi API History kèm Token
        const response = await fetch('/api/v1/history/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        const result = await response.json();

        if (response.ok && result.success) {
            renderHistoryItems(result.data);
        } else {
            if (response.status === 401) logout(); // Token hết hạn thì logout
        }
    } catch (error) {
        console.error("Lỗi tải lịch sử:", error);
        historyList.innerHTML = '<p style="color: #999; text-align: center;">Không thể tải lịch sử.</p>';
    }
}

// File: static/js/script.js

function renderHistoryItems(items) {
    const historyList = document.getElementById('historyList');
    historyList.innerHTML = ''; 

    if (!items || items.length === 0) {
        historyList.innerHTML = '<p style="text-align: center; color: #888; margin-top: 20px;">Chưa có lịch sử dịch nào.</p>';
        return;
    }

    items.forEach(item => {
        const li = document.createElement('li');
        li.className = 'history-item'; 

        // ===========================================================
        // [LOGIC MỚI] XỬ LÝ TÊN NGÔN NGỮ (Auto -> Tiếng Việt)
        // ===========================================================
        let displaySource = item.source_lang;
        let displayTarget = item.target_lang;

        // Kiểm tra nếu nguồn là 'auto' hoặc chứa chữ 'Tự động'
        // (Do trong DB mình lưu là '✨ Tự động phát hiện')
        if (displaySource === 'auto' || displaySource.includes('Tự động')) {
            displaySource = 'Tiếng Việt'; // Ép hiển thị thành Tiếng Việt theo yêu cầu
        }

        // ===========================================================
        // CÁC PHẦN DƯỚI GIỮ NGUYÊN
        // ===========================================================
        
        let contentBox1 = item.original;
        let contentBox2 = item.translated;
        let badgeHtml = '';

        // --- XỬ LÝ THEO LOẠI ---
        if (item.type === 'image') {
            badgeHtml = `<span class="type-badge img">📷 ẢNH/OCR</span>`;
            contentBox1 = formatText(item.original);
            contentBox2 = formatText(item.translated);

        } else if (item.type === 'pdf') {
            badgeHtml = `<span class="type-badge pdf">📄 PDF</span>`;
            contentBox1 = `<span class="file-name-tag">${item.original}</span>`;
            
            if (item.download_url) {
                contentBox2 = `
                    <a href="${item.download_url}" class="download-link" download>
                        📂 ${item.translated} 
                        <span style="font-size: 12px; margin-left: 5px;">(Bấm để tải)</span>
                    </a>
                `;
            } else {
                contentBox2 = `<span style="color: orange;">⏳ Đang xử lý...</span>`;
            }

        } else {
            // Text thường
            badgeHtml = `<span class="type-badge txt">📝 TEXT</span>`;
            contentBox1 = formatText(item.original);
            contentBox2 = formatText(item.translated);
        }

        // --- TẠO HTML (Sử dụng biến displaySource mới xử lý) ---
        li.innerHTML = `
            <div class="history-box source">
                <div class="history-lang-label">
                    ${badgeHtml} ${displaySource} (GỐC) 
                </div>
                <div class="history-content">${contentBox1}</div>
            </div>

            <div class="history-box target">
                <div class="history-lang-label">
                    ${displayTarget} (DỊCH)
                </div>
                <div class="history-content">${contentBox2}</div>
            </div>
        `;

        historyList.appendChild(li);
    });
}

function formatText(text) {
    if (!text) return "";
    return text;
}