"""
Enhanced Domain-DSL Query Engine
Hierarchical OG-RAG with NL-Aware Retrieval for Complex Ontologies

Architecture:
1. Parse JSON-LD ontologies to structured hypergraph
2. Multi-level retrieval: NL patterns + Semantic + Graph walk
3. Hierarchical context assembly
4. LLM generation with rich context

This is a standalone module with no dependencies on other query engines.
"""

import json
import numpy as np
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from collections import defaultdict

# Standalone module - no imports from other query_engine modules


class DomainClassNode:
    """Node representing a domain class with its properties"""
    def __init__(
        self,
        identifier: str,
        label: str,
        description: str,
        subclass_of: Optional[str],
        example_individuals: List[str],
        related_properties: List[Dict]
    ):
        self.identifier = identifier
        self.label = label
        self.description = description
        self.subclass_of = subclass_of
        self.example_individuals = example_individuals
        self.related_properties = related_properties
        self.embedding = None
        
    def __repr__(self):
        return f"ClassNode({self.identifier}, props={len(self.related_properties)})"


class DSLNode:
    """Node representing a DSL entity (query type, function, clause, modifier)"""
    def __init__(
        self,
        identifier: str,
        node_type: str,  # DSLQueryType, DSLFunction, DSLClause, DSLModifier
        keyword: str,
        label: str,
        description: str,
        syntax: str,
        example_dsl: str,
        kind: Optional[str] = None  # aggregate, numeric, string, filter, modifier
    ):
        self.identifier = identifier
        self.node_type = node_type
        self.keyword = keyword
        self.label = label
        self.description = description
        self.syntax = syntax
        self.example_dsl = example_dsl
        self.kind = kind
        self.embedding = None
        
    def __repr__(self):
        return f"DSLNode({self.keyword}, type={self.node_type}, kind={self.kind})"


class OntologyParser:
    """Parse JSON-LD ontologies to structured nodes"""
    
    @staticmethod
    def parse_domain_ontology(jsonld_path: str) -> List[DomainClassNode]:
        """Parse domain ontology JSON-LD"""
        with open(jsonld_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        classes = []
        for item in data.get('@graph', []):
            if item.get('@type') == 'DomainClass':
                classes.append(DomainClassNode(
                    identifier=item.get('identifier'),
                    label=item.get('label'),
                    description=item.get('description', ''),
                    subclass_of=item.get('subclass_of'),
                    example_individuals=item.get('example_individuals', []),
                    related_properties=item.get('related_properties', [])
                ))
        
        print(f"  ✓ Parsed {len(classes)} domain classes")
        total_props = sum(len(c.related_properties) for c in classes)
        print(f"    with {total_props} total properties")
        return classes
    
    @staticmethod
    def parse_dsl_ontology(jsonld_path: str) -> List[DSLNode]:
        """Parse DSL ontology JSON-LD"""
        with open(jsonld_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        nodes = []
        for item in data.get('@graph', []):
            node_type = item.get('@type')
            if node_type in ['DSLQueryType', 'DSLFunction', 'DSLClause', 'DSLModifier']:
                nodes.append(DSLNode(
                    identifier=item.get('identifier'),
                    node_type=node_type,
                    keyword=item.get('keyword', ''),
                    label=item.get('label', ''),
                    description=item.get('description', ''),
                    syntax=item.get('syntax', ''),
                    example_dsl=item.get('example_dsl', ''),
                    kind=item.get('kind')
                ))
        
        # Group by type
        by_type = defaultdict(int)
        for node in nodes:
            by_type[node.node_type] += 1
        
        print(f"  ✓ Parsed {len(nodes)} DSL entities:")
        for node_type, count in by_type.items():
            print(f"    - {node_type}: {count}")
        
        return nodes


class HierarchicalHyperGraph:
    """Hypergraph that preserves class-property hierarchy"""
    
    def __init__(self, embed_model):
        self.embed_model = embed_model
        self.classes = {}  # identifier → DomainClassNode
        self.properties_by_class = defaultdict(list)  # class_id → [properties]
        self.embeddings_cache = {}
        
    def add_domain_classes(self, classes: List[DomainClassNode]):
        """Add domain classes with their properties"""
        print("\n🔨 Building domain hypergraph...")
        
        # Compute embeddings for all texts
        texts_to_embed = []
        text_map = []  # (type, id, subid) tuples
        
        for cls in classes:
            # Class embedding: label + description
            class_text = f"{cls.label}. {cls.description}"
            texts_to_embed.append(class_text)
            text_map.append(('class', cls.identifier, None))
            
            # Property embeddings: property label + description + parent class
            for prop in cls.related_properties:
                prop_text = f"{prop.get('label', '')} of {cls.label}. {prop.get('description', '')}"
                texts_to_embed.append(prop_text)
                text_map.append(('property', cls.identifier, prop.get('property')))
        
        print(f"  Computing embeddings for {len(texts_to_embed)} texts...")
        embeddings = self.embed_model.embed_documents(texts_to_embed)
        
        # Assign embeddings
        for (text_type, class_id, prop_id), embedding in zip(text_map, embeddings):
            if text_type == 'class':
                # Find class and assign embedding
                for cls in classes:
                    if cls.identifier == class_id:
                        cls.embedding = np.array(embedding)
                        self.classes[class_id] = cls
                        break
            else:  # property
                self.embeddings_cache[(class_id, prop_id)] = np.array(embedding)
                # Store property with parent class link
                for cls in classes:
                    if cls.identifier == class_id:
                        for prop in cls.related_properties:
                            if prop.get('property') == prop_id:
                                self.properties_by_class[class_id].append({
                                    **prop,
                                    'embedding': np.array(embedding)
                                })
                                break
                        break
        
        print(f"  ✓ Built graph with {len(self.classes)} classes")
        print(f"    Total properties: {sum(len(props) for props in self.properties_by_class.values())}")
    
    def retrieve_classes(self, query_embedding: np.ndarray, top_k: int = 3) -> List[Tuple[DomainClassNode, float]]:
        """Retrieve most relevant classes"""
        scores = []
        for cls in self.classes.values():
            if cls.embedding is not None:
                score = np.dot(query_embedding, cls.embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(cls.embedding)
                )
                scores.append((cls, score))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]
    
    def retrieve_properties_for_class(self, class_id: str, query_embedding: np.ndarray, top_k: int = 5):
        """Retrieve most relevant properties for a given class"""
        properties = self.properties_by_class.get(class_id, [])
        if not properties:
            return []
        
        scores = []
        for prop in properties:
            if 'embedding' in prop:
                score = np.dot(query_embedding, prop['embedding']) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(prop['embedding'])
                )
                scores.append((prop, score))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]


