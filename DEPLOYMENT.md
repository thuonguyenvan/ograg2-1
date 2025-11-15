# 🚀 Deployment Guide for US Team

Quick guide to deploy OG-RAG system for testing.

---

## 📋 Prerequisites

- Python 3.8 or higher
- 8GB RAM minimum (16GB recommended for large ontologies)
- 10GB free disk space
- Internet connection (for downloading models)

---

## ⚡ Quick Deploy (5 minutes)

### 1. Clone or Download Project

```bash
# If you have git
git clone https://github.com/thuonguyenvan/ograg2-1.git
cd ograg2-1

# Or download and extract ZIP
```

### 2. Install Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements_webapp.txt
```

### 3. Set Groq API Key (Optional)

**Option 1: Using api_keys.yaml file (Recommended)**

Edit `api_keys.yaml` in project root:
```yaml
GROQ_API_KEY: gsk_your_api_key_here
```

**Option 2: Using environment variable**
```bash
# Linux/Mac
export GROQ_API_KEY='gsk_...'

# Windows
set GROQ_API_KEY=gsk-...
```

**Get free Groq API key:** https://console.groq.com/keys

**Note:** Without API key, system still works but returns raw facts instead of generated answers.

### 4. Launch Web Interface

```bash
streamlit run app.py
```

**Browser opens automatically at:** `http://localhost:8501`

---

## 🧪 Test with Sample Ontology

### Option 1: Gene Ontology (Recommended for demo)

```bash
# Download GO (Small version - ~30MB)
wget http://purl.obolibrary.org/obo/go/go-basic.owl

# Or full browser download from:
# http://geneontology.org/docs/download-ontology/
```

**Processing time:** ~10 minutes  
**Sample questions:**
- "What is DNA repair?"
- "How does cell division work?"
- "What is apoptosis?"

### Option 2: Human Phenotype Ontology

```bash
wget http://purl.obolibrary.org/obo/hp.owl
```

**Sample questions:**
- "What is diabetes?"
- "What are symptoms of autism?"

### Option 3: Sequence Ontology

```bash
wget http://purl.obolibrary.org/obo/so.owl
```

**Sample questions:**
- "What is a gene?"
- "What is an exon?"

---

## 📖 Usage Instructions

### Step 1: Upload Ontology

1. Open web interface (http://localhost:8501)
2. Click "Choose an OWL file"
3. Select downloaded .owl file
4. Click "Process Ontology"

### Step 2: Monitor Progress

Processing happens in 2 phases:

1. **PARSING** (30-40% of time)
   - Extracting terms and relationships
   - Creating structured data

2. **BUILDING** (60-70% of time)
   - Generating embeddings
   - Building knowledge graph

**Total time:**
- Small ontology (<5K terms): 2-5 minutes
- Medium (5K-20K terms): 5-10 minutes
- Large (>20K terms): 10-20 minutes

### Step 3: Chat!

Once status shows **READY**:
1. Click "Chat" button
2. Type questions in natural language
3. Get AI-powered answers

---

## 🔧 Troubleshooting

### Port Already in Use

```bash
# Use different port
streamlit run app.py --server.port 8502
```

### Out of Memory

**Solution 1:** Close other applications

**Solution 2:** Use smaller ontology for testing

**Solution 3:** Reduce batch size in `build_hypergraph.py`:
```python
batch_size = 16  # Line 133, reduce from 32
```

### Slow Processing

**Expected behavior:**
- First time downloads embedding model (~100MB)
- Large ontologies take longer
- Progress updates every 1000 terms

**To speed up:**
- Use SSD storage
- Close browser tabs
- Use faster CPU

### Groq API Errors

**Without API key:** System returns retrieved facts (still useful!)

**With API key errors:**
- Check key is valid: https://console.groq.com/keys
- Check API key format: should start with `gsk_`
- Edit `api_keys.yaml` file with correct key
- Or set environment variable: `export GROQ_API_KEY='gsk_...'`
- Check rate limits: Groq has generous free tier (30 req/min)

---

## 💻 Command-Line Testing

For testing without web interface:

```bash
# 1. Parse OWL
python scripts/parse_owl.py \
    --owl-file go-basic.owl \
    --output-dir test_output

# 2. Build hypergraph
python build_hypergraph.py \
    --ontology-dir test_output

# 3. Query
python query_engine/generic_query_engine.py \
    --ontology-dir test_output \
    --query "What is DNA repair?" \
    --no-llm
```

**Or use demo script:**
```bash
./demo.sh go-basic.owl
```

---

## 🌐 Remote Access (Optional)

To access from other computers on network:

```bash
streamlit run app.py \
    --server.address 0.0.0.0 \
    --server.port 8501
```

Access from other computers: `http://[server-ip]:8501`

**Security note:** Only use on trusted networks!

---

## 📊 System Requirements by Ontology Size

| Ontology Size | RAM  | Disk  | Time    |
|---------------|------|-------|---------|
| Small (<5K)   | 4GB  | 500MB | 2-5 min |
| Medium (5-20K)| 8GB  | 2GB   | 5-10 min|
| Large (>20K)  | 16GB | 5GB   | 10-20min|
| GO (50K)      | 16GB | 2GB   | 15 min  |

---

## 🔍 Verification Checklist

After deployment, verify:

- [ ] Web interface loads
- [ ] Can upload OWL file
- [ ] Processing starts (status updates)
- [ ] Processing completes (status = READY)
- [ ] Can click "Chat" button
- [ ] Can send messages
- [ ] Receives responses
- [ ] Retrieved terms shown in expander

---

## 📁 File Structure (After First Upload)

```
ograg2-1/
├── app.py                    # Web interface
├── data/
│   └── ontologies/          # Workspace
│       ├── ontologies_index.json
│       └── [id]/            # Each ontology
│           ├── ontology.owl
│           └── parsed/
│               ├── term_*.json      # ~10MB per 1K terms
│               ├── hypergraph_*.pkl # ~20MB
│               └── *.npy            # ~400MB per 10K terms
└── ...
```

**Disk space per ontology:**
- Parsing: ~10MB per 1000 terms
- Embeddings: ~40MB per 1000 terms
- **Total: ~50MB per 1000 terms**

---

## 🆘 Support

### Common Issues

**"Module not found"**
```bash
pip install -r requirements_webapp.txt
```

**"Permission denied"**
```bash
chmod +x demo.sh
```

**"Streamlit not found"**
```bash
pip install streamlit
```

### Get Help

1. Check error message in terminal
2. Review troubleshooting section above
3. Check file paths are correct
4. Verify OWL file is valid

---

## 🎯 Success Criteria

System is working correctly if:

1. ✅ Can upload OWL file
2. ✅ Processing completes without errors
3. ✅ Status shows "READY"
4. ✅ Can ask questions
5. ✅ Receives relevant answers
6. ✅ Retrieved terms match query

---

## 🔄 Updating

To update to latest version:

```bash
git pull origin main
pip install -r requirements_webapp.txt --upgrade
```

---

## 🛑 Stopping the System

```bash
# In terminal running streamlit:
Ctrl+C

# To completely stop:
# Close terminal or:
pkill -f streamlit
```

---

## 📞 Contact

For questions during testing, check:
- README_WEBAPP.md - Full documentation
- Logs in terminal - Error messages
- Browser console - JavaScript errors

---

**Ready to test! 🎉**

Start with: `streamlit run app.py`
