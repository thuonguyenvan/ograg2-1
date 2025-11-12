# Lazy imports to avoid dependency issues
# Import only when needed

def __getattr__(name):
    """Lazy import to avoid loading modules with heavy dependencies."""
    
    if name == "SPARQLVIQueryEngine":
        from query_engine.sparql_vi_ograg_engine import SPARQLVIQueryEngine
        return SPARQLVIQueryEngine
    
    if name == "KnowledgeGraphListQueryEngine":
        from query_engine.knowledge_graph_query_engine import KnowledgeGraphListQueryEngine
        return KnowledgeGraphListQueryEngine
    
    if name == "KnowledgeGraphListQueryEngineOG":
        from query_engine.knowledge_graph_query_engine import KnowledgeGraphListQueryEngineOG
        return KnowledgeGraphListQueryEngineOG
    
    if name == "KnowledgeGraphListQueryEngineReverse":
        from query_engine.knowledge_graph_query_engine import KnowledgeGraphListQueryEngineReverse
        return KnowledgeGraphListQueryEngineReverse
    
    if name == "KnowledgeGraphListQueryEngineDefault":
        from query_engine.knowledge_graph_query_engine import KnowledgeGraphListQueryEngineDefault
        return KnowledgeGraphListQueryEngineDefault
    
    if name == "KnowledgeTriplesGraphQueryEngine":
        from query_engine.knowledge_graph_query_engine import KnowledgeTriplesGraphQueryEngine
        return KnowledgeTriplesGraphQueryEngine
    
    if name == "LLMQueryEngine":
        from query_engine.llm_query_engine import LLMQueryEngine
        return LLMQueryEngine
    
    if name == "RAGQueryEngine":
        from query_engine.rag_query_engine import RAGQueryEngine
        return RAGQueryEngine
    
    if name == "SnippetRAGQueryEngine":
        from query_engine.snippet_rag_query_engine import SnippetRAGQueryEngine
        return SnippetRAGQueryEngine
    
    if name == "OntoHyperGraphQueryEngine":
        from query_engine.ontograph_query_engine import OntoHyperGraphQueryEngine
        return OntoHyperGraphQueryEngine
    
    if name == "OntoGraphQueryEngine":
        from query_engine.ontograph_query_engine_copy import OntoGraphQueryEngine
        return OntoGraphQueryEngine
    
    if name == "FullOntoQueryEngine":
        from query_engine.full_onto_query_engine import FullOntoQueryEngine
        return FullOntoQueryEngine
    
    if name == "RaptorQueryEngine":
        from query_engine.raptor_query_engine import RaptorQueryEngine
        return RaptorQueryEngine
    
    if name == "GraphRAGQueryEngine":
        from query_engine.graphrag_query_engine import GraphRAGQueryEngine
        return GraphRAGQueryEngine
    
    raise AttributeError(f"module 'query_engine' has no attribute '{name}'")

__all__ = [
    "SPARQLVIQueryEngine",
    "KnowledgeGraphListQueryEngine",
    "KnowledgeGraphListQueryEngineOG",
    "KnowledgeGraphListQueryEngineReverse",
    "KnowledgeGraphListQueryEngineDefault",
    "KnowledgeTriplesGraphQueryEngine",
    "LLMQueryEngine",
    "RAGQueryEngine",
    "SnippetRAGQueryEngine",
    "OntoGraphQueryEngine", 
    "OntoHyperGraphQueryEngine",
    "FullOntoQueryEngine",
    "RaptorQueryEngine",
    "GraphRAGQueryEngine"
]