# OG-RAG for Gene Ontology

**Ontology-Grounded Retrieval-Augmented Generation** applied to Gene Ontology (GO) for biological knowledge retrieval and question answering.

Based on paper: [OG-RAG: Ontology-Grounded Retrieval-Augmented Generation](https://arxiv.org/html/2412.15235v1)

---

## 🔬 Project Overview

This implementation applies the OG-RAG methodology to **Gene Ontology**, a structured knowledge base of biological terms and their relationships. The system enables accurate retrieval and generation of answers to biological questions.

**Dataset:**
- **39,354 active GO terms** (filtered from 51,842 total, removing 12,488 obsolete)
- **3 namespaces**: biological_process, molecular_function, cellular_component  
- **Hierarchical relationships**: is_a, part_of, regulates, etc.

**Performance:**
- Build time: ~10 minutes (with MiniLM)
- Query time: ~1-2 seconds
- 286,288 hypernodes, 39,354 facts

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

### 2. Download & Process GO Ontology

```bash
# Download
wget http://purl.obolibrary.org/obo/go/go-basic.owl

# Parse (creates 39,354 JSON files)
python scripts/parse_go_owl.py \
    --owl-file go-basic.owl \
    --output-dir data/kg/go/ontology

# Build hypergraph (~10 minutes)
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
