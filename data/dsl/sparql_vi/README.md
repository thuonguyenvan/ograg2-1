# SPARQL-VI: Vietnamese SPARQL DSL for OG-RAG Testing

## Overview

SPARQL-VI is a Vietnamese variant of SPARQL designed to test OG-RAG (Ontology-Guided RAG) effectiveness. By translating SPARQL keywords to Vietnamese without diacritics, we ensure LLMs **cannot rely on pre-trained knowledge** and must use the ontology-provided context.

## Why SPARQL-VI?

### 1. **SPARQL is sufficiently complex**
- 50+ keywords (SELECT, WHERE, FILTER, GROUP BY, HAVING, etc.)
- Complex constraints (type checking, cardinality, operator precedence)
- Multiple query types (SELECT, CONSTRUCT, ASK, DESCRIBE)

### 2. **Aggressive obfuscation prevents guessing**
- **Strategy**: Double consonants + random noise suffixes (_JJ, _WW, _KK, _PP, _QQ, _RR, _ZZ, _YY)
- `CHONJ_KW` instead of `SELECT` → LLM cannot recognize pattern
- `NOII_MA_KK` instead of `WHERE` → No correlation to Vietnamese "nơi mà"
- `DEMM_JJ` instead of `COUNT` → Impossible to guess from "đếm"
- **No consistent pattern**: Each keyword has different suffix to prevent pattern learning
- **Result**: LLM has ~0% prior knowledge, **must use ontology context**

### 3. **Validation is straightforward**
- SPARQL-VI → SPARQL → Parse → Execute
- Clear success/failure criteria
- Bidirectional translator ensures consistency

## Keyword Mapping

| SPARQL | SPARQL-VI | Vietnamese Meaning | Obfuscation |
|--------|-----------|-------------------|-------------|
| SELECT | CHONJ_KW | Choose/Select | Double consonant + random suffix |
| WHERE | NOII_MA_KK | Where/At which | Doubled vowel + _KK |
| FILTER | LOCJ_RR | Filter | Added J + _RR |
| GROUP BY | NHOMM_THEO_YY | Group by | Double M + _YY |
| HAVING | COO_ZZ | Have/Having | Double O + _ZZ |
| ORDER BY | SAP_XXEP_THEO_KK | Sort by | XX instead of X + _KK |
| LIMIT | GIOI_HHAN_RR | Limit | Double H + _RR |
| OFFSET | DICCH_CHUYEN_WW | Offset/Shift | Double C + _WW |
| COUNT | DEMM_JJ | Count | Double M + _JJ |
| SUM | TONGG_WW | Sum/Total | Double G + _WW |
| AVG | TRUNGG_BINH_PP | Average | Double G + _PP |
| MAX | LONN_NHAT_RR | Maximum | Double N + _RR |
| MIN | NHOO_NHAT_QQ | Minimum | Double O + _QQ |
| DISTINCT | PHANN_BIET_PP | Distinct | Double N + _PP |
| AS | GOI_LLA_KK | Called/Named as | Double L + _KK |
| OPTIONAL | TUYJ_CHON_PP | Optional | Added J + _PP |
| UNION | HOPP_QQ | Union | Double P + _QQ |
| CONSTRUCT | XAY_DUNGWJ | Construct/Build | Added W + J |
| ASK | HOIQQ_YZ | Ask | Double Q + _YZ |
| DESCRIBE | MO_TAR_PP | Describe | Added R + _PP |
| AND | VAA_JJ | And | Double A + _JJ |
| OR | HOACC_WW | Or | Double C + _WW |
| NOT | KHONGG_RR | Not | Double G + _RR |
| ASC | TANGG_JJ | Ascending | Double G + _JJ |
| DESC | GIAMM_WW | Descending | Double M + _WW |
| FROM | TU_XZ | From | Added _XZ |
| MINUS | TRUU_WJ | Minus | Double U + _WJ |
| PREFIX | TIENN_TO_QQ | Prefix | Double N + _QQ |
| BASE | CO_SOO_JJ | Base | Double O + _JJ |
| REDUCED | GIAMM_RR | Reduced | Double M + _RR |
| SAMPLE | MAUU_ZZ | Sample | Double U + _ZZ |
| GROUP_CONCAT | NOII_NHOM_KK | Group Concat | Double I + _KK |
| BOUND | TONN_TAI_PP | Bound/Exists | Double N + _PP |
| isIRI | LAA_IRI_QQ | Is IRI | Double A + _QQ |
| isURI | LAA_URI_RR | Is URI | Double A + _RR |
| isBLANK | LAA_TRONG_KK | Is Blank | Double A + _KK |
| isLITERAL | LAA_LITERAL_WW | Is Literal | Double A + _WW |
| isNUMERIC | LAA_SO_JJ | Is Numeric | Double A + _JJ |
| LANG | NGONN_NGU_PP | Language | Double N + _PP |
| DATATYPE | KIEUU_DU_LIEU_QQ | Datatype | Double U + _QQ |
| STR | CHUOII_RR | String | Double I + _RR |
| STRLEN | DOO_DAI_CHUOI_KK | String Length | Double O + _KK |
| SUBSTR | CHUOII_CON_WW | Substring | Double I + _WW |
| UCASE | CHUU_HOA_JJ | Uppercase | Double U + _JJ |
| LCASE | CHUU_THUONG_PP | Lowercase | Double U + _PP |
| CONCAT | NOII_QQ | Concatenate | Double I + _QQ |
| CONTAINS | CHUAA_RR | Contains | Double A + _RR |
| STRSTARTS | BATT_DAU_VOI_KK | Starts With | Double T + _KK |
| STRENDS | KETT_THUC_VOI_WW | Ends With | Double T + _WW |
| REGEX | BIEUU_THUC_CHINH_QUY_JJ | Regular Expression | Double U + _JJ |
| REPLACE | THAYY_THE_PP | Replace | Double Y + _PP |
| a (rdf:type) | laa_jj | Is a / type | Double a + _jj |
| GRAPH | DOO_THI_RR | Graph | Double O + _RR |
| SERVICE | DICHH_VU_KK | Service | Double H + _KK |
| BIND | RANGG_BUOC_WW | Bind | Double G + _WW |
| VALUES | GIAA_TRI_QQ | Values | Double A + _QQ |

