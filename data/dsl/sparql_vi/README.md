# SPARQL-VI: Vietnamese SPARQL DSL for OG-RAG Testing

## Overview

SPARQL-VI is a Vietnamese variant of SPARQL designed to test OG-RAG (Ontology-Guided RAG) effectiveness. By translating SPARQL keywords to Vietnamese without diacritics, we ensure LLMs **cannot rely on pre-trained knowledge** and must use the ontology-provided context.

## Why SPARQL-VI?

### 1. **SPARQL is sufficiently complex**
- 50+ keywords (SELECT, WHERE, FILTER, GROUP BY, HAVING, etc.)
- Complex constraints (type checking, cardinality, operator precedence)
- Multiple query types (SELECT, CONSTRUCT, ASK, DESCRIBE)

### 2. **Vietnamese keywords force context reliance**
- `CHON` instead of `SELECT` → LLM has 0% prior knowledge
- `NOI_MA` instead of `WHERE` → Must retrieve from ontology
- `DEM` instead of `COUNT` → Cannot guess meaning

### 3. **Validation is straightforward**
- SPARQL-VI → SPARQL → Parse → Execute
- Clear success/failure criteria

## Keyword Mapping

| SPARQL | SPARQL-VI | Vietnamese Meaning |
|--------|-----------|-------------------|
| SELECT | CHON | Choose/Select |
| WHERE | NOI_MA | Where/At which |
| FILTER | LOC | Filter |
| GROUP BY | NHOM_THEO | Group by |
| HAVING | CO | Have/Having |
| ORDER BY | SAP_XEP_THEO | Sort by |
| LIMIT | GIOI_HAN | Limit |
| OFFSET | DICH_CHUYEN | Offset/Shift |
| COUNT | DEM | Count |
| SUM | TONG | Sum/Total |
| AVG | TRUNG_BINH | Average |
| MAX | LON_NHAT | Maximum |
| MIN | NHO_NHAT | Minimum |
| DISTINCT | PHAN_BIET | Distinct |
| AS | GOI_LA | Called/Named as |
| OPTIONAL | TUY_CHON | Optional |
| UNION | HOP | Union |
| CONSTRUCT | XAY_DUNG | Construct/Build |
| ASK | HOI | Ask |
| DESCRIBE | MO_TA | Describe |
| AND | VA | And |
| OR | HOAC | Or |
| NOT | KHONG | Not |
| ASC | TANG | Ascending |
| DESC | GIAM | Descending |

## Project Structure

```
data/dsl/sparql_vi/
├── sparql_vi_ontology.ttl      # Formal OWL ontology
├── test_cases.json              # 30 test cases (10 simple, 10 medium, 10 complex)
└── README.md                    # This file

dsl/
└── sparql_vi_translator.py      # Bidirectional translator SPARQL ↔ SPARQL-VI
```

## Ontology Structure

### Classes (Loại)
- **TruyVan** (Query): Base class
  - **TruyVanCHON** (SELECT Query)
  - **TruyVanXAY_DUNG** (CONSTRUCT Query)
  - **TruyVanHOI** (ASK Query)
  - **TruyVanMO_TA** (DESCRIBE Query)

- **MenhDe** (Clause): Base class
  - **MenhDeNOI_MA** (WHERE Clause)
  - **MenhDeLOC** (FILTER Clause)
  - **MenhDeNHOM_THEO** (GROUP BY Clause)
  - **MenhDeCO** (HAVING Clause)
  - **MenhDeTUY_CHON** (OPTIONAL Clause)

- **HamTongHop** (Aggregate Function): Base class
  - **HamDEM** (COUNT)
  - **HamTONG** (SUM)
  - **HamTRUNG_BINH** (AVG)
  - **HamLON_NHAT** (MAX)
  - **HamNHO_NHAT** (MIN)

### Constraints (Ràng Buộc)
Each class has formal constraints in the ontology:

```turtle
:MenhDeCO a owl:Class ;
    rdfs:label "CO (HAVING)"@vi ;
    :constraint "Can only be used with NHOM_THEO" .

:HamDEM a owl:Class ;
    rdfs:label "DEM (COUNT)"@vi ;
    :constraint "Requires NHOM_THEO clause" .
```

## Test Dataset

### 30 Test Cases

**Level 1: Simple (10 cases)**
- Basic SELECT queries
- Simple FILTER conditions
- OPTIONAL, DISTINCT, LIMIT
- ASK queries

**Level 2: Medium (10 cases)**
- Aggregation (COUNT, SUM, AVG)
- GROUP BY + HAVING
- UNION queries
- Multiple filters
- CONSTRUCT queries

