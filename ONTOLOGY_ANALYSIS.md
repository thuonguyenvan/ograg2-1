# Phân tích Ontology Mới và Thiết kế Engine

## 📊 Thống kê Ontology

### Domain Ontology (1412 lines)
- **24 DomainClass**: Person, Customer, Product, Order, City, Warehouse, Supplier, Category, Address...
- **56 DomainProperty**: hasName, hasAge, livesIn, placedOrder, hasPrice, inCategory...
- **Đặc điểm**:
  - Mỗi class có: `identifier`, `label`, `description`, `example_individuals`, `related_properties[]`, `subclass_of`
  - Mỗi property trong class có: `property`, `label`, `description`, `range`, `example_triples[]`
  - **Rich context**: Description chứa typical questions
  - **Hierarchical**: Có quan hệ subclass_of (Customer subClassOf Person)
  - **Structured**: Related properties gắn với class cụ thể

### DSL Ontology (352 lines)
- **3 DSLQueryType**: CHONJ_KW (SELECT), XAY_DUNGWJ (CONSTRUCT), HOIQQ_YZ (ASK)
- **9 DSLFunction**: AVG, SUM, COUNT, MIN, MAX, ABS, ROUND, STRLEN, CONTAINS
- **4 DSLClause**: LOCJ_RR (FILTER), NHOMM_THEO_YY (GROUP BY), TUYJ_CHON_PP (OPTIONAL), GOI_LLA_KK (AS)
- **4 DSLModifier**: ORDER BY, LIMIT, OFFSET, DISTINCT
- **1 TriplePatternSpec**: Cấu trúc triple pattern
- **Đặc điểm**:
  - Mỗi entity có: `identifier`, `keyword`, `label`, `kind`, `description`, `syntax`, `example_dsl`
  - **Rich NL patterns**: Description chứa "Typical questions"
  - **Categorized**: Phân loại theo kind (aggregate, numeric, string, filter, modifier)
  - **Grammar-aware**: Có syntax và example DSL cụ thể

---

## 🔍 So sánh với SPARQL-VI Engine cũ

### SPARQL-VI Engine (Simple, 50 facts)
```json
// DSL: 28 flat facts
{
  "dsl_class": "TruyVanCHONJ_KW",
  "description": "SELECT query...",
  "syntax": "CHONJ_KW ?var NOII_MA_KK { pattern }",
  "example": "CHONJ_KW ?name NOII_MA_KK { ?person :hasName ?name }"
}

// Domain: 22 flat facts
{
  "domain_class": "Person",
  "description": "Represents a person",
  "label_en": "Person"
}
```

**Vấn đề**:
- ❌ Flat structure (no hierarchy)
- ❌ Properties tách rời khỏi classes
- ❌ Không có typical questions
- ❌ Thiếu contextual information
- ❌ Không có example triples

### New Ontology (Structured, 80 entities)
```json
// Domain: Nested structure with rich context
{
  "@type": "DomainClass",
  "identifier": ":Person",
  "description": "...Typical questions: 'list all users', 'average age of users'...",
  "related_properties": [
    {
      "property": ":hasAge",
      "description": "...Typical questions: 'users older than 18', 'average age'...",
      "range": "xsd:integer",
      "example_triples": ["ex:alice :hasAge 25 ."]
    }
  ]
}

// DSL: Categorized with NL patterns
{
  "@type": "DSLFunction",
  "keyword": "TRUNGG_BINH_PP",
  "kind": "aggregate",
  "description": "...Typical questions: 'average age of users', 'average price'..."
}
```

**Ưu điểm**:
- ✅ **Hierarchical**: Classes → Properties (context preserved)
- ✅ **Rich NL patterns**: "Typical questions" for better retrieval
- ✅ **Categorized**: kind field (aggregate, numeric, string, filter, modifier)
- ✅ **Contextual**: Example triples, range information
- ✅ **Query-aware**: Description explicitly mentions NL query patterns

---

## 🎯 Thiết kế Engine Mới

### Vấn đề cốt lõi
**Question**: "Find average age of users older than 18"

**Cần retrieve**:
1. **Domain knowledge**:
   - Class: `:Person` ("users")
   - Property: `:hasAge` (range: integer, filterable)
   - Constraint: age > 18 (FILTER clause)

