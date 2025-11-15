---
title: OGRag2 - General Ontology QA
emoji: 🧬
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: 1.31.0
app_file: app.py
pinned: false
license: mit
python_version: 3.10
---

# OG-RAG for General Ontologies

**Ontology-Grounded Retrieval-Augmented Generation** - A web application that allows you to upload any ontology and ask questions using AI-powered retrieval.

Based on paper: [OG-RAG: Ontology-Grounded Retrieval-Augmented Generation](https://arxiv.org/html/2412.15235v1)

---

## 🌐 Live Demo

Try it now: [Hugging Face Space](https://huggingface.co/spaces/YOUR_USERNAME/ograg2-general-ontology)

## ✨ Features

- 📤 **Upload any ontology**: Supports OWL and OBO formats
- 🤖 **AI-powered Q&A**: Ask questions in natural language
- 🔍 **Smart retrieval**: Uses hypergraph-based retrieval with embeddings
- 📊 **Source references**: Shows which ontology terms were used to generate answers
- 🎯 **General purpose**: Works with any ontology from any domain

## 🚀 Quick Start

---

## 🚀 Quick Start

### 1. Setup

```bash
git clone https://github.com/thuonguyenvan/ograg2-1.git
cd ograg2-1
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup API keys
cp api_keys.yaml.template api_keys.yaml
# Edit and add your OpenAI API key
```

### 2. Build GO Hypergraph & Embeddings

**⚠️ Important:** Large binary files (.npy, .pkl embeddings) are NOT in Git repo. You need to build them locally.

**Option A: Quick Build (Recommended - ~10 minutes)**
```bash
# GO term JSONs are already in repo, just build embeddings
python build_go_hypergraph.py \
    --ontology-dir data/kg/go/ontology \
    --model sentence-transformers/all-MiniLM-L6-v2
```

This creates:
- `go_hypergraph_facts.pkl` (19 MB)
- `go_hypergraph_nodes.pkl` (22 MB)  
- `go_hypernode_key_embeddings.npy` (420 MB)
- `go_hypernode_value_embeddings.npy` (420 MB)
- Graph structure files (*.pkl, ~5 MB total)

**Option B: Full Build from Scratch (if you need fresh GO data)**
```bash
# 1. Download GO ontology
wget http://purl.obolibrary.org/obo/go/go-basic.owl

# 2. Parse OWL → JSON (creates 39,354 JSON files)
python scripts/parse_go_owl.py \
    --owl-file go-basic.owl \
    --output-dir data/kg/go/ontology

# 3. Build hypergraph
python build_go_hypergraph.py \
    --ontology-dir data/kg/go/ontology \
    --model sentence-transformers/all-MiniLM-L6-v2
```

### 3. Query

```python
from query_engine.go_query_engine import GOQueryEngine

engine = GOQueryEngine()
answer = engine.query("What is DNA repair?")
print(answer)
```

---

## 📁 Structure

```
├── scripts/parse_go_owl.py          # Parse OWL → JSON
├── build_go_hypergraph.py           # Build hypergraph
├── query_engine/go_query_engine.py  # Complete OG-RAG
├── test_go_query_engine.py          # Full test
├── configs/go/config_go.yaml        # Configuration
└── data/kg/go/ontology/            # GO data
    ├── go_term_*.json              # 39K terms
    └── go_hypergraph_*.pkl/npy     # Embeddings
```

---

## 🎯 Features

### Dual Ranking Retrieval
- Key similarity (GO attributes)
- Value similarity (definitions, synonyms)
- Combined scoring: `max(key_score, value_score)`

### Hierarchical Expansion
- Auto-expand with parent terms (is_a)
- Configurable depth (default: 2 levels)

### LLM Generation  
- GPT-4 for comprehensive answers
- Structured context with GO terms + relationships

---

## 📈 Performance Comparison

| Model | Params | Build Time | Accuracy |
|-------|--------|------------|----------|
| BGE-M3 | 560M | 8-10 hours | Best |
| MiniLM-L6 | 22M | ~10 min | Very Good ✅ |

**50x faster** with MiniLM while maintaining high accuracy for biological terms!

---

## 🧪 Example

```python
from query_engine.go_query_engine import GOQueryEngine

engine = GOQueryEngine(top_k=5, hierarchical_depth=2)

# Get answer with context
result = engine.query(
    "How does cell division work?",
    return_context=True,
    verbose=True
)

print(result['answer'])
print(f"\nRetrieved {len(result['retrieved_facts'])} GO terms")
```

---

## 📚 Sample Questions

- What is DNA repair? → GO:0006281
- How does cell division work? → GO:0051301  
- What is protein phosphorylation? → GO:0006468
- What processes are involved in cellular respiration? → GO:0045333

---

## 📄 License

MIT

## 📖 Citation

```bibtex
@article{ograg2024,
  title={OG-RAG: Ontology-Grounded Retrieval-Augmented Generation},
  journal={arXiv preprint arXiv:2412.15235},
  year={2024}
}
```
