#!/usr/bin/env python3
"""
Test GO Hypergraph Query
Quick test to verify the hypergraph works correctly
"""

import pickle
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
import json

def load_hypergraph(ontology_dir: str):
    """Load hypergraph components"""
    print("Loading hypergraph components...")
    
    # Load facts
    with open(Path(ontology_dir) / "go_hypergraph_facts.pkl", 'rb') as f:
        facts = pickle.load(f)
    print(f"✓ Loaded {len(facts):,} facts")
    
    # Load hypernodes
    with open(Path(ontology_dir) / "go_hypergraph_nodes.pkl", 'rb') as f:
        hypernodes = pickle.load(f)
    print(f"✓ Loaded {len(hypernodes):,} hypernodes")
    
    # Load embeddings
    key_embeddings = np.load(Path(ontology_dir) / "go_hypernode_key_embeddings.npy")
    value_embeddings = np.load(Path(ontology_dir) / "go_hypernode_value_embeddings.npy")
    print(f"✓ Loaded embeddings: {key_embeddings.shape}")
    
    return facts, hypernodes, key_embeddings, value_embeddings


def query_hypergraph(query: str, facts, hypernodes, key_embeddings, value_embeddings, 
                     model, top_k: int = 5):
    """
    Query hypergraph using OG-RAG dual ranking approach
    
    Following paper Algorithm 2:
    1. Encode query
    2. Compute similarity with keys (attribute matching)
    3. Compute similarity with values (content matching)
    4. Combine scores
    5. Return top-k facts
    """
    print(f"\n{'='*80}")
    print(f"Query: {query}")
    print(f"{'='*80}\n")
    
    # Encode query
    query_emb = model.encode([query], normalize_embeddings=True)[0]
    
    # Compute similarities
    key_scores = np.dot(key_embeddings, query_emb)
    value_scores = np.dot(value_embeddings, query_emb)
    
    # Dual ranking: combine key and value scores
    # Paper uses max of key and value scores per hypernode
    combined_scores = np.maximum(key_scores, value_scores)
    
    # Get top-k hypernodes
    top_indices = np.argsort(combined_scores)[-top_k:][::-1]
    
    # Map to facts
    fact_scores = {}
    for idx in top_indices:
        hypernode = hypernodes[idx]
        fact_idx = hypernode['fact_idx']
        score = combined_scores[idx]
        
        if fact_idx not in fact_scores or score > fact_scores[fact_idx]['score']:
            fact_scores[fact_idx] = {
                'score': score,
                'key': hypernode['key'],
                'value': hypernode['value']
            }
    
    # Sort by score
    ranked_facts = sorted(fact_scores.items(), key=lambda x: x[1]['score'], reverse=True)
    
    # Display results
    print(f"Top {len(ranked_facts)} results:\n")
    
    for i, (fact_idx, info) in enumerate(ranked_facts[:top_k], 1):
        fact = facts[fact_idx]
        
        print(f"{i}. Score: {info['score']:.4f}")
        print(f"   Matched: {info['key']} = {info['value'][:100]}...")
        print(f"   GO ID: {fact.get('GO id', 'N/A')}")
        print(f"   Label: {fact.get('GO label', 'N/A')}")
        print(f"   Namespace: {fact.get('GO namespace', 'N/A')}")
        
        if 'GO definition' in fact:
            definition = fact['GO definition']
            print(f"   Definition: {definition[:200]}...")
        
        # Show relationships
        relationships = []
        for key in fact.keys():
            if 'is_a' in key or 'part_of' in key or 'regulates' in key:
                relationships.append(f"{key}: {fact[key]}")
        
        if relationships:
            print(f"   Relationships: {relationships[:2]}")
        
        print()
    
    return ranked_facts


def main():
    # Load hypergraph
    ontology_dir = "data/kg/go/ontology"
    facts, hypernodes, key_embeddings, value_embeddings = load_hypergraph(ontology_dir)
    
    # Load model (same as used for building)
    print("\nLoading embedding model...")
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    print("✓ Model loaded\n")
    
    # Test queries
    test_queries = [
        "DNA repair",
        "What is mitochondrial respiration?",
        "cell division process",
        "protein phosphorylation",
        "immune response"
    ]
    
    for query in test_queries:
        results = query_hypergraph(
            query, 
            facts, 
            hypernodes, 
            key_embeddings, 
            value_embeddings, 
            model,
            top_k=3
        )
        
        input("\nPress Enter for next query...")


if __name__ == "__main__":
    main()