2. **DSL knowledge**:
   - Query type: `CHONJ_KW` (SELECT for "find")
   - Aggregate: `TRUNGG_BINH_PP` (AVG for "average")
   - Filter: `LOCJ_RR` (for "older than")
   - Structure: SELECT with GROUP BY (because AVG)

3. **Integration**:
   - Map "users" → `:Person`
   - Map "age" → `:hasAge`
   - Map "average" → `TRUNGG_BINH_PP`
   - Map "older than" → `LOCJ_RR(?age > 18)`

### Approach 1: Flat Hypergraph (SPARQL-VI style)
**Vấn đề**: Mất cấu trúc hierarchical
- Person.hasAge → 2 separate nodes
- Không biết hasAge thuộc Person
- Retrieval độc lập → thiếu context

### Approach 2: Hierarchical Hypergraph (NEW)
**Idea**: Preserve structure trong hypergraph

```python
# HyperNode cho Class
class_node = {
    "type": "DomainClass",
    "id": ":Person",
    "label": "Person",
    "description": "...Typical questions: 'list all users', 'average age of users'...",
    "embedding": embed("Person. Typical questions: list all users, average age of users")
}

# HyperNode cho Property (với context từ parent class)
property_node = {
    "type": "DomainProperty",
    "id": ":hasAge",
    "parent_class": ":Person",  # IMPORTANT!
    "label": "age",
    "description": "...Typical questions: 'users older than 18', 'average age'...",
    "range": "xsd:integer",
    "embedding": embed("age of person. Typical questions: users older than 18, average age")
}

# HyperEdge liên kết Class → Property
edge = {
    "type": "class_has_property",
    "source": class_node,
    "target": property_node,
    "weight": 1.0
}
```

**Retrieval Strategy**:
1. **Semantic search** trên description (chứa typical questions)
2. **Graph walk**: Class → related Properties
3. **Type filtering**: aggregate functions cho "average", filter clause cho "older than"
4. **Context aggregation**: Class + Property + DSL function

### Approach 3: Multi-Level Index (RECOMMENDED)

**Level 1: NL Pattern Index**
```python
nl_patterns = {
    "average age of users": {
        "domain": [":Person", ":hasAge"],
        "dsl": ["TRUNGG_BINH_PP", "CHONJ_KW"]
    },
    "users older than": {
        "domain": [":Person", ":hasAge"],
        "dsl": ["LOCJ_RR", "CHONJ_KW"]
    }
}
```

**Level 2: Semantic Search** (fallback)
- Embed entire descriptions (with typical questions)
- Retrieve top-k relevant entities

**Level 3: Graph-based Retrieval**
- Start from retrieved Class
- Walk to related Properties
- Filter by range type (xsd:integer for numeric operations)

---

## ✅ Thiết kế Engine Mới: **NL-Aware Hierarchical OG-RAG**

### Architecture

```
Query: "Find average age of users older than 18"
    ↓
┌─────────────────────────────────────────────┐
│ 1. NL Pattern Matching (Fast)              │
│    - Extract keywords: "average", "age",    │
│      "users", "older than"                  │
│    - Match with descriptions                │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ 2. Semantic Retrieval (Hierarchical)       │
│    Domain:                                  │
│    - Retrieve Class (:Person) ✓            │
│    - Walk to Properties (:hasAge) ✓        │
│    - Check range (xsd:integer) ✓           │
│    DSL:                                     │
│    - Retrieve by kind:                      │
│      * aggregate → TRUNGG_BINH_PP ✓        │
│      * filter → LOCJ_RR ✓                  │
│      * query_type → CHONJ_KW ✓             │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ 3. Context Assembly                         │
│    Combine:                                 │
│    - Class description + example            │
│    - Property description + range + example │
│    - DSL function syntax + example          │
│    - Constraint rules (AVG requires GROUP)  │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ 4. LLM Generation                           │
│    Prompt with rich context:               │
│    - Domain: :Person, :hasAge (integer)    │
│    - DSL: CHONJ_KW, TRUNGG_BINH_PP, LOCJ_RR│
│    - Structure: SELECT-WHERE-FILTER        │
└─────────────────────────────────────────────┘
    ↓
Output: CHONJ_KW (TRUNGG_BINH_PP(?age) GOI_LLA_KK ?avg_age)
        NOII_MA_KK { ?person :hasAge ?age . LOCJ_RR(?age > 18) }
```

