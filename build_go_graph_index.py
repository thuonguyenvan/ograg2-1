#!/usr/bin/env python3
"""
Build Graph Index from existing GO HyperGraph
Creates lookup tables for graph traversal without rebuilding embeddings

This preserves hypergraph structure while adding graph navigation capability
"""

import os
import sys
import json
import pickle
from pathlib import Path
from collections import defaultdict
from tqdm import tqdm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def build_graph_index(ontology_dir: str):
    """
    Build graph index from existing hypergraph facts
    
    Creates:
    1. go_id_to_fact_idx: Map GO ID → fact index (for fast lookup)
    2. parent_to_children: Map parent GO ID → list of children
    3. child_to_parents: Map child GO ID → list of parents
    4. relationship_graph: Full relationship map (is_a, part_of, regulates, etc.)
    """
    print(f"\n{'='*80}")
    print(f"Building Graph Index from GO HyperGraph")
    print(f"{'='*80}\n")
    
    ontology_dir = Path(ontology_dir)
    
    # Load existing facts
    facts_file = ontology_dir / "go_hypergraph_facts.pkl"
    print(f"Loading facts from {facts_file}...")
    with open(facts_file, 'rb') as f:
        facts = pickle.load(f)
    print(f"✓ Loaded {len(facts):,} facts\n")
    
    # Initialize indexes
    go_id_to_fact_idx = {}  # GO:xxxx → fact index
    parent_to_children = defaultdict(list)  # Parent → [children]
    child_to_parents = defaultdict(list)  # Child → [parents]
    relationship_graph = defaultdict(lambda: defaultdict(list))  # GO ID → {rel_type: [targets]}
    
    print("Building graph indexes...")
    for fact_idx, fact in enumerate(tqdm(facts, desc="Processing facts")):
        go_id = fact.get('GO id', '')
        if not go_id:
            continue
        
        # Index 1: GO ID → fact index (for fast lookup)
        go_id_to_fact_idx[go_id] = fact_idx
        
        # Index 2 & 3: Parent-child relationships (is_a)
        for key in fact.keys():
            if key.startswith('GO is_a_'):
                parent_id = fact[key]
                if parent_id:
                    parent_to_children[parent_id].append(go_id)
                    child_to_parents[go_id].append(parent_id)
                    relationship_graph[go_id]['is_a'].append(parent_id)
        
        # Index 4: Other relationships
        # part_of
        part_of = fact.get('GO part_of', '')
        if part_of:
            for target in part_of.split(', '):
                if target.strip():
                    relationship_graph[go_id]['part_of'].append(target.strip())
        
        # regulates
        regulates = fact.get('GO regulates', '')
        if regulates:
            for target in regulates.split(', '):
                if target.strip():
                    relationship_graph[go_id]['regulates'].append(target.strip())
        
        # positively_regulates
        pos_reg = fact.get('GO positively_regulates', '')
        if pos_reg:
            for target in pos_reg.split(', '):
                if target.strip():
                    relationship_graph[go_id]['positively_regulates'].append(target.strip())
        
        # negatively_regulates
        neg_reg = fact.get('GO negatively_regulates', '')
        if neg_reg:
            for target in neg_reg.split(', '):
                if target.strip():
                    relationship_graph[go_id]['negatively_regulates'].append(target.strip())
    
    # Convert defaultdicts to regular dicts for pickling
    parent_to_children = dict(parent_to_children)
    child_to_parents = dict(child_to_parents)
    relationship_graph = {k: dict(v) for k, v in relationship_graph.items()}
    
    print(f"\n✓ Built indexes:")
    print(f"   GO ID → fact index: {len(go_id_to_fact_idx):,} mappings")
    print(f"   Parent → children: {len(parent_to_children):,} parents")
    print(f"   Child → parents: {len(child_to_parents):,} children")
    print(f"   Full relationship graph: {len(relationship_graph):,} terms\n")
    
    # Save indexes
    print("Saving graph indexes...")
    
    # Index 1
    id_map_file = ontology_dir / "go_id_to_fact_idx.pkl"
    with open(id_map_file, 'wb') as f:
        pickle.dump(go_id_to_fact_idx, f)
    print(f"✓ Saved GO ID map to {id_map_file}")
    
    # Index 2
    parent_file = ontology_dir / "go_parent_to_children.pkl"
    with open(parent_file, 'wb') as f:
        pickle.dump(parent_to_children, f)
    print(f"✓ Saved parent→children to {parent_file}")
    
    # Index 3
    child_file = ontology_dir / "go_child_to_parents.pkl"
    with open(child_file, 'wb') as f:
        pickle.dump(child_to_parents, f)
    print(f"✓ Saved child→parents to {child_file}")
    
    # Index 4
    rel_file = ontology_dir / "go_relationship_graph.pkl"
    with open(rel_file, 'wb') as f:
        pickle.dump(relationship_graph, f)
    print(f"✓ Saved relationship graph to {rel_file}")
    
    # Save summary
    summary = {
        'total_facts': len(facts),
        'total_go_terms': len(go_id_to_fact_idx),
        'total_parent_terms': len(parent_to_children),
        'total_child_terms': len(child_to_parents),
        'total_relationship_terms': len(relationship_graph),
        'files': {
            'id_to_fact_idx': str(id_map_file),
            'parent_to_children': str(parent_file),
            'child_to_parents': str(child_file),
            'relationship_graph': str(rel_file)
        }
    }
    
    summary_file = ontology_dir / "go_graph_index_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    print(f"✓ Saved summary to {summary_file}")
    
    # Show statistics
    print(f"\n{'='*80}")
    print(f"Graph Statistics:")
    print(f"{'='*80}")
    
    # Parent-child stats
    avg_children = sum(len(v) for v in parent_to_children.values()) / len(parent_to_children) if parent_to_children else 0
    avg_parents = sum(len(v) for v in child_to_parents.values()) / len(child_to_parents) if child_to_parents else 0
    
    print(f"Hierarchy (is_a relationships):")
    print(f"  Terms with children: {len(parent_to_children):,}")
    print(f"  Terms with parents: {len(child_to_parents):,}")
    print(f"  Avg children per parent: {avg_children:.2f}")
    print(f"  Avg parents per child: {avg_parents:.2f}")
    
    # Relationship type stats
    rel_type_counts = defaultdict(int)
    for term_rels in relationship_graph.values():
        for rel_type, targets in term_rels.items():
            rel_type_counts[rel_type] += len(targets)
    
    print(f"\nRelationship types:")
    for rel_type, count in sorted(rel_type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {rel_type}: {count:,}")
    
    print(f"\n{'='*80}")
    print(f"✅ Graph Index Build Complete!")
    print(f"{'='*80}\n")
    
    return summary


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Build GO Graph Index")
    parser.add_argument(
        "--ontology-dir",
        default="data/kg/go/ontology",
        help="Directory containing go_hypergraph_facts.pkl"
    )
    
    args = parser.parse_args()
    
    build_graph_index(args.ontology_dir)


if __name__ == "__main__":
    main()
