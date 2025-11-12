"""
SPARQL-VI Query Engine with OG-RAG
Complete implementation following OG-RAG pattern from test_hypergraph_original.ipynb
"""

import json
import sys
import numpy as np
import importlib.util
from typing import Dict, List, Optional
from pathlib import Path

# Load modules directly to bypass __init__.py
current_dir = Path(__file__).parent
root_dir = current_dir.parent

# Load hypergraph module
spec = importlib.util.spec_from_file_location(
    "sparql_vi_hypergraph",
    current_dir / "sparql_vi_hypergraph.py"
)
hypergraph_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hypergraph_module)
OntoHyperGraph = hypergraph_module.OntoHyperGraph

# Load translator module
spec = importlib.util.spec_from_file_location(
    "sparql_vi_translator",
    root_dir / "dsl" / "sparql_vi_translator.py"
)
translator_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(translator_module)
SPARQLVITranslator = translator_module.SPARQLVITranslator

from langchain_community.embeddings import HuggingFaceEmbeddings


# Prompt template for OG-RAG (based on notebook)
OGRAG_PROMPT_TEMPLATE = """You are a SPARQL-VI query generator for a custom DSL.

ONTOLOGY + DSL:
{context}

RULES (STRICT):
1. Use ONLY DSL keywords/functions/classes listed under "DSL SYNTAX RULES".
2. Use ONLY Class/Property names that appear after "Class:" or "Property:".
3. Do NOT invent new functions/keywords/modifiers 
5. Use label_vi/label_en only for meaning; in the query, always use the actual identifiers 
6. If the question CANNOT be expressed exactly with the given DSL and ontology, output EXACTLY:
   CANNOT_ANSWER
   (no other text).
7. Output ONLY the SPARQL-VI query (or CANNOT_ANSWER). No explanations or comments.

Question:
{question}

SPARQL-VI Query:"""



BASELINE_PROMPT_TEMPLATE = """Generate a SPARQL-VI query for this Vietnamese question.

SPARQL-VI is a Vietnamese variant of SPARQL with keywords like:
- CHONJ_KW (SELECT)
- NOII_MA_KK (WHERE)
- LOCJ_RR (FILTER)
- TIỀN_TỐ (PREFIX)

Question: {question}

SPARQL-VI Query:"""


FEWSHOT_PROMPT_TEMPLATE = """Generate a SPARQL-VI query based on these examples:

{examples}

Now generate a SPARQL-VI query for this question:
Question: {question}

SPARQL-VI Query:"""


