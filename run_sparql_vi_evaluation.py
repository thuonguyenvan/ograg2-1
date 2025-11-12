"""
Run Full Evaluation of SPARQL-VI Query Generation
Compare: Baseline, Few-shot, OG-RAG methods
"""

import os
import sys
import json
import importlib.util
from pathlib import Path
from datetime import datetime

# Load engine module directly
current_dir = Path(__file__).parent
spec = importlib.util.spec_from_file_location(
    "sparql_vi_ograg_engine",
    current_dir / "query_engine" / "sparql_vi_ograg_engine.py"
)
engine_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine_module)
SPARQLVIQueryEngine = engine_module.SPARQLVIQueryEngine


def run_evaluation(api_key: str, num_test_cases: int = None):
    """Run full evaluation"""
    
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║          SPARQL-VI Query Generation - Full Evaluation             ║
║          Comparing: Baseline vs Few-shot vs OG-RAG                ║
╚═══════════════════════════════════════════════════════════════════╝
""")
    
    # Initialize engine
    engine = SPARQLVIQueryEngine(
        facts_path="data/dsl/sparql_vi/hypergraph_facts.json",
        test_cases_path="data/dsl/sparql_vi/test_cases.json",
        llm_api_key=api_key
    )
    
    # Run evaluations for all methods
    methods = ['baseline', 'fewshot', 'ograg']
    all_results = {}
    
    for method in methods:
        print(f"\n{'='*70}")
        print(f"Running Evaluation: {method.upper()}")
        print(f"{'='*70}\n")
        
        results = engine.evaluate_all(method=method, limit=num_test_cases)
        all_results[method] = results
        
        print(f"\n✓ {method.upper()} completed")
        print(f"   Syntax Accuracy: {results['syntax_accuracy']:.1%}")
        print(f"   Exact Match: {results['exact_match_accuracy']:.1%}\n")
    
    # Save results
    output_dir = Path("results/sparql_vi_evaluation")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save detailed results
    output_json = output_dir / f"evaluation_{timestamp}.json"
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved detailed results: {output_json}")
    
    # Save summary
    summary = {
        'timestamp': timestamp,
        'num_test_cases': all_results['baseline']['total_cases'],
        'methods': {}
    }
    
    for method, results in all_results.items():
        summary['methods'][method] = {
            'syntax_accuracy': results['syntax_accuracy'],
            'exact_match_accuracy': results['exact_match_accuracy']
        }
    
    output_summary = output_dir / f"summary_{timestamp}.json"
    with open(output_summary, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    print(f"✓ Saved summary: {output_summary}")
    
    # Print final comparison
    print(f"\n{'='*70}")
    print("FINAL COMPARISON")
    print(f"{'='*70}\n")
    print(f"{'Method':<15} {'Syntax Accuracy':<20} {'Exact Match':<20}")
    print("-" * 70)
    
    for method in methods:
        results = all_results[method]
        syntax_acc = f"{results['syntax_accuracy']:.1%}"
        exact_match = f"{results['exact_match_accuracy']:.1%}"
        print(f"{method.upper():<15} {syntax_acc:<20} {exact_match:<20}")
    
    # Calculate improvements
    baseline_exact = all_results['baseline']['exact_match_accuracy']
    ograg_exact = all_results['ograg']['exact_match_accuracy']
    
    if baseline_exact > 0:
        improvement = ((ograg_exact - baseline_exact) / baseline_exact) * 100
        print(f"\n{'='*70}")
        print(f"OG-RAG Improvement over Baseline: {improvement:+.1f}%")
        print(f"{'='*70}\n")


if __name__ == "__main__":
    api_key = os.environ.get('GROQ_API_KEY')
    
    if not api_key:
        print("""
ERROR: GROQ_API_KEY not set

Please set your Groq API key:
  export GROQ_API_KEY=gsk_...

Or in Python:
  import os
  os.environ['GROQ_API_KEY'] = 'gsk_...'
""")
        sys.exit(1)
    
    # Parse arguments
    num_cases = int(sys.argv[1]) if len(sys.argv) > 1 else None
    
    if num_cases:
        print(f"\n📊 Running evaluation on {num_cases} test cases...")
    else:
        print(f"\n📊 Running evaluation on all test cases...")
    
    run_evaluation(api_key, num_cases)
