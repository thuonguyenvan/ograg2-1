# 🧬 OG-RAG - Universal Ontology Q&A System

**Upload any OWL ontology → Chat with AI**

Zero configuration needed! The system automatically:
- Detects ontology type and structure
- Parses terms, relationships, and hierarchies
- Builds knowledge graph with embeddings
- Enables natural language Q&A

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_webapp.txt
```

### 2. Set OpenAI API Key (Optional but recommended)

```bash
export OPENAI_API_KEY='your-api-key-here'
```

Without API key, system returns retrieved facts without LLM generation.

### 3. Run Web Application

```bash
streamlit run app.py
```

Open browser at `http://localhost:8501`

---

## 📖 Usage

### Step 1: Upload OWL File

1. Click "Choose an OWL file"
2. Select any OBO-formatted ontology (.owl file)
3. Click "Process Ontology"

**Processing time:**
- Small ontologies (~1K terms): 2-3 minutes
- Medium (~10K terms): 5-10 minutes
- Large (~50K terms like GO): 10-15 minutes

### Step 2: Wait for Processing

The system will:
1. **Parse** - Extract terms and relationships (30-40% of time)
2. **Build** - Generate embeddings (60-70% of time)
3. **Ready** - Query engine loaded

You can monitor progress in the ontology list.

### Step 3: Chat!

Once status shows "READY", click "Chat" button and start asking questions!

**Example questions:**
- "What is DNA repair?"
- "How does cell division work?"
- "What processes are involved in metabolism?"

---

## 🎯 Supported Ontologies

Works with **any OBO-formatted OWL ontology**, including:

- **Gene Ontology (GO)** - Biological processes, molecular functions
- **Sequence Ontology (SO)** - Genomic features
- **Chemical Entities (ChEBI)** - Chemical compounds
- **Uberon** - Anatomical structures
- **Cell Ontology (CL)** - Cell types
- **Disease Ontology (DO)** - Human diseases
- **Human Phenotype (HP)** - Phenotypic abnormalities
- **And hundreds more...**

---

## 📁 Project Structure

```
ograg2-1/
├── app.py                          # Streamlit web interface
├── ontology_manager.py             # Multi-ontology management
├── build_hypergraph.py             # Generic hypergraph builder
├── scripts/
│   └── parse_owl.py               # Generic OWL parser
├── query_engine/
│   └── generic_query_engine.py    # Query engine
├── requirements_webapp.txt         # Python dependencies
└── data/
    └── ontologies/                # Workspace for uploaded ontologies
        ├── ontologies_index.json  # Registry
        └── [ontology_id]/         # Individual ontologies
            ├── ontology.owl       # Original OWL file
            ├── parsed/            # Parsed JSON terms
            │   ├── term_*.json
            │   ├── ontology_metadata.json
            │   ├── hypergraph_*.pkl
            │   └── *.npy          # Embeddings
            └── ...
```

---

## 🔧 Command-Line Tools

### Parse OWL File

```bash
python scripts/parse_owl.py \
    --owl-file path/to/ontology.owl \
    --output-dir path/to/output
```

### Build Hypergraph

```bash
python build_hypergraph.py \
    --ontology-dir path/to/parsed_ontology \
    --model sentence-transformers/all-MiniLM-L6-v2
```

### Query via CLI

```bash
python query_engine/generic_query_engine.py \
    --ontology-dir path/to/parsed_ontology \
    --query "What is DNA repair?"
```

---

## ⚙️ Configuration

### Embedding Models

Default: `sentence-transformers/all-MiniLM-L6-v2` (fast, 384 dim)

For better quality, use:
```bash
python build_hypergraph.py \
    --ontology-dir path/to/parsed \
    --model BAAI/bge-m3
```

### LLM Models

Default: GPT-4 (requires OpenAI API key)

To disable LLM generation:
```bash
# Don't set OPENAI_API_KEY
# System will return raw retrieval results
```

---

## 📊 Performance

### Processing Time (on standard laptop)

| Ontology Size | Parse Time | Build Time | Total |
|---------------|------------|------------|-------|
| Small (~1K)   | 10-20s     | 1-2 min    | 2-3 min |
| Medium (~10K) | 1-2 min    | 5-8 min    | 7-10 min |
| Large (~50K)  | 2-3 min    | 8-12 min   | 10-15 min |

### Query Time

- Retrieval: 0.5-1 second
- + LLM generation: 2-5 seconds
- **Total: ~3-6 seconds per question**

### Disk Space

- Small ontology: 50-100 MB
- Medium ontology: 200-500 MB
- Large ontology (GO): 1-2 GB

---

## 🐛 Troubleshooting

### "Out of memory" during processing

**Solution:** Use smaller embedding model or reduce batch size

Edit `build_hypergraph.py`:
```python
chunk_size = 50000  # Reduce from 100000
batch_size = 16     # Reduce from 32
```

### Processing stuck at "PARSING"

**Solution:** Check OWL file format. Must be OBO-formatted OWL.

### "No relevant information found"

**Possible causes:**
1. Query is too vague
2. Ontology doesn't contain relevant terms
3. Try rephrasing query

---

## 🌟 Features

### ✅ Fully Automatic
- No configuration files needed
- Auto-detects ontology type
- Auto-discovers relationships

### ✅ Universal
- Works with ANY OBO-formatted OWL
- Handles different relationship types
- Supports optional namespaces

### ✅ Fast Processing
- Streaming parser (low memory)
- Batched embedding generation
- Optimized for large ontologies

### ✅ Smart Retrieval
- Dual ranking (key + value)
- Hierarchical expansion
- Graph-aware search

### ✅ Multi-Ontology
- Manage multiple ontologies
- Switch between them
- Independent processing

---

## 📚 Examples

### Example 1: Gene Ontology

```bash
# Download GO
wget http://purl.obolibrary.org/obo/go/go-basic.owl

# Use web interface
streamlit run app.py
# Upload go-basic.owl
# Wait 10-15 minutes
# Chat: "What is DNA repair?"
```

### Example 2: Human Phenotype Ontology

```bash
# Download HPO
wget http://purl.obolibrary.org/obo/hp.owl

# Upload via web interface
# Ask: "What are symptoms of diabetes?"
```

### Example 3: Chemical Entities

```bash
# Download ChEBI
wget http://purl.obolibrary.org/obo/chebi.owl

# Upload via web interface
# Ask: "What is glucose?"
```

---

## 🔒 Security

- All data stored locally in `data/ontologies/`
- No external uploads (except OpenAI API for LLM)
- Each ontology isolated in separate directory

---

## 📄 License

MIT License - See LICENSE file

---

## 🙏 Acknowledgments

Based on paper: **OG-RAG: Ontology-Grounded Retrieval-Augmented Generation**

Ontologies from: [OBO Foundry](http://obofoundry.org/)

---

## 💡 Tips

### For Best Results:

1. **Use specific questions** - "What is mitosis?" better than "Tell me about cells"
2. **Include domain terms** - Use ontology-specific terminology
3. **Try variations** - Rephrase if first attempt doesn't work
4. **Check retrieved terms** - Expand the "Retrieved terms" section to verify relevance

### For Faster Processing:

1. Use MiniLM model (default)
2. Close other applications
3. Use SSD storage
4. Increase RAM if possible

---

## 🆘 Support

For issues or questions:
1. Check troubleshooting section above
2. Verify OWL file is OBO-formatted
3. Check logs in terminal for detailed errors

---

**Happy querying! 🚀**