## Two-Ontology Architecture

SPARQL-VI uses **TWO ontologies** working together:

1. **DSL Ontology** (`sparql_vi_ontology.ttl`)
   - Defines SPARQL-VI syntax and keywords
   - Examples: CHONJ_KW, NOII_MA_KK, LOCJ_RR
   - Constraints: CO requires NHOMM_THEO_YY

2. **Domain Ontology** (`domain_ontology.ttl`)
   - Defines data schema (classes and properties)
   - Examples: Person, hasAge, livesIn
   - Entity mappings: "người" → :Person, "tuổi" → :hasAge

See [DOMAIN_ONTOLOGY.md](DOMAIN_ONTOLOGY.md) for detailed documentation.

## Project Structure

```
data/dsl/sparql_vi/
├── sparql_vi_ontology.ttl      # DSL Ontology (syntax rules)
├── domain_ontology.ttl          # Domain Ontology (data schema)
├── test_cases.json              # 30 test cases with domain context
├── test_cases.py                # Test generation script
├── README.md                    # This file
└── DOMAIN_ONTOLOGY.md           # Domain ontology documentation

dsl/
└── sparql_vi_translator.py      # Bidirectional translator SPARQL ↔ SPARQL-VI
```

## Ontology Structure

### Classes (Loại)
- **TruyVan** (Query): Base class
  - **TruyVanCHONJ_KW** (SELECT Query)
  - **TruyVanXAY_DUNGWJ** (CONSTRUCT Query)
  - **TruyVanHOIQQ_YZ** (ASK Query)
  - **TruyVanMO_TAR_PP** (DESCRIBE Query)

- **MenhDe** (Clause): Base class
  - **MenhDeNOII_MA_KK** (WHERE Clause)
  - **MenhDeLOCJ_RR** (FILTER Clause)
  - **MenhDeNHOMM_THEO_YY** (GROUP BY Clause)
  - **MenhDeCOO_ZZ** (HAVING Clause)
  - **MenhDeTUYJ_CHON_PP** (OPTIONAL Clause)

- **HamTongHop** (Aggregate Function): Base class
  - **HamDEMM_JJ** (COUNT)
  - **HamTONGG_WW** (SUM)
  - **HamTRUNGG_BINH_PP** (AVG)
  - **HamLONN_NHAT_RR** (MAX)
  - **HamNHOO_NHAT_QQ** (MIN)

### Constraints (Ràng Buộc)
Each class has formal constraints in the ontology:

```turtle
:MenhDeCOO_ZZ a owl:Class ;
    rdfs:label "COO_ZZ (HAVING)"@vi ;
    :constraint "Can only be used with NHOMM_THEO_YY" .

:HamDEMM_JJ a owl:Class ;
    rdfs:label "DEMM_JJ (COUNT)"@vi ;
    :constraint "Requires NHOMM_THEO_YY clause" .
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

### Example Test Case (with Domain Context)

```json
{
  "id": 21,
  "level": "complex",
  "category": "nested_aggregation",
  "nl_query": "Tìm top 10 thành phố có nhiều người nhất",
  "expected_vi": "CHONJ_KW ?thanh_pho (DEMM_JJ(?nguoi) GOI_LLA_KK ?so) NOII_MA_KK { ?nguoi :song_tai ?thanh_pho } NHOMM_THEO_YY ?thanh_pho SAP_XXEP_THEO_KK GIAMM_WW(?so) GIOI_HHAN_RR 10",
  "expected_sparql": "SELECT ?city (COUNT(?person) AS ?count) WHERE { ?person :livesIn ?city } GROUP BY ?city ORDER BY DESC(?count) LIMIT 10",
  "concepts": ["CHONJ_KW", "NOII_MA_KK", "DEMM_JJ", "NHOMM_THEO_YY", "SAP_XXEP_THEO_KK", "GIAMM_WW", "GIOI_HHAN_RR"],
  "validation": {
    "syntax_valid": true,
    "requires_groupby": true
  },
  "domain_schema": {
    "classes": [":Person", ":City"],
    "properties": [":livesIn"]
  },
  "entity_mapping": {
    "người": ":Person",
    "thành phố": ":City",
    "sống tại": ":livesIn"
  }
}
```

**Key Addition**: Each test case now includes:
- `domain_schema`: Required classes and properties
- `entity_mapping`: Vietnamese term → Ontology concept mapping

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