---

## 🚀 Implementation Plan

### Phase 1: Parser (Parse JSON-LD to Structured Nodes)
```python
class OntologyParser:
    def parse_domain_ontology(self, jsonld_path):
        # Parse DomainClass + nested related_properties
        # Create ClassNode + PropertyNode with parent link
        
    def parse_dsl_ontology(self, jsonld_path):
        # Parse by @type (DSLQueryType, DSLFunction, DSLClause, DSLModifier)
        # Create nodes with kind categorization
```

### Phase 2: Hierarchical Hypergraph
```python
class HierarchicalHyperGraph:
    def __init__(self):
        self.class_nodes = {}  # id → ClassNode
        self.property_nodes = {}  # id → PropertyNode
        self.dsl_nodes = {}  # id → DSLNode
        self.edges = []  # class_has_property, property_has_range
        
    def add_class_with_properties(self, class_data):
        # Create class node
        # Create property nodes with parent link
        # Create edges
        
    def retrieve_hierarchical(self, query_embedding, top_k=5):
        # 1. Retrieve top-k classes by semantic similarity
        # 2. For each class, get related properties
        # 3. Return (class, properties) tuples
```

### Phase 3: Multi-Index Retrieval
```python
class MultiIndexRetriever:
    def __init__(self, domain_graph, dsl_graph):
        self.domain_graph = domain_graph
        self.dsl_graph = dsl_graph
        self.nl_pattern_index = self._build_nl_index()
        
    def retrieve_by_nl_patterns(self, query):
        # Extract keywords: "average", "older than"
        # Match with typical questions in descriptions
        
    def retrieve_by_kind(self, query, kind):
        # Filter DSL nodes by kind (aggregate, filter, etc.)
        
    def retrieve_contextual(self, query):
        # 1. NL pattern matching
        # 2. Semantic retrieval
        # 3. Graph walk (class → properties)
        # 4. Type filtering (range check)
```

### Phase 4: New Engine
```python
class EnhancedDomainDSLQueryEngine:
    def __init__(self, domain_ontology_path, dsl_ontology_path, llm):
        # Parse ontologies
        self.domain_graph = HierarchicalHyperGraph.from_jsonld(domain_ontology_path)
        self.dsl_graph = HierarchicalHyperGraph.from_jsonld(dsl_ontology_path)
        
        # Build retrievers
        self.retriever = MultiIndexRetriever(self.domain_graph, self.dsl_graph)
        self.llm = llm
        
    def query(self, nl_query):
        # 1. Retrieve hierarchical context
        domain_context = self.retriever.retrieve_domain_context(nl_query)
        dsl_context = self.retriever.retrieve_dsl_context(nl_query)
        
        # 2. Assemble rich context
        context = self._assemble_context(domain_context, dsl_context)
        
        # 3. Generate with LLM
        return self.llm.generate(nl_query, context)
```

---

## 📌 Key Differences from SPARQL-VI Engine

| Aspect | SPARQL-VI (Old) | Enhanced Engine (New) |
|--------|-----------------|----------------------|
| **Structure** | Flat facts | Hierarchical (Class → Properties) |
| **Context** | Minimal descriptions | Rich: typical questions, examples |
| **Retrieval** | Pure semantic search | Multi-level: NL patterns + semantic + graph walk |
| **Domain-Property** | Separate nodes | Linked (parent_class) |
| **DSL Organization** | Flat list | Categorized by kind |
| **Scale** | 50 simple facts | 80 complex entities with nested data |
| **NL Awareness** | Basic | High (descriptions contain typical questions) |

---

## 🎯 Next Steps

1. ✅ Implement `OntologyParser` for JSON-LD
2. ✅ Build `HierarchicalHyperGraph` with parent links
3. ✅ Create `MultiIndexRetriever` with NL pattern matching
4. ✅ Implement `EnhancedDomainDSLQueryEngine`
5. ✅ Test with complex queries

Bạn muốn tôi implement engine mới này không?
