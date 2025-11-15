# Deploy OGRag2 to Hugging Face Spaces

## Bước 1: Tạo Hugging Face Space

1. Truy cập https://huggingface.co/spaces
2. Đăng nhập hoặc tạo tài khoản
3. Click "Create new Space"
4. Điền thông tin:
   - **Space name**: ograg2-general-ontology (hoặc tên bạn muốn)
   - **License**: MIT
   - **Select the Space SDK**: Streamlit
   - **Space hardware**: CPU basic (free) hoặc upgrade nếu cần
   - **Visibility**: Public hoặc Private

## Bước 2: Setup Git và Push Code

```bash
# Di chuyển vào thư mục project
cd /media/thuongnv/New\ Volume/Code/Github/ograg2-1

# Thêm Hugging Face Space làm remote
# Thay YOUR_USERNAME bằng username Hugging Face của bạn
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/ograg2-general-ontology

# Push code lên Hugging Face Space
git push hf quick-demo-general-ontology:main --force
```

**Lưu ý**: Hugging Face Spaces chỉ chấp nhận branch `main`, nên ta push từ branch `quick-demo-general-ontology` sang `main` của HF Space.

## Bước 3: Cấu hình API Key trên Hugging Face

**QUAN TRỌNG**: Không nên push API key trực tiếp lên git. Thay vào đó, dùng Secrets của Hugging Face:

1. Truy cập Space của bạn trên Hugging Face
2. Click vào tab "Settings"
3. Scroll xuống phần "Repository secrets"
4. Click "New secret"
5. Thêm secret:
   - **Name**: `MEGALLM_API_KEY`
   - **Value**: `sk-mega-cfeefed3f8e0fc99bb83d0026d631532342a1c6543a782433c262d8248506399`
6. Click "Save"

## Bước 4: Sửa app.py để đọc API key từ Environment

Cần sửa file `app.py` để đọc API key từ environment variables (Hugging Face Secrets) thay vì file yaml:

```python
# Thay thế hàm load_api_keys() bằng:
def load_api_keys():
    """Load API keys from environment or yaml file"""
    # Ưu tiên lấy từ environment (Hugging Face Secrets)
    megallm_key = os.getenv('MEGALLM_API_KEY')
    if megallm_key:
        return {'MEGALLM_API_KEY': megallm_key}
    
    # Fallback: đọc từ file yaml (cho local development)
    api_keys_file = Path(__file__).parent / "api_keys.yaml"
    if api_keys_file.exists():
        with open(api_keys_file, 'r') as f:
            return yaml.safe_load(f)
    return {}
```

## Bước 5: Tạo file requirements.txt cho Hugging Face

Hugging Face Spaces tự động cài packages từ `requirements.txt`:

```bash
# Copy requirements cho HF
cp requirements_huggingface.txt requirements.txt

# Commit và push
git add requirements.txt
git commit -m "Add requirements.txt for Hugging Face Spaces"
git push hf quick-demo-general-ontology:main
```

## Bước 6: Đợi Build và Test

1. Hugging Face sẽ tự động build Space (mất 5-10 phút)
2. Xem logs tại tab "Logs" để theo dõi quá trình build
3. Khi build xong, Space sẽ tự động khởi động
4. Truy cập URL của Space (ví dụ: https://huggingface.co/spaces/YOUR_USERNAME/ograg2-general-ontology)

## Bước 7: Test trên Production

1. Upload file ontology (.owl hoặc .obo)
2. Đợi processing hoàn tất
3. Thử hỏi câu hỏi về ontology
4. Kiểm tra response có chính xác không

## Lưu ý Quan Trọng

### Storage
- Hugging Face Spaces có giới hạn storage (thường 50GB)
- Nên thêm `.gitignore` để không commit các file data lớn:
  ```
  data/ontologies/*/parsed/*.npy
  data/ontologies/*/parsed/*.pkl
  ```

### Performance
- Free tier có RAM hạn chế (16GB)
- Nếu ontology quá lớn, có thể cần upgrade hardware
- Cân nhắc thêm cache để tránh rebuild hypergraph mỗi lần restart

### Security
- **KHÔNG BAO GIỜ** commit api_keys.yaml vào git public
- Luôn dùng Hugging Face Secrets cho API keys
- Có thể set Space là Private nếu cần bảo mật

## Troubleshooting

### Lỗi "Module not found"
- Kiểm tra `requirements.txt` có đầy đủ dependencies
- Xem logs để biết package nào thiếu

### Lỗi "Out of memory"
- Ontology quá lớn, cần upgrade hardware
- Hoặc optimize code để giảm memory usage

### Lỗi API key
- Kiểm tra Secret đã được set đúng tên `MEGALLM_API_KEY`
- Kiểm tra code đã đọc từ environment variables

### App không start
- Xem logs chi tiết tại tab "Logs"
- Kiểm tra file `app.py` có lỗi syntax không
- Kiểm tra port 7860 (default của Streamlit trên HF)

## Alternative: Deploy với API Key Hardcoded (Không Khuyến Nghị)

Nếu muốn đơn giản hơn (nhưng kém bảo mật):

1. Set Space là **Private**
2. Giữ nguyên `api_keys.yaml` trong code
3. Push trực tiếp lên (HF sẽ có file này)

**Lưu ý**: Cách này chỉ nên dùng cho Space Private, không dùng cho Public Space.
