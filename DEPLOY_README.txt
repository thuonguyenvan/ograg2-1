==========================================
🚀 DEPLOY OGRAG2 LÊN HUGGING FACE SPACES
==========================================

📚 Có 3 file hướng dẫn:

1. ⚡ DEPLOY_QUICK_GUIDE.md
   → Hướng dẫn đầy đủ 2 phương pháp (Secrets & Hardcode)
   → Có so sánh, troubleshooting, checklist
   
2. 📖 DEPLOY_HUGGINGFACE.md
   → Hướng dẫn chi tiết từng bước
   → Giải thích rõ từng config
   
3. 🤖 deploy_interactive.sh
   → Script tự động, chạy và làm theo hướng dẫn
   → Nhập username/space name và tự động deploy

==========================================
🎯 CÁCH DEPLOY NHANH NHẤT
==========================================

OPTION 1: Dùng Script Tự Động (KHUYẾN NGHỊ)
-------------------------------------------
$ ./deploy_interactive.sh

→ Script sẽ hướng dẫn từng bước
→ Tự động push code lên HF
→ Nhắc bạn thêm API key vào Secrets


OPTION 2: Deploy Thủ Công
-------------------------------------------

1. Tạo HF Space:
   https://huggingface.co/spaces → Create new Space
   - Name: ograg2-ontology-qa
   - SDK: Streamlit
   - Visibility: Public

2. Thêm git remote:
   $ git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/ograg2-ontology-qa

3. Push code:
   $ git push hf quick-demo-general-ontology:main --force

4. Thêm Secret:
   - Vào Settings > Repository secrets
   - Name: MEGALLM_API_KEY
   - Value: sk-mega-cfeefed3f8e0fc99bb83d0026d631532342a1c6543a782433c262d8248506399

5. Đợi build (5-10 phút)

6. Test app tại: https://huggingface.co/spaces/YOUR_USERNAME/ograg2-ontology-qa

==========================================
📋 ĐÃ CHUẨN BỊ SẴN
==========================================

✅ README.md - Có HF Space header (title, emoji, sdk...)
✅ app.py - Đọc API key từ environment (HF Secrets)
✅ requirements.txt - Dependencies cho HF Spaces
✅ .streamlit/config.toml - Config cho HF
✅ .gitignore - Loại bỏ file lớn không cần thiết
✅ deploy_hf.sh - Script deploy nhanh
✅ deploy_interactive.sh - Script deploy có hướng dẫn

==========================================
🔐 API KEY
==========================================

Đã sẵn sàng trong api_keys.yaml:
sk-mega-cfeefed3f8e0fc99bb83d0026d631532342a1c6543a782433c262d8248506399

⚠️  QUAN TRỌNG:
- File api_keys.yaml KHÔNG được push lên git (có trong .gitignore)
- Phải thêm API key vào HF Secrets (bước 4 ở trên)
- App sẽ tự động đọc từ environment variable MEGALLM_API_KEY

==========================================
✨ SAU KHI DEPLOY
==========================================

Người dùng chỉ cần:
1. Vào link HF Space của bạn
2. Upload file ontology (.owl hoặc .obo)
3. Đợi processing (có progress bar)
4. Hỏi câu hỏi trong chat
5. Nhận câu trả lời từ AI

KHÔNG CẦN:
❌ Cài đặt gì
❌ Có API key
❌ Biết code
❌ Chạy terminal

==========================================
📞 HỖ TRỢ
==========================================

Nếu gặp lỗi:
1. Xem logs tại HF Space: Tab "Logs"
2. Đọc file DEPLOY_QUICK_GUIDE.md phần "Troubleshooting"
3. Kiểm tra Secret đã thêm đúng chưa (tên: MEGALLM_API_KEY)

==========================================
