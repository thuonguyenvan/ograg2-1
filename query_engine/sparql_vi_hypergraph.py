"""
SPARQL-VI Hypergraph Classes
Simplified version without llama_index dependencies
Based on OntoHyperGraph from test_hypergraph_original.ipynb
"""

import numpy as np
from typing import List, Dict, Set, Optional
from collections import defaultdict


class HyperNode:
    """
    Node in hypergraph representing a key-value pair
    Has separate embeddings for key and value
    """
    
    def __init__(
        self,
        key: str,
        value: str,
        key_embedding: np.ndarray,
        value_embedding: np.ndarray,
        edge_ids: Optional[Set[int]] = None
    ):
        self.key = key
        self.value = value
        self.key_embedding = np.array(key_embedding)
        self.value_embedding = np.array(value_embedding)
        self.edge_ids = edge_ids or set()
    
    def similarity(self, query_embedding: np.ndarray, method: str = 'sum') -> float:
        """
        Calculate similarity with query
        
        Methods:
        - 'sum': cos(query, key) + cos(query, value)
        - 'key_only': cos(query, key)
        - 'value_only': cos(query, value)
        - 'product': cos(query, key) * cos(query, value)
        """
        query_emb = np.array(query_embedding)
        
        def cosine_sim(vec1, vec2):
            dot = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            if norm1 == 0 or norm2 == 0:
                return 0.0
            return dot / (norm1 * norm2)
        
        key_sim = cosine_sim(query_emb, self.key_embedding)
        value_sim = cosine_sim(query_emb, self.value_embedding)
        
        if method == 'sum':
            return key_sim + value_sim
        elif method == 'key_only':
            return key_sim
        elif method == 'value_only':
            return value_sim
        elif method == 'product':
            return key_sim * value_sim
        else:
            return key_sim + value_sim
    
    def __repr__(self):
        return f"HyperNode(key='{self.key}', value='{self.value}', edges={len(self.edge_ids)})"


class HyperEdge:
    """
    Edge in hypergraph connecting multiple nodes
    Represents one complete fact (dictionary)
    """
    
    def __init__(self, nodes: List[HyperNode], edge_id: int):
        self.nodes = nodes
        self.edge_id = edge_id
    
    def to_dict(self) -> Dict[str, str]:
        """Convert edge back to dictionary"""
        return {node.key: node.value for node in self.nodes}
    
    def to_text(self) -> str:
        """Convert edge to readable text"""
        fact_dict = self.to_dict()
        text_parts = [f"{k}: {v}" for k, v in fact_dict.items()]
        return " | ".join(text_parts)
    
    def __repr__(self):
        return f"HyperEdge(id={self.edge_id}, nodes={len(self.nodes)})"


