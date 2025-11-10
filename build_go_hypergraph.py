#!/usr/bin/env python3
"""
Build HyperGraph from Gene Ontology (GO) Files
Adapted from build_duoclieu_hypergraph.py for GO structure

Key differences:
1. GO has hierarchical relationships (is_a, part_of, regulates)
2. Multiple parents (21% of terms)
3. No chunking needed (text already short ~200 chars)
4. Filtered obsolete terms (only 39,354 active terms)
"""

import os
import sys
import json
import yaml
import pickle
import numpy as np
from pathlib import Path
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any

# Add project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def flatten_go_term_to_facts(term_data: Dict[str, Any]) -> list:
    """
    Flatten GO term JSON to list of fact dictionaries
    Following OG-RAG paper Algorithm 1: Flatten(F)
    
    Key format: "GO <attribute>" (s⊕a concatenation)
    
    Example:
        {
          "GO @type": "GOTerm",
          "GO id": "GO:0006281",
          "GO label": "DNA repair",
          "GO definition": "The process of restoring DNA...",
          "GO is_a_1": "GO:0006259",
          "GO is_a_2": "GO:0006974"
        }
    """
    facts = []
    fact = {}
    
    # Key prefix (subject type)
    key_prefix = "GO"
    
    # Basic fields
    fact[f'{key_prefix} @type'] = "GOTerm"
    fact[f'{key_prefix} id'] = term_data.get('id', '')
    fact[f'{key_prefix} label'] = term_data.get('label', '')
    fact[f'{key_prefix} namespace'] = term_data.get('namespace', '')
    
    # Definition (no chunking - already short)
    definition = term_data.get('definition', '')
    if definition:
        fact[f'{key_prefix} definition'] = definition
    
    # Synonyms
    synonyms_data = term_data.get('synonyms', {})
    all_synonyms = []
    
    if synonyms_data:
        # Collect all synonym types
        for syn_type in ['exact', 'broad', 'narrow', 'related']:
            syns = synonyms_data.get(syn_type, [])
            if syns:
                all_synonyms.extend(syns)
        
        # Store as single field (no chunking needed)
        if all_synonyms:
            fact[f'{key_prefix} synonyms'] = ' | '.join(all_synonyms)
    
    # Relationships - CRITICAL for GO!
    relationships = term_data.get('relationships', {})
    
    if relationships:
        # is_a parents (most important)
        is_a_parents = relationships.get('is_a', [])
        for i, parent_id in enumerate(is_a_parents, 1):
            fact[f'{key_prefix} is_a_{i}'] = parent_id
        
        # part_of
        part_of = relationships.get('part_of', [])
        if part_of:
            fact[f'{key_prefix} part_of'] = ', '.join(part_of)
        
        # regulates
        regulates = relationships.get('regulates', [])
        if regulates:
            fact[f'{key_prefix} regulates'] = ', '.join(regulates)
        
        # positively_regulates
        pos_reg = relationships.get('positively_regulates', [])
        if pos_reg:
            fact[f'{key_prefix} positively_regulates'] = ', '.join(pos_reg)
        
        # negatively_regulates
        neg_reg = relationships.get('negatively_regulates', [])
        if neg_reg:
            fact[f'{key_prefix} negatively_regulates'] = ', '.join(neg_reg)
        
        # occurs_in
        occurs_in = relationships.get('occurs_in', [])
        if occurs_in:
            fact[f'{key_prefix} occurs_in'] = ', '.join(occurs_in)
        
        # has_part
        has_part = relationships.get('has_part', [])
        if has_part:
            fact[f'{key_prefix} has_part'] = ', '.join(has_part)
    
    # Cross-references (optional - can expand in Phase 2)
    xrefs = term_data.get('cross_references', {})
    if xrefs:
        # Only include major databases
        if 'Reactome' in xrefs:
            fact[f'{key_prefix} reactome'] = ', '.join(xrefs['Reactome'][:3])  # Max 3
        
        if 'Wikipedia' in xrefs:
            fact[f'{key_prefix} wikipedia'] = ', '.join(xrefs['Wikipedia'][:1])  # Max 1
    
    facts.append(fact)
    return facts


