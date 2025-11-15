# 🚀 Hướng Dẫn Deploy Lên Hugging Face Spaces

## 🎯 Mục Tiêu
Deploy app OGRag2 lên Hugging Face Spaces với API key của MegaLLM, người dùng chỉ cần vào link và sử dụng trực tiếp.

---

## 📋 2 Phương Pháp Deploy

### **Phương Pháp 1: Dùng Secrets (BẢO MẬT - KHUYẾN NGHỊ)**
API key được lưu an toàn trong Hugging Face Secrets, không xuất hiện trong code.

### **Phương Pháp 2: Hardcode API Key (ĐƠN GIẢN - Space phải Private)**
API key được push trực tiếp trong file yaml. Chỉ dùng cho Private Space.

---

## 🔐 Phương Pháp 1: Dùng Secrets (Khuyến Nghị)

### Bước 1: Tạo Hugging Face Space

1. Truy cập: https://huggingface.co/spaces
2. Click **"Create new Space"**
3. Điền thông tin:
   - **Owner**: Chọn tài khoản của bạn
   - **Space name**: `ograg2-ontology-qa` (hoặc tên bạn muốn)
   - **License**: MIT
   - **Select the Space SDK**: **Streamlit**
   - **Space hardware**: **CPU basic - free** (hoặc upgrade nếu cần)
   - **Space visibility**: **Public** (vì dùng Secrets nên an toàn)
4. Click **"Create Space"**

### Bước 2: Setup Git Remote

```bash
# Thay YOUR_USERNAME bằng username HF của bạn
# Thay SPACE_NAME bằng tên space vừa tạo
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME

# Ví dụ:
# git remote add hf https://huggingface.co/spaces/thuonguyenvan/ograg2-ontology-qa
```

### Bước 3: Push Code Lên HF

```bash
cd /media/thuongnv/New\ Volume/Code/Github/ograg2-1

# Commit các thay đổi
git add -A
git commit -m "feat: prepare for Hugging Face Spaces deployment"

# Push lên HF (branch main)
git push hf quick-demo-general-ontology:main --force
```

**Lưu ý**: Hugging Face Spaces chỉ nhận branch `main`, nên ta push từ branch local `quick-demo-general-ontology` sang `main` trên HF.

### Bước 4: Thêm API Key vào Secrets

1. Truy cập Space vừa tạo: `https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME`
2. Click tab **"Settings"** (góc trên bên phải)
3. Scroll xuống phần **"Repository secrets"**
4. Click **"New secret"**
5. Nhập:
   - **Name**: `MEGALLM_API_KEY`
   - **Value**: `sk-mega-cfeefed3f8e0fc99bb83d0026d631532342a1c6543a782433c262d8248506399`
6. Click **"Add secret"**

### Bước 5: Đợi Build

1. Quay lại tab **"App"**
2. HF sẽ tự động build (mất 5-10 phút lần đầu)
3. Xem logs tại tab **"Logs"** để theo dõi
4. Khi xong, app sẽ tự khởi động

### Bước 6: Test App

1. Upload file ontology (.owl hoặc .obo)
2. Đợi parsing + building (theo dõi progress bar)
3. Thử hỏi câu hỏi
4. Kiểm tra response có đúng không

**✅ Hoàn tất!** Share link Space cho người khác sử dụng.

---

## 🔓 Phương Pháp 2: Hardcode API Key (Đơn Giản)

**⚠️ LƯU Ý**: Chỉ dùng phương pháp này nếu Space là **PRIVATE**!

### Bước 1: Tạo Private Space

Giống Phương Pháp 1 nhưng chọn:
- **Space visibility**: **Private**

### Bước 2: Giữ Nguyên api_keys.yaml

```bash
# File api_keys.yaml đã có sẵn API key, không cần thay đổi
cat api_keys.yaml
# Output:
# MEGALLM_API_KEY: sk-mega-cfeefed3f8e0fc99bb83d0026d631532342a1c6543a782433c262d8248506399
```

### Bước 3: Sửa .gitignore

