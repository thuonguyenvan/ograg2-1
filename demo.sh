#!/bin/bash
# Quick demo script to test the full pipeline

echo "================================="
echo "OG-RAG Quick Demo"
echo "================================="
echo ""

# Check if OWL file provided
if [ "$#" -ne 1 ]; then
    echo "Usage: ./demo.sh <path-to-owl-file>"
    echo ""
    echo "Example:"
    echo "  ./demo.sh go-basic.owl"
    echo ""
    echo "Download sample ontologies:"
    echo "  wget http://purl.obolibrary.org/obo/go/go-basic.owl    # Gene Ontology"
    echo "  wget http://purl.obolibrary.org/obo/hp.owl             # Human Phenotype"
    echo "  wget http://purl.obolibrary.org/obo/so.owl             # Sequence Ontology"
    exit 1
fi

OWL_FILE=$1
OUTPUT_DIR="demo_output"

echo "Input: $OWL_FILE"
echo "Output: $OUTPUT_DIR"
echo ""

# Step 1: Parse OWL
echo "Step 1/3: Parsing OWL file..."
python scripts/parse_owl.py \
    --owl-file "$OWL_FILE" \
    --output-dir "$OUTPUT_DIR"

if [ $? -ne 0 ]; then
    echo "❌ Parsing failed!"
    exit 1
fi

echo ""

# Step 2: Build Hypergraph
echo "Step 2/3: Building hypergraph..."
python build_hypergraph.py \
    --ontology-dir "$OUTPUT_DIR" \
    --model sentence-transformers/all-MiniLM-L6-v2

if [ $? -ne 0 ]; then
    echo "❌ Hypergraph building failed!"
    exit 1
fi

echo ""

# Step 3: Test Query
echo "Step 3/3: Testing query..."
echo ""

# Sample queries based on common ontologies
if [[ "$OWL_FILE" == *"go"* ]]; then
    QUERY="What is DNA repair?"
elif [[ "$OWL_FILE" == *"hp"* ]]; then
    QUERY="What is diabetes?"
elif [[ "$OWL_FILE" == *"so"* ]]; then
    QUERY="What is a gene?"
else
    QUERY="What is this ontology about?"
fi

echo "Sample query: $QUERY"
echo ""

python query_engine/generic_query_engine.py \
    --ontology-dir "$OUTPUT_DIR" \
    --query "$QUERY" \
    --no-llm

echo ""
echo "================================="
echo "✅ Demo complete!"
echo "================================="
echo ""
echo "Next steps:"
echo "  1. Run web interface:"
echo "     streamlit run app.py"
echo ""
echo "  2. Upload $OWL_FILE via the web UI"
echo ""
echo "  3. Chat with your ontology!"
