#!/bin/bash
# Quick deploy script for Hugging Face Spaces

echo "🚀 Deploying OGRag2 to Hugging Face Spaces..."
echo ""

# Kiểm tra xem đã có remote hf chưa
if git remote | grep -q "^hf$"; then
    echo "✓ Remote 'hf' đã tồn tại"
else
    echo "❌ Chưa có remote 'hf'. Vui lòng thêm remote:"
    echo ""
    echo "git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME"
    echo ""
    exit 1
fi

# Commit các thay đổi
echo ""
echo "📦 Committing changes..."
git add .
git commit -m "chore: prepare for Hugging Face Spaces deployment" || echo "No changes to commit"

# Push lên Hugging Face Space
echo ""
echo "⬆️  Pushing to Hugging Face Space..."
git push hf quick-demo-general-ontology:main --force

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📝 Next steps:"
echo "1. Truy cập Hugging Face Space của bạn"
echo "2. Vào Settings > Repository secrets"
echo "3. Thêm secret: MEGALLM_API_KEY = sk-mega-cfeefed3f8e0fc99bb83d0026d631532342a1c6543a782433c262d8248506399"
echo "4. Đợi Space rebuild (5-10 phút)"
echo "5. Test app tại: https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME"
echo ""