```bash
# Mở file .gitignore và comment dòng này:
# api_keys.yaml  →  # api_keys.yaml

# Hoặc dùng lệnh:
sed -i 's/^api_keys.yaml$/# api_keys.yaml/' .gitignore
```

### Bước 4: Push Code Lên HF

```bash
# Setup remote
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME

# Commit và push
git add api_keys.yaml .gitignore
git commit -m "feat: add api_keys.yaml for private space"
git push hf quick-demo-general-ontology:main --force
```

### Bước 5: Build & Test

- Đợi build hoàn tất (5-10 phút)
- Test app như Phương Pháp 1

**✅ Hoàn tất!** App chỉ có bạn và người bạn share link mới truy cập được.

---

## 🛠️ Script Tự Động (Phương Pháp 1)

```bash
# Chỉnh sửa deploy_hf.sh với thông tin của bạn
nano deploy_hf.sh

# Thay YOUR_USERNAME và SPACE_NAME trong script

# Chạy script
./deploy_hf.sh
```

---

## 📊 So Sánh 2 Phương Pháp

| Tiêu chí | Phương Pháp 1 (Secrets) | Phương Pháp 2 (Hardcode) |
|----------|-------------------------|--------------------------|
| **Bảo mật** | ✅ Cao - API key không xuất hiện trong code | ⚠️ Thấp - API key trong git history |
| **Space visibility** | ✅ Public hoặc Private | ⚠️ Chỉ Private |
| **Dễ setup** | Medium (cần config Secrets) | ✅ Dễ (chỉ push code) |
| **Khuyến nghị** | ✅ **NÊN DÙNG** | ⚠️ Chỉ dùng cho test/demo |

---

## 🔧 Troubleshooting

### Lỗi "No module named 'xxx'"
```bash
# Kiểm tra requirements.txt có đầy đủ package
cat requirements.txt

# Nếu thiếu, thêm vào và push lại
echo "package-name==version" >> requirements.txt
git add requirements.txt
git commit -m "fix: add missing package"
git push hf quick-demo-general-ontology:main
```

### Lỗi "API key not found"
```bash
# Kiểm tra Secret đã được thêm chưa
# Tên phải chính xác: MEGALLM_API_KEY

# Hoặc kiểm tra code đã đọc từ environment chưa
grep -n "os.getenv('MEGALLM_API_KEY')" app.py
```

### App chạy chậm hoặc Out of Memory
```bash
# Ontology quá lớn, cần upgrade hardware
# Vào Settings > Change hardware > Chọn CPU upgrade (có phí)
```

### Build bị lỗi
```bash
# Xem logs chi tiết tại tab "Logs"
# Thường là lỗi dependencies hoặc syntax error

# Test local trước khi deploy:
streamlit run app.py
```

---

## 📝 Checklist Deploy

- [ ] Tạo Hugging Face Space (Public/Private tùy phương pháp)
- [ ] Setup git remote `hf`
- [ ] Commit tất cả thay đổi
- [ ] Push code lên HF
- [ ] Thêm MEGALLM_API_KEY vào Secrets (Phương pháp 1)
- [ ] Đợi build hoàn tất
- [ ] Test upload ontology
- [ ] Test chat với ontology
- [ ] Share link cho người dùng

---

## 🎉 Kết Quả

Sau khi deploy thành công:

**URL**: `https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME`

**Người dùng có thể**:
- Truy cập link trên
- Upload ontology file (.owl hoặc .obo)
- Hỏi câu hỏi về ontology
- Nhận câu trả lời từ AI với source references

**Không cần**:
- Cài đặt gì
- Có API key riêng
- Biết code
- Run terminal commands

---

## 📧 Hỗ Trợ

Nếu gặp vấn đề:
1. Xem logs tại tab "Logs" trên HF Space
2. Kiểm tra [Hugging Face Docs](https://huggingface.co/docs/hub/spaces)
3. Tham khảo file `DEPLOY_HUGGINGFACE.md` cho thông tin chi tiết hơn
