"""
GO Query Engine - Complete OG-RAG Implementation for Gene Ontology

Following OG-RAG paper (arxiv.org/html/2412.15235v1):
- Algorithm 1: Hypergraph Construction ✅ (done in build_go_hypergraph.py)
- Algorithm 2: Dual Ranking Retrieval ✅ (implemented here)
- Algorithm 3: LLM Generation ✅ (implemented here)
"""

import os
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from sentence_transformers import SentenceTransformer
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import yaml


class GOQueryEngine:
    """
    Query Engine for Gene Ontology using OG-RAG methodology
    """
    
    def __init__(
        self,
        ontology_dir: str = "data/kg/go/ontology",
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        llm_model: str = "gpt-4",
        top_k: int = 5,
        hierarchical_depth: int = 2,
        api_key: Optional[str] = None
    ):
        """
        Initialize GO Query Engine
        
        Args:
            ontology_dir: Directory containing hypergraph files
            model_name: Embedding model name (must match build)
            llm_model: LLM model for generation
            top_k: Number of facts to retrieve
            hierarchical_depth: Depth for hierarchical expansion
            api_key: OpenAI API key (reads from api_keys.yaml if None)
        """
        self.ontology_dir = Path(ontology_dir)
        self.model_name = model_name
        self.top_k = top_k
        self.hierarchical_depth = hierarchical_depth
        
        print(f"Initializing GO Query Engine...")
        
        # Load hypergraph
        self._load_hypergraph()
        
        # Load embedding model
        print(f"Loading embedding model: {model_name}...")
        self.embed_model = SentenceTransformer(model_name)
        
        # Load LLM
        if api_key is None:
            api_key = self._load_api_key()
        
        print(f"Loading LLM: {llm_model}...")
        self.llm = ChatOpenAI(
            model=llm_model,
            temperature=0,
            api_key=api_key
        )
        
        # Create prompt template
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are a biology expert with deep knowledge of Gene Ontology. "
                      "Answer questions accurately using the provided GO terms and their relationships."),
            ("user", """Question: {question}

Retrieved GO Terms:
{context}

Instructions:
1. Use the GO terms, definitions, and relationships provided above
2. Explain biological processes clearly
3. If multiple related terms are provided, explain how they connect
4. Be concise but comprehensive

Answer:""")
        ])
        
        print(f"✓ GO Query Engine initialized")
        print(f"  - {len(self.facts):,} GO terms")
        print(f"  - {len(self.hypernodes):,} hypernodes")
        print(f"  - Top-k: {self.top_k}")
        print(f"  - Hierarchical depth: {self.hierarchical_depth}\n")
    
    def _load_api_key(self) -> str:
        """Load OpenAI API key from api_keys.yaml"""
        api_keys_file = Path("api_keys.yaml")
        if not api_keys_file.exists():
            raise ValueError("api_keys.yaml not found. Please create it with your OpenAI API key.")
        
        with open(api_keys_file, 'r') as f:
            api_keys = yaml.safe_load(f)
        
        if 'openai_api_key' not in api_keys:
            raise ValueError("openai_api_key not found in api_keys.yaml")
        
        return api_keys['openai_api_key']
    
    def _load_hypergraph(self):
        """Load hypergraph components from disk"""
        print(f"Loading hypergraph from {self.ontology_dir}...")
        
        # Load facts (HyperEdges)
        with open(self.ontology_dir / "go_hypergraph_facts.pkl", 'rb') as f:
            self.facts = pickle.load(f)
        
        # Load hypernodes
        with open(self.ontology_dir / "go_hypergraph_nodes.pkl", 'rb') as f:
            self.hypernodes = pickle.load(f)
        
        # Load embeddings
        self.key_embeddings = np.load(self.ontology_dir / "go_hypernode_key_embeddings.npy")
        self.value_embeddings = np.load(self.ontology_dir / "go_hypernode_value_embeddings.npy")
        
        # Build GO ID index for hierarchical queries
        self._build_go_index()
    
    def _build_go_index(self):
        """Build index: GO_ID → fact_idx for fast lookup"""
        self.go_id_to_fact = {}
        
        for fact_idx, fact in enumerate(self.facts):
            go_id = fact.get('GO id')
            if go_id:
                self.go_id_to_fact[go_id] = fact_idx
    
    def retrieve_facts(
        self, 
        query: str, 
        top_k: Optional[int] = None,
        include_hierarchical: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Retrieve top-k facts using dual ranking (Algorithm 2 from paper)
        
        Args:
            query: Query string
            top_k: Number of facts to retrieve (uses self.top_k if None)
            include_hierarchical: Whether to expand with parent/child terms
        
        Returns:
            List of retrieved facts with scores
        """
        if top_k is None:
            top_k = self.top_k
        
        # Encode query
        query_emb = self.embed_model.encode([query], normalize_embeddings=True)[0]
        
        # Compute similarities (dual ranking)
        key_scores = np.dot(self.key_embeddings, query_emb)
        value_scores = np.dot(self.value_embeddings, query_emb)
        
        # Combine scores: max of key and value (following paper)
        combined_scores = np.maximum(key_scores, value_scores)
        
        # Get top-k hypernodes
        top_k_nodes = min(top_k * 3, len(combined_scores))  # Retrieve more for diversity
        top_indices = np.argsort(combined_scores)[-top_k_nodes:][::-1]
        
        # Map hypernodes to facts
        fact_scores = {}
        
        for idx in top_indices:
            hypernode = self.hypernodes[idx]
            fact_idx = hypernode['fact_idx']
            score = float(combined_scores[idx])
            
            # Keep best score per fact
            if fact_idx not in fact_scores or score > fact_scores[fact_idx]['score']:
                fact_scores[fact_idx] = {
                    'fact_idx': fact_idx,
                    'score': score,
                    'matched_key': hypernode['key'],
                    'matched_value': hypernode['value']
                }
        
        # Sort by score and get top-k facts
        ranked_facts = sorted(fact_scores.values(), key=lambda x: x['score'], reverse=True)[:top_k]
        
        # Add full fact data
        results = []
        for item in ranked_facts:
            fact_idx = item['fact_idx']
            result = {
                'fact': self.facts[fact_idx],
                'score': item['score'],
                'matched_key': item['matched_key'],
                'matched_value': item['matched_value']
            }
            results.append(result)
        
        # Hierarchical expansion
        if include_hierarchical and self.hierarchical_depth > 0:
            results = self._expand_hierarchical(results)
        
        return results
    
    def _expand_hierarchical(self, results: List[Dict]) -> List[Dict]:
        """
        Expand results with parent/child GO terms following is_a relationships
        
        Example: "DNA repair" → Also get parent terms (DNA metabolic process)
        """
        expanded = []
        seen_go_ids = set()
        
        for result in results:
            fact = result['fact']
            go_id = fact.get('GO id')
            
            if go_id and go_id not in seen_go_ids:
                expanded.append(result)
                seen_go_ids.add(go_id)
                
                # Get parent terms (is_a relationships)
                for depth in range(1, self.hierarchical_depth + 1):
                    parent_key = f'GO is_a_{depth}'
                    if parent_key in fact:
                        parent_ref = fact[parent_key]
                        # Extract GO:XXXXXXX from "GO:XXXXXXX (term name)"
                        parent_id = parent_ref.split()[0] if ' ' in parent_ref else parent_ref
                        
                        if parent_id in self.go_id_to_fact and parent_id not in seen_go_ids:
                            parent_fact_idx = self.go_id_to_fact[parent_id]
                            expanded.append({
                                'fact': self.facts[parent_fact_idx],
                                'score': result['score'] * 0.8,  # Slightly lower score
                                'matched_key': f'Hierarchical parent (is_a)',
                                'matched_value': parent_ref
                            })
                            seen_go_ids.add(parent_id)
        
        return expanded
    
    def format_context(self, retrieved_facts: List[Dict]) -> str:
        """
        Format retrieved facts into context string for LLM
        
        Args:
            retrieved_facts: List of retrieved facts with scores
        
        Returns:
            Formatted context string
        """
        context_parts = []
        
        for i, result in enumerate(retrieved_facts, 1):
            fact = result['fact']
            score = result['score']
            
            # Format each GO term
            go_term = f"\n{'='*60}\n"
            go_term += f"GO Term {i} (Relevance: {score:.3f})\n"
            go_term += f"{'='*60}\n"
            
            # Basic info
            go_term += f"ID: {fact.get('GO id', 'N/A')}\n"
            go_term += f"Name: {fact.get('GO label', 'N/A')}\n"
            go_term += f"Namespace: {fact.get('GO namespace', 'N/A')}\n"
            
            # Definition
            if 'GO definition' in fact:
                go_term += f"\nDefinition:\n{fact['GO definition']}\n"
            
            # Synonyms
            if 'GO synonyms' in fact:
                go_term += f"\nSynonyms: {fact['GO synonyms']}\n"
            
            # Relationships
            relationships = []
            for key, value in fact.items():
                if any(rel in key for rel in ['is_a', 'part_of', 'regulates', 'occurs_in']):
                    relationships.append(f"  - {key.replace('GO ', '')}: {value}")
            
            if relationships:
                go_term += f"\nRelationships:\n" + "\n".join(relationships) + "\n"
            
            context_parts.append(go_term)
        
        return "\n".join(context_parts)
    
    def query(
        self, 
        question: str, 
        return_context: bool = False,
        verbose: bool = False
    ) -> Union[str, Dict[str, Any]]:
        """
        Complete query pipeline: Retrieve + Generate (Full OG-RAG)
        
        Args:
            question: User question
            return_context: If True, return dict with answer and context
            verbose: If True, print retrieval details
        
        Returns:
            Answer string, or dict with answer and context if return_context=True
        """
        if verbose:
            print(f"\n{'='*80}")
            print(f"Question: {question}")
            print(f"{'='*80}\n")
        
        # Step 1: Retrieve facts (Algorithm 2)
        retrieved_facts = self.retrieve_facts(question)
        
        if verbose:
            print(f"Retrieved {len(retrieved_facts)} relevant GO terms:")
            for i, result in enumerate(retrieved_facts[:3], 1):
                fact = result['fact']
                print(f"{i}. {fact.get('GO label', 'N/A')} ({fact.get('GO id', 'N/A')}) - Score: {result['score']:.3f}")
            print()
        
        # Step 2: Format context
        context = self.format_context(retrieved_facts)
        
        # Step 3: Generate answer with LLM (Algorithm 3)
        prompt = self.prompt_template.invoke({
            "question": question,
            "context": context
        })
        
        response = self.llm.invoke(prompt)
        answer = response.content
        
        if return_context:
            return {
                'answer': answer,
                'context': context,
                'retrieved_facts': retrieved_facts,
                'question': question
            }
        
        return answer


def main():
    """Test GO Query Engine"""
    
    # Initialize
    engine = GOQueryEngine(
        ontology_dir="data/kg/go/ontology",
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        llm_model="gpt-4",
        top_k=5,
        hierarchical_depth=2
    )
    
    # Test queries
    test_questions = [
        "What is DNA repair?",
        "How does cell division work in eukaryotes?",
        "What is the role of mitochondria in cellular respiration?",
        "Explain protein phosphorylation.",
        "What are the main processes involved in immune response?"
    ]
    
    for question in test_questions:
        print(f"\n{'='*80}")
        print(f"Q: {question}")
        print(f"{'='*80}")
        
        result = engine.query(question, return_context=False, verbose=True)
        
        print(f"\nAnswer:\n{result}\n")
        print("="*80)
        
        input("\nPress Enter for next question...")


if __name__ == "__main__":
    main()
