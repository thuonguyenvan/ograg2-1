#!/usr/bin/env python3
"""
Debug script to check if context is being retrieved and used correctly
"""

import os
import sys
import yaml
from pathlib import Path
from sentence_transformers import SentenceTransformer
from unittest.mock import MagicMock
import numpy as np
import importlib.util
import pickle

# Add project root
sys.path.insert(0, str(Path(__file__).parent))

# Mock modules
sys.modules['azureml'] = MagicMock()
sys.modules['azureml.rag'] = MagicMock()
sys.modules['azureml.rag.utils'] = MagicMock()
sys.modules['azureml.rag.utils.connections'] = MagicMock()
sys.modules['langchain_together'] = MagicMock()
sys.modules['llama_index.legacy'] = MagicMock()
sys.modules['llama_index.legacy.embeddings'] = MagicMock()

def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot_product / (norm1 * norm2)

utils_mock = MagicMock()
utils_mock.cosine_similarity = cosine_similarity
utils_mock.flatten_tree = lambda node: [node] if isinstance(node, dict) else []
utils_mock.load_graph_nodes = lambda path: []
utils_mock.load_graph_nodes_chunks = lambda path, chunks: ([], [])
sys.modules['utils'] = utils_mock

# Load ontograph module
spec = importlib.util.spec_from_file_location(
    "ontograph_module",
    "query_engine/ontograph_query_engine.py"
)
ontograph_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ontograph_module)

OntoHyperGraph = ontograph_module.OntoHyperGraph
OntoHyperGraphQueryEngine = ontograph_module.OntoHyperGraphQueryEngine

from langchain_groq import ChatGroq

print("="*80)
print("🔍 OG-RAG CONTEXT RETRIEVAL DEBUG")
print("="*80)

# Load config
with open("configs/duoclieu/config_simple.yaml", 'r') as f:
    config = yaml.safe_load(f)

# Load API keys
with open("api_keys.yaml", 'r') as f:
    api_keys = yaml.safe_load(f)
    for key, value in api_keys.items():
        if value:
            os.environ[key] = str(value)

print("\n1️⃣ Loading embedding model...")
embed_model = SentenceTransformer(config['embedding']['model_name'])

# Add LangChain compatibility
def embed_query(text):
    return embed_model.encode(text, normalize_embeddings=True)

def embed_documents(texts):
    return embed_model.encode(texts, normalize_embeddings=True)

embed_model.embed_query = embed_query
embed_model.embed_documents = embed_documents

print("✅ Embedding model loaded")

print("\n2️⃣ Loading hypergraph...")
hypergraph_dir = Path(config['hypergraph_dir'])
with open(hypergraph_dir / 'hypergraph_facts.pkl', 'rb') as f:
    facts = pickle.load(f)
with open(hypergraph_dir / 'hypergraph_embeddings.pkl', 'rb') as f:
    embeddings_dict = pickle.load(f)

hypergraph = OntoHyperGraph.from_fact_lists(
    facts=facts,
    embed_model=embed_model,
    embeddings=embeddings_dict
)
print(f"✅ Loaded {len(hypergraph.nodes)} nodes, {len(hypergraph.edges)} edges")

print("\n3️⃣ Initializing LLM...")
llm = ChatGroq(
    model=config['llm']['model_name'],
    temperature=config['llm']['temperature'],
    max_tokens=config['llm']['max_tokens'],
)
print("✅ LLM initialized")

print("\n4️⃣ Creating query engine...")
query_engine = OntoHyperGraphQueryEngine(
    llm=llm,
    onto_hypergraph=hypergraph
)
print("✅ Query engine ready")

# Test query
print("\n" + "="*80)
print("🧪 TEST QUERY")
print("="*80)

question = "Cây nghệ có công dụng gì?"
print(f"\nQuestion: {question}")

print("\n📦 Retrieving context...")
response, context = query_engine.query(
    query_str=question,
    top_k=5,
    nodes_top_k=20,
    return_context=True
)

print(f"\n✅ Retrieved {len(context)} contexts:")
print("-"*80)

for i, ctx in enumerate(context, 1):
    print(f"\n{i}. {ctx}")
    print("-"*40)

# Extract answer
if hasattr(response, 'content'):
    answer = response.content
elif hasattr(response, 'response'):
    answer = response.response
else:
    answer = str(response)

print("\n" + "="*80)
print("💬 LLM ANSWER:")
print("="*80)
print(answer)

# Check if answer uses context
print("\n" + "="*80)
print("🔍 ANALYSIS:")
print("="*80)

# Look for keywords from contexts in answer
context_str = " ".join([str(c) for c in context]).lower()
answer_lower = answer.lower()

# Extract some key terms from context
import re
context_terms = set()
for ctx in context:
    ctx_str = str(ctx)
    # Extract Vietnamese words (simple approach)
    words = re.findall(r'[\w\u00C0-\u1EF9]+', ctx_str)
    context_terms.update([w for w in words if len(w) > 3])

# Check overlap
answer_words = set(re.findall(r'[\w\u00C0-\u1EF9]+', answer_lower))
overlap = context_terms & answer_words

print(f"✓ Context keywords: {len(context_terms)}")
print(f"✓ Answer keywords: {len(answer_words)}")
print(f"✓ Overlap: {len(overlap)} keywords")
overlap_ratio = len(overlap)/len(context_terms)*100 if context_terms else 0
print(f"✓ Overlap ratio: {overlap_ratio:.1f}%")

print(f"\n✓ Sample overlapping terms:")
for term in list(overlap)[:10]:
    print(f"   - {term}")

# Check if context mentions are in answer
nghệ_in_context = any('nghệ' in str(c).lower() for c in context)
nghệ_in_answer = 'nghệ' in answer_lower

print(f"\n✓ 'nghệ' in context: {nghệ_in_context}")
print(f"✓ 'nghệ' in answer: {nghệ_in_answer}")

print("\n" + "="*80)
print("🎯 VERDICT:")
print("="*80)

if len(overlap) > 10 and overlap_ratio > 20:
    print("✅ LLM is USING context from hypergraph retrieval!")
else:
    print("❌ LLM may be using its own knowledge instead of context!")
    print("   This suggests the RAG_QUERY_PROMPT needs stronger constraints")