class DSLHyperGraph:
    """Hypergraph for DSL entities with kind-based retrieval"""
    
    def __init__(self, embed_model):
        self.embed_model = embed_model
        self.nodes_by_type = defaultdict(list)  # node_type → [DSLNode]
        self.nodes_by_kind = defaultdict(list)  # kind → [DSLNode]
        
    def add_dsl_nodes(self, nodes: List[DSLNode]):
        """Add DSL nodes and compute embeddings"""
        print("\n🔨 Building DSL hypergraph...")
        
        # Compute embeddings
        texts = [f"{node.keyword} {node.label}. {node.description}" for node in nodes]
        print(f"  Computing embeddings for {len(texts)} DSL entities...")
        embeddings = self.embed_model.embed_documents(texts)
        
        # Assign embeddings and organize
        for node, embedding in zip(nodes, embeddings):
            node.embedding = np.array(embedding)
            self.nodes_by_type[node.node_type].append(node)
            if node.kind:
                self.nodes_by_kind[node.kind].append(node)
        
        print(f"  ✓ Built graph with {len(nodes)} DSL entities")
        print(f"    Organized by {len(self.nodes_by_type)} types and {len(self.nodes_by_kind)} kinds")
    
    def retrieve_by_type(self, query_embedding: np.ndarray, node_type: str, top_k: int = 3):
        """Retrieve nodes of specific type"""
        nodes = self.nodes_by_type.get(node_type, [])
        return self._score_and_rank(nodes, query_embedding, top_k)
    
    def retrieve_by_kind(self, query_embedding: np.ndarray, kind: str, top_k: int = 3):
        """Retrieve nodes of specific kind"""
        nodes = self.nodes_by_kind.get(kind, [])
        return self._score_and_rank(nodes, query_embedding, top_k)
    
    def retrieve_all(self, query_embedding: np.ndarray, top_k: int = 5):
        """Retrieve across all DSL entities"""
        all_nodes = []
        for nodes_list in self.nodes_by_type.values():
            all_nodes.extend(nodes_list)
        return self._score_and_rank(all_nodes, query_embedding, top_k)
    
    def _score_and_rank(self, nodes: List[DSLNode], query_embedding: np.ndarray, top_k: int):
        """Score and rank nodes by similarity"""
        scores = []
        for node in nodes:
            if node.embedding is not None:
                score = np.dot(query_embedding, node.embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(node.embedding)
                )
                scores.append((node, score))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]


