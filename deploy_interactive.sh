#!/bin/bash
# HƯỚNG DẪN DEPLOY NHANH - Chạy từng lệnh theo thứ tự

echo "=========================================="
echo "🚀 DEPLOY OGRAG2 LÊN HUGGING FACE SPACES"
echo "=========================================="
echo ""

# ============================================
# BƯỚC 1: TẠO HUGGING FACE SPACE
# ============================================
echo "📝 BƯỚC 1: TẠO HUGGING FACE SPACE"
echo ""
echo "1. Truy cập: https://huggingface.co/spaces"
echo "2. Click 'Create new Space'"
echo "3. Điền thông tin:"
echo "   - Space name: ograg2-ontology-qa"
echo "   - License: MIT"
echo "   - SDK: Streamlit"
echo "   - Hardware: CPU basic (free)"
echo "   - Visibility: Public"
echo "4. Click 'Create Space'"
echo ""
read -p "Đã tạo Space xong? Nhấn Enter để tiếp tục..."

# ============================================
# BƯỚC 2: NHẬP THÔNG TIN HF
# ============================================
echo ""
echo "📋 BƯỚC 2: NHẬP THÔNG TIN HUGGING FACE"
echo ""
read -p "Nhập HF username của bạn: " HF_USERNAME
read -p "Nhập Space name vừa tạo (mặc định: ograg2-ontology-qa): " HF_SPACE
HF_SPACE=${HF_SPACE:-ograg2-ontology-qa}

echo ""
echo "✓ Username: $HF_USERNAME"
echo "✓ Space: $HF_SPACE"
echo "✓ URL: https://huggingface.co/spaces/$HF_USERNAME/$HF_SPACE"
echo ""
read -p "Thông tin đúng? Nhấn Enter để tiếp tục..."

# ============================================
# BƯỚC 3: SETUP GIT REMOTE
# ============================================
echo ""
echo "🔗 BƯỚC 3: SETUP GIT REMOTE"
echo ""

# Xóa remote hf cũ nếu có
git remote remove hf 2>/dev/null

# Thêm remote mới
HF_REPO="https://huggingface.co/spaces/$HF_USERNAME/$HF_SPACE"
git remote add hf $HF_REPO

echo "✓ Đã thêm remote: $HF_REPO"

# ============================================
# BƯỚC 4: PUSH CODE LÊN HF
# ============================================
echo ""
echo "⬆️  BƯỚC 4: PUSH CODE LÊN HUGGING FACE"
echo ""
echo "Đang push code..."

git push hf quick-demo-general-ontology:main --force

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Push thành công!"
else
    echo ""
    echo "❌ Push thất bại! Có thể cần đăng nhập HF:"
    echo ""
    echo "Chạy lệnh này và thử lại:"
    echo "huggingface-cli login"
    exit 1
fi

# ============================================
# BƯỚC 5: THÊM API KEY VÀO SECRETS
# ============================================
echo ""
echo "🔐 BƯỚC 5: THÊM API KEY VÀO SECRETS"
echo ""
echo "1. Truy cập: https://huggingface.co/spaces/$HF_USERNAME/$HF_SPACE/settings"
echo "2. Scroll xuống 'Repository secrets'"
echo "3. Click 'New secret'"
echo "4. Nhập:"
echo "   - Name: MEGALLM_API_KEY"
echo "   - Value: sk-mega-cfeefed3f8e0fc99bb83d0026d631532342a1c6543a782433c262d8248506399"
echo "5. Click 'Add secret'"
echo ""
echo "⚠️  QUAN TRỌNG: Phải thêm secret để app hoạt động!"
echo ""
read -p "Đã thêm secret xong? Nhấn Enter để tiếp tục..."

# ============================================
# HOÀN TẤT
# ============================================
echo ""
echo "=========================================="
echo "✅ DEPLOY HOÀN TẤT!"
echo "=========================================="
echo ""
echo "📍 URL Space của bạn:"
echo "   https://huggingface.co/spaces/$HF_USERNAME/$HF_SPACE"
echo ""
echo "⏳ Đợi 5-10 phút để HF build app"
echo ""
echo "📋 Để theo dõi build:"
echo "   https://huggingface.co/spaces/$HF_USERNAME/$HF_SPACE/logs"
echo ""
echo "🎉 Sau khi build xong, share link cho người khác dùng!"
echo ""