class SPARQLVIQueryEngine:
    """
    Query Engine for SPARQL-VI generation using OG-RAG
    """
    
    def __init__(
        self,
        dsl_facts_path: str,
        domain_facts_path: str,
        test_cases_path: str,
        embed_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        llm_api_key: Optional[str] = None,
        llm_model: str = "llama-3.3-70b-versatile",
        llm_base_url: str = "https://api.groq.com/openai/v1"
    ):
        """
        Initialize SPARQL-VI Query Engine with TWO-ONTOLOGY OG-RAG
        
        Args:
            dsl_facts_path: Path to dsl_facts.json (syntax rules)
            domain_facts_path: Path to domain_facts.json (schema)
            test_cases_path: Path to test_cases.json
            embed_model_name: HuggingFace model for embeddings
            llm_api_key: API key for LLM (Groq)
            llm_model: LLM model name
            llm_base_url: Base URL for LLM API
        """
        self.dsl_facts_path = dsl_facts_path
        self.domain_facts_path = domain_facts_path
        self.test_cases_path = test_cases_path
        self.translator = SPARQLVITranslator()
        
        print("="*70)
        print("Initializing SPARQL-VI OG-RAG Query Engine")
        print("TWO-ONTOLOGY ARCHITECTURE")
        print("="*70)
        
        # Initialize embedding model
        print("\n📦 Loading embedding model...")
        self.embed_model = HuggingFaceEmbeddings(model_name=embed_model_name)
        print(f"   ✓ {embed_model_name}")
        
        # Initialize LLM (use langchain_groq to avoid pydantic v2 issues)
        if llm_api_key:
            print("\n🤖 Loading LLM...")
            try:
                from langchain_groq import ChatGroq
                self.llm = ChatGroq(
                    model=llm_model,
                    api_key=llm_api_key,
                    temperature=0.0,
                    max_tokens=2048
                )
                print(f"   ✓ {llm_model} (via Groq)")
            except ImportError:
                print("   ⚠️  langchain_groq not installed, trying langchain_openai...")
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(
                    model=llm_model,
                    api_key=llm_api_key,
                    base_url=llm_base_url,
                    temperature=0.0,
                    max_tokens=2048
                )
                print(f"   ✓ {llm_model}")
        else:
            print("\n⚠️  No LLM API key provided - generation will not work")
            self.llm = None
        
        # Load resources for BOTH ontologies
        self._load_facts()
        self._load_test_cases()
        self._precompute_embeddings()
        self._build_dual_hypergraphs()
        
        print("\n" + "="*70)
        print("✓ Engine ready with DUAL hypergraphs!")
        print("="*70)
    
    def _load_facts(self):
        """Load facts from BOTH ontologies separately"""
        print("\n📚 Loading facts from both ontologies...")
        
        # Load DSL facts (syntax rules)
        with open(self.dsl_facts_path, 'r', encoding='utf-8') as f:
            dsl_data = json.load(f)
        self.dsl_facts = dsl_data['facts']
        
        # Load Domain facts (schema)
        with open(self.domain_facts_path, 'r', encoding='utf-8') as f:
            domain_data = json.load(f)
        self.domain_facts = domain_data['facts']
        
        print(f"   ✓ DSL facts (syntax): {len(self.dsl_facts)}")
        print(f"   ✓ Domain facts (schema): {len(self.domain_facts)}")
    
    def _load_test_cases(self):
        """Load test cases"""
        print("\n📝 Loading test cases...")
        with open(self.test_cases_path, 'r', encoding='utf-8') as f:
            self.test_cases = json.load(f)
        print(f"   ✓ {len(self.test_cases)} test cases loaded")
    
    def _precompute_embeddings(self):
        """Compute embeddings for BOTH ontologies separately"""
        import numpy as np
        
        print("\n🔢 Computing embeddings for both ontologies...")
        
        # Collect unique texts from DSL facts
        dsl_texts = set()
        for fact in self.dsl_facts:
            for key, value in fact.items():
                dsl_texts.add(key)
                dsl_texts.add(str(value))
        
        # Collect unique texts from Domain facts
        domain_texts = set()
        for fact in self.domain_facts:
            for key, value in fact.items():
                domain_texts.add(key)
                domain_texts.add(str(value))
        
        # Combine all unique texts
        all_texts = list(dsl_texts | domain_texts)
        print(f"   Found {len(all_texts)} unique texts ({len(dsl_texts)} DSL + {len(domain_texts)} Domain)")
        
        # Compute embeddings
        print(f"   Embedding...")
        embeddings = self.embed_model.embed_documents(all_texts)
        
        self.embeddings_dict = {
            text: np.array(emb) 
            for text, emb in zip(all_texts, embeddings)
        }
        
        print(f"   ✓ Computed {len(self.embeddings_dict)} embeddings")
        print(f"      Dimension: {len(embeddings[0])}")
    
    def _build_dual_hypergraphs(self):
        """Build TWO separate hypergraphs: DSL + Domain"""
        print("\n🕸️  Building DUAL hypergraphs...")
        
        # Build DSL hypergraph (syntax rules)
        print("\n   1️⃣  DSL Hypergraph (Syntax Rules)...")
        self.dsl_hypergraph = OntoHyperGraph.from_fact_lists(
            facts=self.dsl_facts,
            embed_model=self.embed_model,
            embeddings=self.embeddings_dict
        )
        print(f"      ✓ DSL: {len(self.dsl_hypergraph.nodes)} nodes, {len(self.dsl_hypergraph.edges)} edges")
        
        # Build Domain hypergraph (schema)
        print("\n   2️⃣  Domain Hypergraph (Schema)...")
        self.domain_hypergraph = OntoHyperGraph.from_fact_lists(
            facts=self.domain_facts,
            embed_model=self.embed_model,
            embeddings=self.embeddings_dict
        )
        print(f"      ✓ Domain: {len(self.domain_hypergraph.nodes)} nodes, {len(self.domain_hypergraph.edges)} edges")
    
    def retrieve_context(
        self,
        question: str,
        dsl_top_k: int = 5,
        domain_top_k: int = 10,
        nodes_top_k: int = 20
    ) -> str:
        """
        Retrieve relevant context from BOTH hypergraphs
        Returns combined context with DSL syntax rules + Domain schema
        """
        query_embedding = self.embed_model.embed_query(question)
        
        # Retrieve from DSL hypergraph
        dsl_context = self.dsl_hypergraph.retrieve_context(
            query_embedding,
            nodes_top_k=nodes_top_k,
            top_k=dsl_top_k
        )
        
        # Retrieve from Domain hypergraph
        domain_context = self.domain_hypergraph.retrieve_context(
            query_embedding,
            nodes_top_k=nodes_top_k,
            top_k=domain_top_k
        )
        
        # Combine: DSL first (syntax is more critical)
        combined = []
        
        if dsl_context:
            combined.append("=== DSL SYNTAX RULES (SPARQL-VI Keywords) ===\n" + dsl_context)
        
        if domain_context:
            combined.append("=== DOMAIN SCHEMA (Classes & Properties) ===\n" + domain_context)
        
        return "\n\n".join(combined)
    
    def generate_baseline(self, question: str) -> str:
        """Baseline: LLM without any context"""
        if not self.llm:
            return "# LLM not available"
        
        prompt = BASELINE_PROMPT_TEMPLATE.format(question=question)
        response = self.llm.invoke(prompt)
        return response.content.strip()
    
    def generate_fewshot(self, question: str, num_examples: int = 5) -> str:
        """Few-shot: LLM with examples but no ontology"""
        if not self.llm:
            return "# LLM not available"
        
        # Use first N test cases as examples
        examples_text = []
        for tc in self.test_cases[:num_examples]:
            ex = f"Question: {tc['nl_query']}\nSPARQL-VI:\n{tc['expected_vi']}"
            examples_text.append(ex)
        
        examples_str = "\n\n".join(examples_text)
        prompt = FEWSHOT_PROMPT_TEMPLATE.format(
            examples=examples_str,
            question=question
        )
        
        response = self.llm.invoke(prompt)
        return response.content.strip()
    
    def generate_ograg(
        self,
        question: str,
        dsl_top_k: int = 5,
        domain_top_k: int = 10,
        nodes_top_k: int = 20
    ) -> str:
        """OG-RAG: LLM with DUAL hypergraph-retrieved context"""
        if not self.llm:
            return "# LLM not available"
        
        # Retrieve context from BOTH ontologies
        context = self.retrieve_context(
            question,
            dsl_top_k=dsl_top_k,
            domain_top_k=domain_top_k,
            nodes_top_k=nodes_top_k
        )
        
        # Generate with dual context
        prompt = OGRAG_PROMPT_TEMPLATE.format(
            context=context,
            question=question
        )
        
        response = self.llm.invoke(prompt)
        return response.content.strip()
    
    def validate_query(
        self,
        vi_query: str,
        expected_sparql: Optional[str] = None
    ) -> Dict:
        """Validate generated SPARQL-VI query"""
        validation = {
            'syntax_valid': False,
            'translates': False,
            'exact_match': False,
            'errors': []
        }
        
        # Syntax validation
        is_valid, result = self.translator.validate_vi_query(vi_query)
        validation['syntax_valid'] = is_valid
        
        if not is_valid:
            validation['errors'].append(f"Syntax: {result}")
            return validation
        
        # Translation test
        try:
            sparql = self.translator.vi_to_sparql(vi_query)
            validation['translates'] = True
            validation['generated_sparql'] = sparql
        except Exception as e:
            validation['errors'].append(f"Translation: {str(e)}")
            return validation
        
        # Exact match test
        if expected_sparql:
            norm_gen = sparql.upper().replace(' ', '').replace('\n', '')
            norm_exp = expected_sparql.upper().replace(' ', '').replace('\n', '')
            validation['exact_match'] = norm_gen == norm_exp
        
        return validation
    
    def evaluate_test_case(
        self,
        test_case: Dict,
        method: str = 'ograg',
        dsl_top_k: int = 5,
        domain_top_k: int = 10,
        nodes_top_k: int = 20
    ) -> Dict:
        """Evaluate a single test case"""
        question = test_case['nl_query']
        
        # Generate query
        if method == 'baseline':
            generated = self.generate_baseline(question)
        elif method == 'fewshot':
            generated = self.generate_fewshot(question)
        elif method == 'ograg':
            generated = self.generate_ograg(
                question,
                dsl_top_k=dsl_top_k,
                domain_top_k=domain_top_k,
                nodes_top_k=nodes_top_k
            )
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Validate
        validation = self.validate_query(
            generated,
            test_case.get('expected_sparql')
        )
        
        return {
            'test_case_id': test_case['id'],
            'method': method,
            'question': question,
            'generated_vi': generated,
            'expected_vi': test_case['expected_vi'],
            'expected_sparql': test_case.get('expected_sparql'),
            **validation
        }
    
    def evaluate_all(
        self,
        method: str = 'ograg',
        limit: Optional[int] = None,
        dsl_top_k: int = 5,
        domain_top_k: int = 10,
        nodes_top_k: int = 20
    ) -> Dict:
        """Evaluate all test cases"""
        test_cases = self.test_cases[:limit] if limit else self.test_cases
        
        print(f"\n{'='*70}")
        print(f"Evaluating {len(test_cases)} test cases - Method: {method.upper()}")
        print(f"{'='*70}\n")
        
        results = []
        for tc in test_cases:
            print(f"[{tc['id']}] {tc['nl_query'][:50]}...")
            
            evaluation = self.evaluate_test_case(
                tc, 
                method=method,
                dsl_top_k=dsl_top_k,
                domain_top_k=domain_top_k,
                nodes_top_k=nodes_top_k
            )
            results.append(evaluation)
            
            # Show result
            if evaluation['syntax_valid']:
                print(f"   ✓ Syntax valid")
            else:
                print(f"   ✗ Syntax error: {evaluation['errors']}")
            
            if evaluation.get('exact_match'):
                print(f"   ✓ Exact match!")
            print()
        
        # Calculate metrics
        total = len(results)
        syntax_correct = sum(1 for r in results if r['syntax_valid'])
        exact_matches = sum(1 for r in results if r.get('exact_match', False))
        
        print(f"{'='*70}")
        print("Results Summary")
        print(f"{'='*70}")
        print(f"Method: {method.upper()}")
        print(f"Total: {total}")
        print(f"Syntax Accuracy: {syntax_correct}/{total} ({100*syntax_correct/total:.1f}%)")
        print(f"Exact Match: {exact_matches}/{total} ({100*exact_matches/total:.1f}%)")
        
        return {
            'method': method,
            'total_cases': total,
            'syntax_accuracy': syntax_correct / total if total > 0 else 0,
            'exact_match_accuracy': exact_matches / total if total > 0 else 0,
            'results': results
        }


