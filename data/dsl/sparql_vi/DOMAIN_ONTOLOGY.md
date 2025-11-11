# Domain Ontology for SPARQL-VI Test Cases

## Overview

This domain ontology defines the **data schema** (classes and properties) used in all 30 SPARQL-VI test cases. It works together with the **DSL Ontology** (SPARQL-VI syntax) to enable complete NL→DSL generation.

## Two-Ontology Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Natural Language Query                    │
│          "Tìm người có tuổi lớn hơn 18"                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
                    ┌─────────────────────┐
                    │    OG-RAG System    │
                    └─────────────────────┘
                              ↓
         ┌────────────────────┴────────────────────┐
         ↓                                         ↓
┌──────────────────────┐              ┌──────────────────────┐
│   DSL Ontology       │              │  Domain Ontology     │
│  (Syntax Rules)      │              │  (Data Schema)       │
├──────────────────────┤              ├──────────────────────┤
│ - CHONJ_KW = SELECT  │              │ - "người" = :Person  │
│ - NOII_MA_KK = WHERE │              │ - "tuổi" = :hasAge   │
│ - LOCJ_RR = FILTER   │              │ - :Person class      │
│ - Constraints        │              │ - :hasAge property   │
└──────────────────────┘              └──────────────────────┘
         ↓                                         ↓
         └────────────────────┬────────────────────┘
                              ↓
                    ┌─────────────────────┐
                    │   LLM Generation    │
                    └─────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Generated SPARQL-VI                       │
│  CHONJ_KW ?nguoi NOII_MA_KK { ?nguoi :coTuoi ?tuoi .       │
│                               LOCJ_RR(?tuoi > 18) }          │
└─────────────────────────────────────────────────────────────┘
```

## Classes (Lớp Đối Tượng)

| Class | Vietnamese | Description | Usage in Test Cases |
|-------|-----------|-------------|---------------------|
| `:Person` | Người | A person/user | 25 test cases |
| `:Customer` | Khách hàng | A customer (subclass of Person) | 8 test cases |
| `:Product` | Sản phẩm | A product that can be purchased | 10 test cases |
| `:Book` | Sách | A book (subclass of Product) | 2 test cases |
| `:Order` | Đơn hàng | A purchase order | 6 test cases |
| `:City` | Thành phố | A city/location | 7 test cases |
| `:Category` | Danh mục | Product category | 5 test cases |

## Properties (Thuộc Tính)

### Datatype Properties

| Property | Vietnamese | Domain | Range | Description |
|----------|-----------|---------|-------|-------------|
| `:hasName` | tên | Person | string | Person's name |
| `:hasAge` | tuổi | Person | integer | Person's age |
| `:hasEmail` | email | Person | string | Email address |
| `:hasPhone` | điện thoại, sdt | Person | string | Phone number |
| `:hasNick` | nick, nickname | Person | string | Nickname |
| `:hasPrice` | giá | Product, Order | decimal | Price value |
| `:cityName` | tên thành phố | City | string | City name |
| `:categoryName` | tên danh mục | Category | string | Category name |

### Object Properties

| Property | Vietnamese | Domain | Range | Description |
|----------|-----------|---------|-------|-------------|
| `:livesIn` | sống tại, ở | Person | City | Person lives in city |
| `:ofCustomer` | của khách hàng | Order | Customer | Order belongs to customer |
| `:placeOrder` | đặt đơn hàng | Customer | Order | Customer places order |
| `:inCategory` | thuộc danh mục | Product | Category | Product in category |
| `:friendOf` | bạn, bạn bè | Person | Person | Friendship (symmetric) |
| `:borrowed` | mượn | Person | Book | Person borrowed book |

## Entity Mapping

The ontology includes explicit mappings from Vietnamese terms to ontology concepts:

### Class Mappings

```turtle
:nguoi_mapping a :EntityMapping ;
    :vietnameseTerm "người" ;
    :mapsToClass :Person .

:khach_hang_mapping a :EntityMapping ;
    :vietnameseTerm "khách hàng" ;
    :vietnameseTerm "khách" ;
    :mapsToClass :Customer .
