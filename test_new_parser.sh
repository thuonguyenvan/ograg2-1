#!/bin/bash
# Test new universal parser and hypergraph builder

set -e

echo "Testing Universal OWL Parser + HyperGraph"
echo "=========================================="
echo ""

# Test directory
TEST_DIR="data/ontologies/3657d8300e5207f8"
PARSED_DIR="$TEST_DIR/parsed_new"

echo "Step 1: Parsing OWL with universal XML parser..."
python scripts/parse_owl.py \
    --owl-file "$TEST_DIR/ontology.owl" \
    --output-dir "$PARSED_DIR"

echo ""
echo "Step 2: Building hypergraph with no-loss approach..."
python build_hypergraph.py \
    --ontology-dir "$PARSED_DIR"

echo ""
echo "Step 3: Testing query..."
python -c "
from query_engine.generic_query_engine import GenericQueryEngine
import os

engine = GenericQueryEngine(
    ontology_dir='$PARSED_DIR',
    groq_api_key=os.getenv('GROQ_API_KEY')
)

result = engine.query('what is computational evidence', top_k=3, use_llm=False)

print('='*80)
print('Query: what is computational evidence')
print('='*80)
print()
print('Retrieved Facts:')
print(result['full_context'])
"

echo ""
echo "✅ Test complete!"