class OntoHyperGraph:
    """
    Hypergraph for ontology-guided RAG
    
    Architecture:
    - Each fact (dict) → HyperEdge
    - Each key-value pair → HyperNode
    - Nodes have separate key & value embeddings
    - Retrieval: dual ranking by key + value similarity
    """
    
    def __init__(self):
        self.nodes: List[HyperNode] = []
        self.edges: List[HyperEdge] = []
        self.node_map: Dict[tuple, int] = {}  # (key, value) -> node_index
    
    @classmethod
    def from_fact_lists(
        cls,
        facts: List[Dict[str, str]],
        embed_model,
        embeddings: Optional[Dict[str, np.ndarray]] = None
    ):
        """
        Build hypergraph from list of facts
        
        Args:
            facts: List of dictionaries (each dict = 1 fact = 1 edge)
            embed_model: Langchain embeddings model
            embeddings: Pre-computed embeddings dict (optional)
        
        Returns:
            OntoHyperGraph instance
        """
        graph = cls()
        
        # Step 1: Collect all unique key-value pairs
        unique_pairs = set()
        for fact in facts:
            for key, value in fact.items():
                unique_pairs.add((key, str(value)))
        
        print(f"  Building hypergraph from {len(facts)} facts...")
        print(f"  Found {len(unique_pairs)} unique key-value pairs")
        
        # Step 2: Compute embeddings if not provided
        if embeddings is None:
            print(f"  Computing embeddings...")
            all_texts = []
            for key, value in unique_pairs:
                all_texts.append(key)
                all_texts.append(value)
            
            all_embeddings = embed_model.embed_documents(all_texts)
            embeddings = {text: np.array(emb) for text, emb in zip(all_texts, all_embeddings)}
        
        # Step 3: Create HyperNodes for each unique pair
        node_index = 0
        for key, value in unique_pairs:
            key_emb = embeddings.get(key, embeddings.get(key, np.zeros(384)))
            value_emb = embeddings.get(value, embeddings.get(value, np.zeros(384)))
            
            node = HyperNode(
                key=key,
                value=value,
                key_embedding=key_emb,
                value_embedding=value_emb,
                edge_ids=set()
            )
            graph.nodes.append(node)
            graph.node_map[(key, value)] = node_index
            node_index += 1
        
        # Step 4: Create HyperEdges (one per fact)
        for edge_id, fact in enumerate(facts):
            edge_nodes = []
            for key, value in fact.items():
                node_idx = graph.node_map.get((key, str(value)))
                if node_idx is not None:
                    node = graph.nodes[node_idx]
                    node.edge_ids.add(edge_id)
                    edge_nodes.append(node)
            
            edge = HyperEdge(nodes=edge_nodes, edge_id=edge_id)
            graph.edges.append(edge)
        
        print(f"✓ Hypergraph built: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
        return graph
    
    def get_relevant_hypernodes(
        self,
        query_embedding: np.ndarray,
        top_k: int = 20,
        method: str = 'dual'
    ) -> List[HyperNode]:
        """
        Retrieve top-k relevant nodes
        
        Method 'dual': Retrieve by KEY and VALUE separately, then combine
        This is the OG-RAG approach from the notebook
        """
        if method == 'dual':
            # Dual ranking strategy
            k_per_method = top_k // 2
            
            # Top-k by KEY similarity only
            key_nodes = sorted(
                self.nodes,
                key=lambda n: n.similarity(query_embedding, method='key_only'),
                reverse=True
            )[:k_per_method]
            
            # Top-k by VALUE similarity only
            value_nodes = sorted(
                self.nodes,
                key=lambda n: n.similarity(query_embedding, method='value_only'),
                reverse=True
            )[:k_per_method]
            
            # Combine and deduplicate
            seen = set()
            relevant = []
            for node in key_nodes + value_nodes:
                node_id = (node.key, node.value)
                if node_id not in seen:
                    seen.add(node_id)
                    relevant.append(node)
            
            return relevant[:top_k]
        
        else:
            # Single ranking
            return sorted(
                self.nodes,
                key=lambda n: n.similarity(query_embedding, method='sum'),
                reverse=True
            )[:top_k]
    
    def get_relevant_hyperedges(
        self,
        relevant_nodes: List[HyperNode],
        top_k: int = 5
    ) -> List[HyperEdge]:
        """
        Get hyperedges that cover the most relevant nodes
        """
        # Count how many relevant nodes each edge contains
        edge_scores = defaultdict(int)
        for node in relevant_nodes:
            for edge_id in node.edge_ids:
                edge_scores[edge_id] += 1
        
        # Sort edges by coverage
        sorted_edges = sorted(
            edge_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]
        
        # Return actual edge objects
        return [self.edges[edge_id] for edge_id, _ in sorted_edges]
    
    def retrieve_context(
        self,
        query_embedding: np.ndarray,
        nodes_top_k: int = 20,
        top_k: int = 5,
        include_dsl_facts: int = 3
    ) -> str:
        """
        Retrieve relevant context for query embedding
        
        Args:
            query_embedding: Pre-computed query embedding
            nodes_top_k: Number of nodes to retrieve
            top_k: Total number of hyperedges to return
            include_dsl_facts: Minimum number of DSL facts to include
        
        Returns formatted text of relevant hyperedges
        """
        # Get relevant nodes and edges
        relevant_nodes = self.get_relevant_hypernodes(
            query_embedding,
            top_k=nodes_top_k,
            method='dual'
        )
        
        relevant_edges = self.get_relevant_hyperedges(
            relevant_nodes,
            top_k=top_k
        )
        
        # Format as readable text with full information
        context_parts = []
        for i, edge in enumerate(relevant_edges, 1):
            fact_dict = edge.to_dict()
            
            # Build a descriptive text based on fact type
            if 'domain_class' in fact_dict or 'domain_property' in fact_dict:
                # Domain ontology fact
                entity = fact_dict.get('domain_class') or fact_dict.get('domain_property')
                entity_type = 'Class' if 'domain_class' in fact_dict else 'Property'
                
                # Format: Show entity name clearly
                parts = [f"{entity_type}: :{entity}"]
                if 'label_vi' in fact_dict:
                    parts.append(f"  label_vi: \"{fact_dict['label_vi']}\"")
                if 'label_en' in fact_dict:
                    parts.append(f"  label_en: \"{fact_dict['label_en']}\"")
                if 'description' in fact_dict:
                    parts.append(f"  description: {fact_dict['description']}")
                
                # Add domain/range for properties (CRITICAL for understanding relationships)
                if entity_type == 'Property':
                    if 'domain' in fact_dict and fact_dict['domain'] not in ['domain', 'N/A']:
                        parts.append(f"  domain: {fact_dict['domain']} (subject/owner of this property)")
                    if 'range' in fact_dict and fact_dict['range'] not in ['range', 'N/A']:
                        parts.append(f"  range: {fact_dict['range']} (value type)")
                
                context_parts.append(f"{i}. {chr(10).join(parts)}")
                
            elif 'dsl_class' in fact_dict:
                # DSL class/clause fact
                dsl_class = fact_dict.get('dsl_class', 'N/A')
                parts = [f"DSL Class: {dsl_class}"]
                if 'label_vi' in fact_dict:
                    parts.append(f"  Vietnamese: {fact_dict['label_vi']}")
                if 'description' in fact_dict:
                    parts.append(f"  Description: {fact_dict['description']}")
                if 'syntax' in fact_dict:
                    parts.append(f"  Syntax: {fact_dict['syntax']}")
                if 'example' in fact_dict:
                    parts.append(f"  Example: {fact_dict['example']}")
                context_parts.append(f"{i}. {chr(10).join(parts)}")
            else:
                # Fallback: generic format
                fact_lines = [f"  {k}: {v}" for k, v in fact_dict.items()]
                context_parts.append(f"{i}.\n" + "\n".join(fact_lines))
        
        return "\n\n".join(context_parts)


def test_hypergraph():
    """Test hypergraph functionality"""
    from langchain_community.embeddings import HuggingFaceEmbeddings
    import json
    
    print("\n" + "="*60)
    print("Testing OntoHyperGraph (OG-RAG Pattern)")
    print("="*60)
    
    # Load facts
    with open("data/dsl/sparql_vi/hypergraph_facts.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    facts = data['facts']
    
    print(f"\nLoaded {len(facts)} facts")
    
    # Initialize embeddings
    print("\nInitializing embedding model...")
    embed_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    # Pre-compute embeddings (OG-RAG pattern)
    print("\n" + "="*60)
    print("Pre-computing embeddings for all keys & values")
    print("="*60)
    
    unique_texts = set()
    for fact in facts:
        for key, value in fact.items():
            unique_texts.add(key)
            unique_texts.add(str(value))
    
    unique_texts = list(unique_texts)
    print(f"  Found {len(unique_texts)} unique texts")
    
    print(f"  Embedding {len(unique_texts)} texts...")
    unique_embeddings = embed_model.embed_documents(unique_texts)
    
    embeddings_dict = {text: np.array(emb) for text, emb in zip(unique_texts, unique_embeddings)}
    
    print(f"✓ Cached {len(embeddings_dict)} embeddings")
    print(f"  Embedding dimension: {len(unique_embeddings[0])}")
    
    # Build hypergraph with pre-computed embeddings
    print("\n" + "="*60)
    print("Building hypergraph")
    print("="*60)
    
    hypergraph = OntoHyperGraph.from_fact_lists(
        facts=facts,
        embed_model=embed_model,
        embeddings=embeddings_dict  # Pass pre-computed embeddings
    )
    
    # Test retrieval
    print("\n" + "="*60)
    print("Testing retrieval")
    print("="*60)
    
    test_queries = [
        "Tìm người có tuổi lớn hơn 18",
        "CHONJ_KW SELECT query",
        "Đếm số lượng sản phẩm"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 60)
        
        # Embed query
        query_embedding = embed_model.embed_query(query)
        
        # Retrieve context
        context = hypergraph.retrieve_context(
            query_embedding,
            nodes_top_k=10,
            top_k=3
        )
        
        print(f"Retrieved Context:\n{context}\n")


if __name__ == "__main__":
    test_hypergraph()
