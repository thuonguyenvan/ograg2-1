"""
GO Graph-Aware Retriever
Combines embedding-based retrieval with graph structure traversal
"""

import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Set


class GOGraphRetriever:
    """
    Graph-aware retriever for GO terms
    
    Combines:
    1. Semantic retrieval (embedding similarity)
    2. Graph traversal (parent/child/relationship expansion)
    """
    
    def __init__(self, ontology_dir: str, model=None):
        """
        Load hypergraph + graph indexes
        
        Args:
            ontology_dir: Path to ontology directory
            model: SentenceTransformer model (optional, for re-ranking)
        """
        ontology_dir = Path(ontology_dir)
        
        # Load hypergraph components
        print("Loading hypergraph...")
        with open(ontology_dir / "go_hypergraph_facts.pkl", 'rb') as f:
            self.facts = pickle.load(f)
        
        with open(ontology_dir / "go_hypergraph_nodes.pkl", 'rb') as f:
            self.hypernodes = pickle.load(f)
        
        self.key_embeddings = np.load(ontology_dir / "go_hypernode_key_embeddings.npy")
        self.value_embeddings = np.load(ontology_dir / "go_hypernode_value_embeddings.npy")
        
        # Load graph indexes
        print("Loading graph indexes...")
        with open(ontology_dir / "go_id_to_fact_idx.pkl", 'rb') as f:
            self.go_id_to_fact_idx = pickle.load(f)
        
        with open(ontology_dir / "go_parent_to_children.pkl", 'rb') as f:
            self.parent_to_children = pickle.load(f)
        
        with open(ontology_dir / "go_child_to_parents.pkl", 'rb') as f:
            self.child_to_parents = pickle.load(f)
        
        with open(ontology_dir / "go_relationship_graph.pkl", 'rb') as f:
            self.relationship_graph = pickle.load(f)
        
        self.model = model
        
        print(f"✓ Loaded {len(self.facts):,} facts")
        print(f"✓ Loaded {len(self.hypernodes):,} hypernodes")
        print(f"✓ Loaded {len(self.go_id_to_fact_idx):,} GO term mappings")
        print(f"✓ Loaded {len(self.parent_to_children):,} parent→children edges")
        print(f"✓ Loaded {len(self.child_to_parents):,} child→parent edges\n")
    
    def retrieve_semantic(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Pure semantic retrieval (original hypergraph method)
        """
        if self.model is None:
            raise ValueError("Model required for semantic retrieval")
        
        # Encode query
        query_emb = self.model.encode([query], normalize_embeddings=True)[0]
        
        # Dual ranking
        key_scores = np.dot(self.key_embeddings, query_emb)
        value_scores = np.dot(self.value_embeddings, query_emb)
        combined_scores = np.maximum(key_scores, value_scores)
        
        # Get top hypernodes
        top_indices = np.argsort(combined_scores)[-(top_k*3):][::-1]
        
        # Map to facts
        fact_scores = {}
        for idx in top_indices:
            hypernode = self.hypernodes[idx]
            fact_idx = hypernode['fact_idx']
            score = float(combined_scores[idx])
            
            if fact_idx not in fact_scores or score > fact_scores[fact_idx]['score']:
                fact_scores[fact_idx] = {
                    'fact': self.facts[fact_idx],
                    'score': score,
                    'source': 'semantic'
                }
        
        results = sorted(fact_scores.values(), key=lambda x: x['score'], reverse=True)[:top_k]
        return results
    
    def expand_with_parents(self, go_ids: Set[str], max_hops: int = 1) -> Set[str]:
        """
        Expand GO IDs with parent terms (hierarchical up)
        
        Args:
            go_ids: Set of GO IDs
            max_hops: Maximum hops to traverse (1 = direct parents only)
        
        Returns:
            Expanded set of GO IDs
        """
        expanded = set(go_ids)
        current_level = set(go_ids)
        
        for hop in range(max_hops):
            next_level = set()
            for go_id in current_level:
                parents = self.child_to_parents.get(go_id, [])
                next_level.update(parents)
            
            if not next_level:
                break
            
            expanded.update(next_level)
            current_level = next_level
        
        return expanded
    
    def expand_with_children(self, go_ids: Set[str], max_hops: int = 1) -> Set[str]:
        """
        Expand GO IDs with child terms (hierarchical down)
        """
        expanded = set(go_ids)
        current_level = set(go_ids)
        
        for hop in range(max_hops):
            next_level = set()
            for go_id in current_level:
                children = self.parent_to_children.get(go_id, [])
                next_level.update(children)
            
            if not next_level:
                break
            
            expanded.update(next_level)
            current_level = next_level
        
        return expanded
    
    def expand_with_relationships(self, go_ids: Set[str], rel_types: List[str] = None) -> Set[str]:
        """
        Expand GO IDs with related terms (part_of, regulates, etc.)
        
        Args:
            go_ids: Set of GO IDs
            rel_types: List of relationship types to follow
                      Default: ['part_of', 'regulates']
        """
        if rel_types is None:
            rel_types = ['part_of', 'regulates']
        
        expanded = set(go_ids)
        
        for go_id in go_ids:
            rels = self.relationship_graph.get(go_id, {})
            for rel_type in rel_types:
                targets = rels.get(rel_type, [])
                expanded.update(targets)
        
        return expanded
    
    def retrieve_with_graph_expansion(
        self, 
        query: str, 
        top_k: int = 5,
        expand_parents: int = 1,
        expand_children: int = 0,
        expand_relationships: bool = False,
        boost_factor: float = 0.8
    ) -> List[Dict]:
        """
        Graph-aware retrieval with hierarchical expansion
        
        Args:
            query: Search query
            top_k: Final number of results
            expand_parents: Number of parent hops (0 = disabled)
            expand_children: Number of child hops (0 = disabled)
            expand_relationships: Whether to expand related terms
            boost_factor: Score multiplier for expanded terms (< 1.0)
        
        Returns:
            List of facts with scores
        """
        # Step 1: Initial semantic retrieval (get 2x candidates)
        initial_results = self.retrieve_semantic(query, top_k=top_k*2)
        
        # Step 2: Extract GO IDs from initial results
        initial_go_ids = set()
        initial_scores = {}
        for result in initial_results:
            go_id = result['fact'].get('GO id')
            if go_id:
                initial_go_ids.add(go_id)
                initial_scores[go_id] = result['score']
        
        # Step 3: Graph expansion
        expanded_go_ids = set(initial_go_ids)
        
        # Expand with parents (hierarchical up)
        if expand_parents > 0:
            parent_ids = self.expand_with_parents(initial_go_ids, max_hops=expand_parents)
            expanded_go_ids.update(parent_ids)
        
        # Expand with children (hierarchical down)
        if expand_children > 0:
            child_ids = self.expand_with_children(initial_go_ids, max_hops=expand_children)
            expanded_go_ids.update(child_ids)
        
        # Expand with relationships
        if expand_relationships:
            related_ids = self.expand_with_relationships(initial_go_ids)
            expanded_go_ids.update(related_ids)
        
        # Step 4: Score expanded terms
        all_results = {}
        for go_id in expanded_go_ids:
            fact_idx = self.go_id_to_fact_idx.get(go_id)
            if fact_idx is None:
                continue
            
            # Base score
            if go_id in initial_scores:
                score = initial_scores[go_id]
                source = 'semantic'
            else:
                # Boosted score from parent/child/relation
                # Find highest scoring neighbor
                max_neighbor_score = 0.0
                for neighbor_id in initial_go_ids:
                    if neighbor_id in initial_scores:
                        max_neighbor_score = max(max_neighbor_score, initial_scores[neighbor_id])
                
                score = max_neighbor_score * boost_factor
                source = 'graph_expansion'
            
            all_results[go_id] = {
                'fact': self.facts[fact_idx],
                'score': score,
                'source': source
            }
        
        # Step 5: Sort and return top-k
        sorted_results = sorted(all_results.values(), key=lambda x: x['score'], reverse=True)
        return sorted_results[:top_k]
    
    def get_fact_by_id(self, go_id: str) -> Dict[str, Any]:
        """Get fact by GO ID"""
        fact_idx = self.go_id_to_fact_idx.get(go_id)
        if fact_idx is not None:
            return self.facts[fact_idx]
        return None
    
    def get_parents(self, go_id: str) -> List[str]:
        """Get parent GO IDs"""
        return self.child_to_parents.get(go_id, [])
    
    def get_children(self, go_id: str) -> List[str]:
        """Get children GO IDs"""
        return self.parent_to_children.get(go_id, [])
    
    def get_related(self, go_id: str, rel_type: str = None) -> Dict[str, List[str]]:
        """
        Get related GO IDs
        
        Args:
            go_id: GO term ID
            rel_type: Specific relationship type (None = all)
        
        Returns:
            Dict of {relationship_type: [GO IDs]}
        """
        rels = self.relationship_graph.get(go_id, {})
        if rel_type:
            return {rel_type: rels.get(rel_type, [])}
        return rels