def build_hypergraph(ontology_dir: str, model_name: str = "BAAI/bge-m3"):
    """
    Build hypergraph from GO ontology files
    
    Args:
        ontology_dir: Directory containing go_term_*.json files
        model_name: Embedding model (default: BAAI/bge-m3)
    """
    print(f"\n{'='*80}")
    print(f"Building HyperGraph from GO Ontology")
    print(f"{'='*80}\n")
    
    # Load embedding model
    print(f"Loading embedding model: {model_name}...")
    model = SentenceTransformer(model_name)
    print(f"✓ Model loaded\n")
    
    # Load all GO term files
    ontology_files = sorted(Path(ontology_dir).glob("go_term_*.json"))
    print(f"Found {len(ontology_files)} GO term files\n")
    
    # Flatten to facts
    print("Flattening GO terms to facts...")
    all_facts = []
    
    for term_file in tqdm(ontology_files, desc="Processing GO terms"):
        with open(term_file, 'r', encoding='utf-8') as f:
            term_data = json.load(f)
        
        facts = flatten_go_term_to_facts(term_data)
        all_facts.extend(facts)
    
    print(f"✓ Created {len(all_facts)} HyperEdges (facts)\n")
    
    # Build HyperNodes (key-value pairs)
    print("Building HyperNodes (key-value pairs)...")
    hypernodes = []
    hypernode_keys = []
    hypernode_values = []
    
    for fact_idx, fact in enumerate(tqdm(all_facts, desc="Extracting nodes")):
        for key, value in fact.items():
            if value and str(value).strip():  # Skip empty values
                hypernodes.append({
                    'fact_idx': fact_idx,
                    'key': key,
                    'value': str(value)
                })
                hypernode_keys.append(key)
                hypernode_values.append(str(value))
    
    print(f"✓ Created {len(hypernodes)} HyperNodes\n")
    
    # Generate embeddings in batches to avoid OOM
    # Build VALUES first (shorter text), then KEYS
    print("Generating embeddings (batched to avoid OOM)...")
    
    # Use smaller batches and process in chunks
    # For MiniLM (smaller model): Can use larger batch_size and chunk_size
    chunk_size = 100000  # Process 100K nodes at a time (larger for small models)
    num_chunks = (len(hypernodes) + chunk_size - 1) // chunk_size
    
    value_embeddings_list = []
    key_embeddings_list = []
    
    # STEP 1: Encode VALUES first
    print(f"\nSTEP 1: Encoding VALUES (shorter text) - {num_chunks} chunks...")
    for chunk_idx in tqdm(range(num_chunks), desc="Encoding VALUE chunks"):
        start_idx = chunk_idx * chunk_size
        end_idx = min((chunk_idx + 1) * chunk_size, len(hypernodes))
        
        chunk_values = hypernode_values[start_idx:end_idx]
        
        chunk_val_emb = model.encode(
            chunk_values,
            batch_size=32,  # Larger batch for smaller models (MiniLM is lightweight)
            show_progress_bar=False,  # Disable inner progress bar
            normalize_embeddings=True
        )
        value_embeddings_list.append(chunk_val_emb)
        
        # Free memory immediately
        del chunk_values, chunk_val_emb
        import gc
        gc.collect()
    
    # Concatenate value embeddings
    print("  Concatenating value embeddings...")
    value_embeddings = np.vstack(value_embeddings_list)
    print(f"✓ Generated {len(value_embeddings):,} value embeddings")
    
    # Free memory
    del value_embeddings_list
    import gc
    gc.collect()
    
    # STEP 2: Encode KEYS
    print(f"\nSTEP 2: Encoding KEYS - {num_chunks} chunks...")
    for chunk_idx in tqdm(range(num_chunks), desc="Encoding KEY chunks"):
        start_idx = chunk_idx * chunk_size
        end_idx = min((chunk_idx + 1) * chunk_size, len(hypernodes))
        
        chunk_keys = hypernode_keys[start_idx:end_idx]
        
        chunk_key_emb = model.encode(
            chunk_keys,
            batch_size=32,  # Larger batch for smaller models (MiniLM is lightweight)
            show_progress_bar=False,  # Disable inner progress bar
            normalize_embeddings=True
        )
        key_embeddings_list.append(chunk_key_emb)
        
        # Free memory immediately
        del chunk_keys, chunk_key_emb
        import gc
        gc.collect()
    
    # Concatenate key embeddings
    print("  Concatenating key embeddings...")
    key_embeddings = np.vstack(key_embeddings_list)
    print(f"✓ Generated {len(key_embeddings):,} key embeddings\n")
    
    # Free memory
    del key_embeddings_list
    import gc
    gc.collect()
    
    # Save hypergraph
    output_dir = Path(ontology_dir)
    
    print("Saving hypergraph components...")
    
    # Save facts (HyperEdges)
    facts_file = output_dir / "go_hypergraph_facts.pkl"
    with open(facts_file, 'wb') as f:
        pickle.dump(all_facts, f)
    print(f"✓ Saved facts to {facts_file}")
    
    # Save hypernodes
    hypernodes_file = output_dir / "go_hypergraph_nodes.pkl"
    with open(hypernodes_file, 'wb') as f:
        pickle.dump(hypernodes, f)
    print(f"✓ Saved hypernodes to {hypernodes_file}")
    
    # Save embeddings
    key_emb_file = output_dir / "go_hypernode_key_embeddings.npy"
    np.save(key_emb_file, key_embeddings)
    print(f"✓ Saved key embeddings to {key_emb_file}")
    
    val_emb_file = output_dir / "go_hypernode_value_embeddings.npy"
    np.save(val_emb_file, value_embeddings)
    print(f"✓ Saved value embeddings to {val_emb_file}")
    
    # Save summary
    summary = {
        'model': model_name,
        'total_terms': len(ontology_files),
        'total_facts': len(all_facts),
        'total_hypernodes': len(hypernodes),
        'embedding_dim': key_embeddings.shape[1],
        'files': {
            'facts': str(facts_file),
            'hypernodes': str(hypernodes_file),
            'key_embeddings': str(key_emb_file),
            'value_embeddings': str(val_emb_file)
        }
    }
    
    summary_file = output_dir / "go_hypergraph_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    print(f"✓ Saved summary to {summary_file}")
    
    print(f"\n{'='*80}")
    print(f"✅ HyperGraph Build Complete!")
    print(f"{'='*80}\n")
    print(f"Summary:")
    print(f"  GO Terms: {summary['total_terms']:,}")
    print(f"  HyperEdges (facts): {summary['total_facts']:,}")
    print(f"  HyperNodes: {summary['total_hypernodes']:,}")
    print(f"  Embedding dimension: {summary['embedding_dim']}")
    print(f"\nOutput directory: {output_dir}\n")
    
    return summary


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Build GO HyperGraph")
    parser.add_argument(
        "--ontology-dir",
        default="data/kg/go/ontology",
        help="Directory containing go_term_*.json files"
    )
    parser.add_argument(
        "--model",
        default="BAAI/bge-m3",
        help="Embedding model name"
    )
    
    args = parser.parse_args()
    
    build_hypergraph(args.ontology_dir, args.model)


if __name__ == "__main__":
    main()