class EnhancedDomainDSLQueryEngine:
    """Enhanced query engine for complex ontologies with hierarchical retrieval"""
    
    def __init__(
        self,
        domain_ontology_path: str,
        dsl_ontology_path: str,
        llm,
        embed_model
    ):
        """Initialize engine with JSON-LD ontologies"""
        print("="*70)
        print("Initializing Enhanced Domain-DSL Query Engine")
        print("Hierarchical OG-RAG for Complex Ontologies")
        print("="*70)
        
        self.llm = llm
        self.embed_model = embed_model
        
        # Parse ontologies
        print("\n📚 Parsing ontologies...")
        domain_classes = OntologyParser.parse_domain_ontology(domain_ontology_path)
        dsl_nodes = OntologyParser.parse_dsl_ontology(dsl_ontology_path)
        
        # Build hypergraphs
        self.domain_graph = HierarchicalHyperGraph(embed_model)
        self.domain_graph.add_domain_classes(domain_classes)
        
        self.dsl_graph = DSLHyperGraph(embed_model)
        self.dsl_graph.add_dsl_nodes(dsl_nodes)
        
        print("\n" + "="*70)
        print("✓ Engine initialized successfully!")
        print("="*70)
    
    def retrieve_hierarchical_context(
        self,
        query: str,
        top_k_classes: int = 3,
        top_k_properties: int = 5,
        top_k_dsl: int = 5
    ) -> Dict:
        """Retrieve context with hierarchical structure"""
        query_embedding = self.embed_model.embed_query(query)
        
        # 1. Retrieve relevant classes
        relevant_classes = self.domain_graph.retrieve_classes(query_embedding, top_k_classes)
        
        # 2. For each class, retrieve relevant properties
        domain_context = []
        for cls, cls_score in relevant_classes:
            properties = self.domain_graph.retrieve_properties_for_class(
                cls.identifier,
                query_embedding,
                top_k_properties
            )
            domain_context.append({
                'class': cls,
                'class_score': cls_score,
                'properties': properties
            })
        
        # 3. Retrieve DSL entities
        dsl_context = self.dsl_graph.retrieve_all(query_embedding, top_k_dsl)
        
        return {
            'domain': domain_context,
            'dsl': dsl_context
        }
    
    def format_context(self, context: Dict) -> str:
        """Format retrieved context for LLM"""
        parts = []
        
        # Domain context
        parts.append("=== DOMAIN KNOWLEDGE ===\n")
        for item in context['domain']:
            cls = item['class']
            parts.append(f"Class: {cls.identifier}")
            parts.append(f"  Label: {cls.label}")
            parts.append(f"  Description: {cls.description}")
            if cls.example_individuals:
                parts.append(f"  Examples: {', '.join(cls.example_individuals[:3])}")
            
            if item['properties']:
                parts.append(f"  Related Properties:")
                for prop, score in item['properties']:
                    parts.append(f"    - {prop.get('property')}")
                    parts.append(f"      Label: {prop.get('label')}")
                    parts.append(f"      Description: {prop.get('description')}")
                    parts.append(f"      Range: {prop.get('range')}")
                    if prop.get('example_triples'):
                        parts.append(f"      Example: {prop['example_triples'][0]}")
            parts.append("")
        
        # DSL context
        parts.append("=== DSL SYNTAX ===\n")
        for node, score in context['dsl']:
            parts.append(f"{node.node_type}: {node.keyword}")
            parts.append(f"  Label: {node.label}")
            parts.append(f"  Description: {node.description}")
            parts.append(f"  Syntax: {node.syntax}")
            if node.example_dsl:
                parts.append(f"  Example: {node.example_dsl}")
            parts.append("")
        
        return "\n".join(parts)
    
    def generate(self, query: str) -> str:
        """Generate DSL query from natural language"""
        # Retrieve context
        context = self.retrieve_hierarchical_context(query)
        
        # Format context
        formatted_context = self.format_context(context)
        
        # Create prompt with clear instructions
        prompt = f"""You are a DSL query generator. Generate ONLY the DSL query code, nothing else.

DOMAIN & DSL KNOWLEDGE:
{formatted_context}

IMPORTANT RULES:
1. Output ONLY the DSL query code
2. Do NOT explain or describe the query
3. Do NOT use markdown code blocks
4. Use the exact DSL keywords from the knowledge above
5. Follow the syntax patterns from the examples

Question: {query}

DSL Query (code only):"""
        
        # Generate with LLM
        response = self.llm.invoke(prompt)
        result = response.content.strip()
        
        # Clean up if LLM still adds explanations
        if '```' in result:
            # Extract code from markdown blocks
            import re
            code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', result, re.DOTALL)
            if code_blocks:
                result = code_blocks[0].strip()
        
        # Remove common explanation prefixes
        lines = result.split('\n')
        clean_lines = []
        for line in lines:
            # Skip explanation lines
            if any(line.strip().startswith(prefix) for prefix in [
                'To ', 'The ', 'This ', 'We ', 'Here', 'Given', 'DSL Query:', 'Query:'
            ]):
                continue
            clean_lines.append(line)
        
        if clean_lines:
            result = '\n'.join(clean_lines).strip()
        
        return result, formatted_context


if __name__ == "__main__":
    print("""
Enhanced Domain-DSL Query Engine
=================================

This engine supports complex, hierarchical ontologies with:
- Rich NL patterns in descriptions
- Class-property relationships
- DSL categorization by kind
- Multi-level retrieval

To use:
    from enhanced_engine import EnhancedDomainDSLQueryEngine
    from langchain_groq import ChatGroq
    from langchain_community.embeddings import HuggingFaceEmbeddings
    
    engine = EnhancedDomainDSLQueryEngine(
        domain_ontology_path="data/kg/domain_extended/ontology/domain_extended.jsonld",
        dsl_ontology_path="data/kg/dsl_extended/ontology/dsl_extended.jsonld",
        llm=ChatGroq(...),
        embed_model=HuggingFaceEmbeddings(...)
    )
    
    result = engine.generate("Find average age of users older than 18")
""")
