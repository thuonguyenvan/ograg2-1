#!/usr/bin/env python3
"""
Test GO Query Engine with sample questions
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from query_engine.go_query_engine import GOQueryEngine


def main():
    print("\n" + "="*80)
    print("GO QUERY ENGINE - TEST")
    print("="*80 + "\n")
    
    # Initialize engine
    engine = GOQueryEngine(
        ontology_dir="data/kg/go/ontology",
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        llm_model="gpt-4",
        top_k=5,
        hierarchical_depth=2
    )
    
    # Sample questions
    questions = [
        {
            "question": "What is DNA repair?",
            "expected_go": "GO:0006281"
        },
        {
            "question": "How does cell division work?",
            "expected_go": "GO:0051301"
        },
        {
            "question": "What is protein phosphorylation?",
            "expected_go": "GO:0006468"
        },
        {
            "question": "What processes are involved in cellular respiration?",
            "expected_go": "GO:0045333"
        },
        {
            "question": "Explain the immune response process.",
            "expected_go": "GO:0006955"
        }
    ]
    
    # Test each question
    for i, q_data in enumerate(questions, 1):
        question = q_data['question']
        expected_go = q_data['expected_go']
        
        print(f"\n{'='*80}")
        print(f"Question {i}/{len(questions)}")
        print(f"{'='*80}")
        print(f"Q: {question}")
        print(f"Expected GO: {expected_go}\n")
        
        # Query with verbose mode
        result = engine.query(question, return_context=True, verbose=True)
        
        # Check if expected GO was retrieved
        retrieved_gos = [f['fact'].get('GO id') for f in result['retrieved_facts']]
        if expected_go in retrieved_gos:
            print(f"✓ Expected GO term {expected_go} was retrieved!")
        else:
            print(f"✗ Expected GO term {expected_go} NOT in top results")
            print(f"  Retrieved: {retrieved_gos[:3]}")
        
        print(f"\nAnswer:")
        print("-" * 80)
        print(result['answer'])
        print("-" * 80)
        
        if i < len(questions):
            input("\nPress Enter for next question...")
    
    print(f"\n{'='*80}")
    print("✓ All tests completed!")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