**Level 3: Complex (10 cases)**
- Nested aggregation with ORDER BY + LIMIT
- Multiple aggregates
- Subqueries
- Complex HAVING with multiple conditions
- REGEX patterns
- Full pipeline queries

### Example Test Case

```json
{
  "id": 21,
  "level": "complex",
  "category": "nested_aggregation",
  "nl_query": "Tìm top 10 thành phố có nhiều người nhất",
  "expected_vi": "CHON ?thanh_pho (DEM(?nguoi) GOI_LA ?so) NOI_MA { ?nguoi :song_tai ?thanh_pho } NHOM_THEO ?thanh_pho SAP_XEP_THEO GIAM(?so) GIOI_HAN 10",
  "expected_sparql": "SELECT ?city (COUNT(?person) AS ?count) WHERE { ?person :livesIn ?city } GROUP BY ?city ORDER BY DESC(?count) LIMIT 10",
  "concepts": ["CHON", "NOI_MA", "DEM", "NHOM_THEO", "SAP_XEP_THEO", "GIAM", "GIOI_HAN"],
  "validation": {
    "syntax_valid": true,
    "requires_groupby": true
  }
}
```

## Expected Results

### Baseline (LLM only - no context)
- **Simple**: 5-10% (Cannot guess Vietnamese keywords)
- **Medium**: 0-5% (No knowledge of NHOM_THEO, CO, etc.)
- **Complex**: 0% (Impossible without context)
- **Average**: ~5%

### With Examples (Few-shot)
- **Simple**: 20-30% (Can copy patterns)
- **Medium**: 10-15% (Limited generalization)
- **Complex**: 5-10% (Struggles with new combinations)
- **Average**: ~15-20%

### With OG-RAG (Ontology-guided)
- **Simple**: 85-95% (Clear context from ontology)
- **Medium**: 75-85% (Retrieves constraints correctly)
- **Complex**: 60-75% (Benefits from constraint checking)
- **Average**: **75-85%**

### Expected Improvement
**+60-70% absolute improvement** over baseline, demonstrating clear OG-RAG effectiveness!

## Validation Strategy

### 1. Syntax Validation
```python
vi_query → translator → sparql_query → parse → ✓/✗
```

### 2. Constraint Validation
Check ontology constraints:
- `CO` must have `NHOM_THEO` ✓
- `DEM` requires `NHOM_THEO` ✓
- `GIOI_HAN` must be non-negative integer ✓

### 3. Semantic Validation
- Variable bindings correct
- Type compatibility
- Operator precedence

## Usage

### 1. Translate Query
```python
from dsl.sparql_vi_translator import SPARQLVITranslator

translator = SPARQLVITranslator()

# Vietnamese → SPARQL
sparql = translator.vi_to_sparql(
    "CHON ?ten NOI_MA { ?nguoi :coTen ?ten }"
)
# → "SELECT ?name WHERE { ?person :hasName ?name }"

# SPARQL → Vietnamese
vi = translator.sparql_to_vi(
    "SELECT ?name WHERE { ?person :hasName ?name }"
)
# → "CHON ?ten NOI_MA { ?nguoi :coTen ?ten }"
```

### 2. Validate Query
```python
is_valid, result = translator.validate_vi_query(vi_query)
if is_valid:
    print(f"Valid! SPARQL: {result}")
else:
    print(f"Error: {result}")
```

## Implementation Roadmap

### Week 1: Setup ✅
- [x] SPARQL-VI translator
- [x] Ontology creation (OWL/Turtle)
- [x] Test dataset (30 cases)
- [x] Documentation

### Week 2: OG-RAG Pipeline
- [ ] Build hypergraph from ontology
- [ ] Implement smart context retrieval
- [ ] Prompt engineering for generation
- [ ] Validation pipeline

### Week 3: Evaluation
- [ ] Run baseline (LLM only)
- [ ] Run few-shot baseline
- [ ] Run OG-RAG pipeline
- [ ] Collect metrics

### Week 4: Analysis
- [ ] Compare results
- [ ] Error analysis
- [ ] Write paper section
- [ ] Prepare presentation

## Metrics

1. **Syntax Accuracy**: % queries with valid syntax
2. **Constraint Satisfaction**: % queries satisfying ontology constraints
3. **Exact Match**: % queries matching expected output
4. **Semantic Equivalence**: % queries logically equivalent
5. **Execution Success**: % queries that execute without error

## Citation

```bibtex
@misc{sparqlvi2025,
  title={SPARQL-VI: Vietnamese SPARQL for Testing Ontology-Guided RAG},
  author={Nguyen Van Thuong},
  year={2025},
  note={Test dataset for OG-RAG evaluation}
}
```

## License

MIT License - Feel free to use for research purposes.