if __name__ == "__main__":
    import os
    
    print("""
╔══════════════════════════════════════════════════════════════════╗
║          SPARQL-VI Query Engine with TWO-ONTOLOGY OG-RAG         ║
╚══════════════════════════════════════════════════════════════════╝

To use this engine with LLM generation, set GROQ_API_KEY:
  export GROQ_API_KEY=gsk_...

Without API key, only retrieval will work.
""")
    
    # Initialize engine with DUAL ontologies
    api_key = os.environ.get('GROQ_API_KEY')
    
    engine = SPARQLVIQueryEngine(
        dsl_facts_path="data/dsl/sparql_vi/dsl_facts.json",
        domain_facts_path="data/dsl/sparql_vi/domain_facts.json",
        test_cases_path="data/dsl/sparql_vi/test_cases.json",
        llm_api_key=api_key
    )
    
    # Test retrieval
    print("\n" + "="*70)
    print("Testing Context Retrieval")
    print("="*70)
    
    test_query = "Tìm tất cả người có tuổi lớn hơn 18"
    print(f"\nQuery: {test_query}")
    
    context = engine.retrieve_context(test_query, nodes_top_k=10, edges_top_k=5)
    print(f"\nRetrieved Context:\n{context}")
    
    # Test generation if LLM available
    if api_key:
        print("\n" + "="*70)
        print("Testing OG-RAG Generation")
        print("="*70)
        
        generated = engine.generate_ograg(test_query)
        print(f"\nGenerated SPARQL-VI:\n{generated}")
        
        # Validate
        validation = engine.validate_query(generated)
        print(f"\nValidation:")
        print(f"  Syntax valid: {validation['syntax_valid']}")
        print(f"  Translates: {validation['translates']}")
        if validation['errors']:
            print(f"  Errors: {validation['errors']}")
    else:
        print("\n⚠️  Set GROQ_API_KEY to test generation")