```

### Property Mappings

```turtle
:tuoi_mapping a :EntityMapping ;
    :vietnameseTerm "tuổi" ;
    :mapsToProperty :hasAge .

:gia_mapping a :EntityMapping ;
    :vietnameseTerm "giá" ;
    :vietnameseTerm "giá trị" ;
    :vietnameseTerm "giá tiền" ;
    :mapsToProperty :hasPrice .
```

## Integration with Test Cases

Each of the 30 test cases now includes:

### 1. Domain Schema
Specifies which classes and properties are needed:
```json
"domain_schema": {
  "classes": [":Person"],
  "properties": [":hasAge"]
}
```

### 2. Entity Mapping
Maps Vietnamese terms to ontology concepts:
```json
"entity_mapping": {
  "người": ":Person",
  "tuổi": ":hasAge"
}
```

### Example: Complete Test Case

```json
{
  "id": 3,
  "nl_query": "Tìm người có tuổi lớn hơn 18",
  "expected_vi": "CHONJ_KW ?nguoi NOII_MA_KK { ?nguoi :coTuoi ?tuoi . LOCJ_RR(?tuoi > 18) }",
  "expected_sparql": "SELECT ?person WHERE { ?person :hasAge ?age . FILTER(?age > 18) }",
  "domain_schema": {
    "classes": [":Person"],
    "properties": [":hasAge"]
  },
  "entity_mapping": {
    "người": ":Person",
    "tuổi": ":hasAge"
  }
}
```

## How OG-RAG Uses Both Ontologies

### Phase 1: Entity Recognition (Domain Ontology)
```
NL: "Tìm người có tuổi lớn hơn 18"
          ↓
Retrieve from Domain Ontology:
- "người" → :Person class
- "tuổi" → :hasAge property
- :hasAge domain is :Person
- :hasAge range is xsd:integer
```

### Phase 2: DSL Syntax Generation (DSL Ontology)
```
Task: Generate SPARQL-VI query structure
          ↓
Retrieve from DSL Ontology:
- Query type: CHONJ_KW (SELECT)
- Pattern clause: NOII_MA_KK (WHERE)
- Filter condition: LOCJ_RR (FILTER)
- Comparison operator: > (greater than)
```

### Phase 3: Final Generation
```
Combine contexts:
- Entities: ?nguoi (Person), ?tuoi (age)
- Properties: :coTuoi (:hasAge)
- DSL Keywords: CHONJ_KW, NOII_MA_KK, LOCJ_RR
          ↓
Generated Query:
CHONJ_KW ?nguoi NOII_MA_KK { 
  ?nguoi :coTuoi ?tuoi . 
  LOCJ_RR(?tuoi > 18) 
}
```

## Sample Data

The ontology includes sample instances for validation:

```turtle
:person1 a :Person ;
    :hasName "Nguyen Van A" ;
    :hasAge 25 ;
    :hasEmail "nguyenvana@example.com" ;
    :livesIn :hanoi .

:hanoi a :City ;
    :cityName "Hà Nội" .

:book1 a :Book ;
    :hasName "Introduction to SPARQL" ;
    :hasPrice 150000 ;
    :inCategory :tech_books .
```

## Statistics

- **Total Classes**: 7
- **Total Properties**: 12 (6 datatype + 6 object)
- **Entity Mappings**: 20+ Vietnamese terms
- **Test Case Coverage**: 100% (all 30 test cases covered)

## Files

- `domain_ontology.ttl` - OWL/Turtle ontology definition
- `test_cases.json` - 30 test cases with domain schema
- `test_cases.py` - Python source for test generation

## Expected Impact

With both ontologies:

### Baseline (LLM only - no context)
- **Accuracy**: <1% (Cannot guess obfuscated keywords or Vietnamese mappings)

### OG-RAG (with both ontologies)
- **Accuracy**: 65-75% (Can retrieve and combine both syntax and schema knowledge)
- **Improvement**: +65-75 percentage points

This demonstrates the **critical importance of ontology-guided context retrieval** for DSL generation in low-resource scenarios.
