# 🧠 Smart Context Design - Universal Ontology System

## Tổng quan

Hệ thống áp dụng **Smart Context** một cách **HOÀN TOÀN TỔNG QUÁT** cho mọi ontology, không cần configuration riêng.

---

## 1. Chunking Strategy (build_hypergraph.py)

### Tại sao chunk?
- **Ontology terms phức tạp**: Có thể có definition dài, nhiều synonyms, relationships, examples
- **Embedding hiệu quả hơn**: Mỗi chunk tập trung vào 1 khía cạnh
- **Retrieval chính xác hơn**: Match đúng phần cần thiết

### Chunk Types (4 loại):

#### 1. **CORE Chunk** (Luôn có - Ưu tiên cao nhất)
```
ID: GO:0006281
Label: DNA repair
Definition: The process of restoring DNA after damage...
Namespace: biological_process
```
- **Purpose**: Thông tin cốt lõi nhất của term
- **Khi nào match**: Query về khái niệm chính

#### 2. **SYNONYMS Chunk** (Nếu có synonyms)
```
Term: GO:0006281
Label: DNA repair
Synonyms: DNA repair process, DNA damage repair
```
- **Purpose**: Tìm term qua tên gọi khác
- **Khi nào match**: User dùng từ đồng nghĩa

#### 3. **RELATIONSHIPS Chunk** (Nếu có relationships)
```
Term: GO:0006281
Label: DNA repair
Relationships:
  is_a: GO:0006259 (DNA metabolic process)
  part_of: GO:0071897 (DNA biosynthetic process)
```
- **Purpose**: Hiểu vị trí trong hierarchy, related concepts
- **Khi nào match**: Query về quan hệ giữa các terms
- **Bonus**: Chứa `_parents` để expand hierarchy

#### 4. **DETAILS Chunk** (Nếu có examples/comments)
```
Term: GO:0006281
Label: DNA repair
Examples:
  • Base excision repair (BER) is initiated by...
Comments:
  • This process is essential for maintaining genomic stability
```
- **Purpose**: Context chi tiết, ví dụ cụ thể
- **Khi nào match**: Query về chi tiết, cách thức hoạt động

---

## 2. Hierarchical Expansion (generic_query_engine.py)

### Strategy:

1. **Retrieve top-k chunks** (dual ranking: key + value similarity)
2. **Group by term_id** → Merge chunks của cùng 1 term
3. **Expand hierarchy** → Add parent terms for context

### Tại sao expand parents?

Ontology có cấu trúc **tree hierarchy**:
```
evidence (ECO:0000000)
  └─ computational evidence (ECO:0007672)
      ├─ computational evidence used in manual assertion
      └─ computational evidence used in automatic assertion
```

Khi user hỏi về "computational evidence", nên show:
- ✅ Term chính (ECO:0007672)
- ✅ **Parent term** (ECO:0000000 - evidence) → Hiểu broader context
- ✅ **Child terms** (các loại specific hơn) → Hiểu variations

### Code flow:

```python
# 1. Retrieve chunks
retrieved_chunks = retrieve(query, top_k=5)

# 2. Group by term
terms = group_by_term_id(retrieved_chunks)  
# → Có thể có 5 chunks nhưng chỉ 2-3 terms

# 3. Expand hierarchy
parent_ids = extract_parent_ids(terms)
parent_terms = find_parent_chunks(parent_ids)
results = terms + parent_terms[:2]  # Add max 2 parents
```

---

## 3. Tổng quát hóa

### ✅ Works với MỌI ontology vì:

1. **Auto-detect chunks**: Không hardcode fields
   - Có definition? → Core chunk
   - Có synonyms? → Synonyms chunk
   - Có relationships? → Relationships chunk
   - Có examples/comments? → Details chunk

2. **Generic relationship extraction**:
   - Không hardcode `is_a`, `part_of`
   - Parse **TẤT CẢ relationship types** từ OWL
   - Tự động detect parent terms từ `is_a` relationships

3. **Dynamic formatting**:
   - Không hardcode prefix (GO, ECO, SO...)
   - Format từ `_raw_term` data
   - Hiển thị TẤT CẢ fields có sẵn

---

## 4. So sánh với approaches khác

### ❌ **Naive RAG**:
```
- 1 term = 1 giant chunk
- Embed toàn bộ → Không focused
- Retrieve → Có thể miss relevant info nếu query chỉ match 1 phần
```

### ❌ **Fixed chunking**:
```
- Split by length (e.g., every 512 tokens)
- Cắt ngang definition, relationships
- Mất ngữ cảnh
```

### ✅ **Smart Context (Our approach)**:
```
+ 1 term = 4 semantic chunks
+ Mỗi chunk tập trung 1 aspect
+ Group lại khi retrieve → Complete term
+ Expand hierarchy → Related context
```

---

## 5. Performance Benefits

### Memory Efficiency:
- Không duplicate data (chỉ lưu pointer `_raw_term`)
- Mỗi chunk nhỏ → Embed nhanh hơn

### Retrieval Quality:
- **Precision**: Match đúng phần cần thiết
- **Recall**: Group chunks → Không miss info
- **Context**: Hierarchy expansion → Hiểu broader picture

### Example:

Query: "What is DNA repair?"

**Without Smart Context**:
```
Retrieved: GO:0006281 (full term, 500 tokens)
Score: 0.75
```

**With Smart Context**:
```
Retrieved:
1. GO:0006281 - CORE chunk (definition) 
   Score: 0.92 ← Higher! Focused match
2. GO:0006281 - SYNONYMS chunk
   Score: 0.85
3. GO:0006259 (parent: DNA metabolic process)
   Score: 0.50 (context)

→ Merge chunks 1+2 → Complete GO:0006281
→ Add parent for context
```

---

## 6. Configuration (Zero config!)

Không cần config vì:
- ✅ Auto-detect chunk types từ fields available
- ✅ Auto-extract relationships từ parsed data
- ✅ Auto-format output based on ontology prefix
- ✅ Works with ANY OWL ontology

---

## 7. Extension Ideas (Future)

1. **Cross-term expansion**:
   - Add sibling terms (same parent)
   - Add related terms (part_of, regulates, etc.)

2. **Weighted chunks**:
   - Core chunk: weight=1.0
   - Relationships: weight=0.8
   - Details: weight=0.6

3. **Query-aware expansion**:
   - Query về definition → Only core chunks
   - Query về relationships → Expand more
   - Query về examples → Include details chunks

4. **Caching**:
   - Cache parent lookup
   - Cache term_id → chunks mapping

---

## 8. Testing

Test với ECO ontology:
```bash
# Build với smart chunking
python build_hypergraph.py --ontology-dir data/ontologies/.../parsed_new

# Query với hierarchy expansion
python -c "
from query_engine.generic_query_engine import GenericQueryEngine
engine = GenericQueryEngine('data/ontologies/.../parsed_new')
result = engine.query('what is computational evidence', top_k=3)
print(result['full_context'])
"
```

Expected output:
- ✅ ECO:0007672 (main term) with ALL chunks merged
- ✅ ECO:0000000 (parent: evidence) for context
- ✅ Related children terms if relevant

---

## Kết luận

Smart Context = **Chunking thông minh + Hierarchical expansion**

- 🎯 **Universal**: Works với mọi ontology
- ⚡ **Efficient**: Better retrieval quality
- 🧠 **Smart**: Context-aware expansion
- 🔧 **Zero-config**: Tự động detect patterns

**No hardcoding. No configuration. Just works.**
