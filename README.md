# 🚀 DH DOW - Advanced Multi-Platform Video Downloader

![DH DOW Banner](https://img.shields.gradient.is/DH-DOW?colorA=6366f1&colorB=06b6d4)
![Version](https://img.shields.io/badge/Version-2.0.0--PRO-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Engines](https://img.shields.io/badge/Engines-You--Get%20%2B%20YT--DLP-purple)

**DH DOW** là ứng dụng tải video đa năng cao cấp tích hợp trực tiếp 2 động cơ hàng đầu: **You-Get** ([github.com/soimort/you-get](https://github.com/soimort/you-get)) và **YT-DLP** ([github.com/yt-dlp/yt-dlp](https://github.com/yt-dlp/yt-dlp)).

Ứng dụng sở hữu giao diện Cyberpunk Glassmorphism hiện đại, hỗ trợ chuyển đổi ngôn ngữ **Tiếng Việt 🇻🇳 / Tiếng Anh 🇬🇧** mượt mà, khởi động cực nhanh và tích hợp thông tin liên hệ tác giả trực quan.

---

## 🛠️ Câu Lệnh Clone 2 Repo Động Cơ & Khởi Tạo Dự Án "DH DOW"

Dưới đây là chuỗi câu lệnh Git chuẩn để bạn clone ứng dụng gốc từ **You-Get** và **YT-DLP** về tích hợp thẳng vào thư mục mã nguồn ứng dụng **DH DOW**:

```bash
# 1. Clone mã nguồn You-Get về thư mục DH-DOW
git clone https://github.com/soimort/you-get.git DH-DOW
cd DH-DOW

# 2. Tích hợp mã nguồn động cơ YT-DLP trực tiếp vào dự án
git clone --depth 1 https://github.com/yt-dlp/yt-dlp.git yt-dlp-src
xcopy /E /I /Y "yt-dlp-src\yt_dlp" "yt_dlp"
cmd /c rmdir /s /q yt-dlp-src

# 3. Xóa lịch sử Git cũ để biến repo thành dự án cá nhân của bạn
cmd /c rmdir /s /q .git

# 4. Khởi tạo lại Repository Git mới cho DH DOW
git init
git add .
git commit -m "Initial commit: DH DOW - Integrated You-Get & YT-DLP Downloader"

# 5. (Tùy chọn) Đẩy lên GitHub cá nhân của bạn
git branch -M main
git remote add origin https://github.com/<tai-khoan-cua-ban>/DH-DOW.git
git push -u origin main
```

---

## ✨ Tính Năng Nổi Bật

1. **Động Cơ Kép Natively Embedded (You-Get + YT-DLP)**:
   - Tích hợp mã nguồn trực tiếp từ 2 dự án mã nguồn mở lớn nhất hiện nay: `you-get` và `yt-dlp`.
   - Tự động fallback và xử lý mã hóa video 4K/1080p, TikTok Shorts, Facebook Reels, Bilibili, Instagram, YouTube,...

2. **Khởi Động Siêu Nhanh (Fast Startup Engine)**:
   - Tối ưu hóa khởi tạo máy chủ chỉ mất chưa tới **0.5 giây**.
   - Tự động mở cửa sổ ứng dụng Native hoặc Trình duyệt mặc định không bị treo lag.

3. **Giao Diện Đỉnh Cao (High Aesthetic Cyberpunk UI)**:
   - Tone màu tối vũ trụ (`#090B13`), thẻ xem trước thông tin video, đồng hồ tốc độ tải thời gian thực (% Progress, MB/s, ETA).

4. **Hỗ Trợ 2 Ngôn Ngữ Thuần (Thuần Việt 🇻🇳 & English 🇬🇧)**:
   - Nút tab chuyển đổi ngôn ngữ instant `[ 🇻🇳 VN | 🇬🇧 ENG ]` ngay góc trên màn hình.

5. **Thông Tin Liên Hệ Tác Giả Trực Quan ("Ấn Vào Mục Sẽ Hiện Ra")**:
   - **Số Điện Thoại**: `0862.610.313` (Ấn vào để Sao Chép SĐT hoặc Gọi Điện).
   - **Facebook**: `https://www.facebook.com/ducduy2512` (Ấn vào để Mở Trang Facebook cá nhân).
   - **Zalo**: `0862.610.313` (Ấn vào để Sao Chép & Mở khung nhắn tin Zalo ngay lập tức).

---

## 🖥️ Hướng Dẫn Khởi Chạy Ứng Dụng

### 1. Cài đặt các thư viện cần thiết:
```bash
py -3 -m pip install -r requirements.txt
```

### 2. Chạy ứng dụng giao diện Desktop / Web App:
```bash
py -3 app.py
```
*(Hoặc nhấp đúp vào file `RUN_DH_DOW.bat`)*

### 3. Đóng gói thành file chạy `.exe` duy nhất:
```bash
py -3 build_exe.py
```
File `DH-DOW.exe` sẽ được tạo trong thư mục `dist/DH-DOW.exe`.

---

## 📞 Thông Tin Liên Hệ Tác Giả

- **Số Điện Thoại**: `0862.610.313`
- **Facebook**: [facebook.com/ducduy2512](https://www.facebook.com/ducduy2512)
- **Zalo**: `0862.610.313`
