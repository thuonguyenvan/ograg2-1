"""
Convert the extended domain & DSL ontologies into JSON-LD artifacts for OG-RAG.

Run this script once to populate:
  data/kg/domain_extended/ontology/domain_extended.jsonld
  data/kg/dsl_extended/ontology/dsl_extended.jsonld
  data/rules/dsl_rules.txt
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


WORKSPACE_ROOT = Path(__file__).parent
DATA_DIR = WORKSPACE_ROOT / "data"

DOMAIN_SOURCE = WORKSPACE_ROOT / "domain_ontology_extended.json"
DSL_SOURCE = WORKSPACE_ROOT / "dsl_ontology_extended.json"

DOMAIN_TARGET_DIR = DATA_DIR / "kg" / "domain_extended" / "ontology"
DSL_TARGET_DIR = DATA_DIR / "kg" / "dsl_extended" / "ontology"
RULES_DIR = DATA_DIR / "rules"


def _load_json(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as fp:
        return json.load(fp)


def _build_domain_jsonld(domain_data: Dict) -> Dict:
    classes: List[Dict] = domain_data.get("classes", [])
    properties: List[Dict] = domain_data.get("properties", [])

    props_by_domain: Dict[str, List[Dict]] = {}
    for prop in properties:
        props_by_domain.setdefault(prop.get("domain"), []).append(
            {
                "property": prop.get("name"),
                "label": prop.get("label"),
                "description": prop.get("description"),
                "range": prop.get("range"),
                "example_triples": prop.get("example_triples", []),
            }
        )

    graph: List[Dict] = []

    for cls in classes:
        graph.append(
            {
                "@type": "DomainClass",
                "identifier": cls.get("name"),
                "label": cls.get("label"),
                "description": cls.get("description", ""),
                "subclass_of": cls.get("subclass_of"),
                "example_individuals": cls.get("example_individuals", []),
                "related_properties": props_by_domain.get(cls.get("name"), []),
            }
        )

    for prop in properties:
        graph.append(
            {
                "@type": "DomainProperty",
                "identifier": prop.get("name"),
                "label": prop.get("label"),
                "description": prop.get("description"),
                "domain": prop.get("domain"),
                "range": prop.get("range"),
                "example_triples": prop.get("example_triples", []),
            }
        )

    return {"@graph": graph}


def _build_dsl_jsonld(dsl_data: Dict) -> Dict:
    graph: List[Dict] = []

    for fn in dsl_data.get("dsl_functions", []):
        graph.append(
            {
                "@type": "DSLFunction",
                "identifier": fn.get("id"),
                "keyword": fn.get("keyword"),
                "label": fn.get("label"),
                "kind": fn.get("kind"),
                "description": fn.get("description"),
                "syntax": fn.get("syntax"),
                "example_dsl": fn.get("example_dsl"),
            }
        )

    for clause in dsl_data.get("dsl_clauses", []):
        graph.append(
            {
                "@type": "DSLClause",
                "identifier": clause.get("id"),
                "keyword": clause.get("keyword"),
                "label": clause.get("label"),
                "kind": clause.get("kind"),
                "description": clause.get("description"),
                "syntax": clause.get("syntax"),
                "example_dsl": clause.get("example_dsl"),
            }
        )

    for modifier in dsl_data.get("dsl_modifiers", []):
        graph.append(
            {
                "@type": "DSLModifier",
                "identifier": modifier.get("id"),
                "keyword": modifier.get("keyword"),
                "label": modifier.get("label"),
                "kind": modifier.get("kind"),
                "description": modifier.get("description"),
                "syntax": modifier.get("syntax"),
                "example_dsl": modifier.get("example_dsl"),
            }
        )

    for query_id, spec in dsl_data.get("dsl_query_types", {}).items():
        components: List[Dict] = []
        for comp_name, comp_spec in spec.get("components", {}).items():
            item = {"name": comp_name}
            item.update(comp_spec)
            components.append(item)

        graph.append(
            {
                "@type": "DSLQueryType",
                "identifier": query_id,
                "kind": spec.get("kind"),
                "label": spec.get("label"),
                "description": spec.get("description"),
                "order": spec.get("order", []),
                "components": components,
                "example_dsl": spec.get("example_dsl"),
            }
        )

    triple_pattern_spec = dsl_data.get("triple_pattern_spec")
    if triple_pattern_spec:
        graph.append(
            {
                "@type": "TriplePatternSpec",
                "description": triple_pattern_spec.get("description"),
                "syntax": triple_pattern_spec.get("syntax"),
            }
        )

    return {"@graph": graph}


def _write_jsonld(target_dir: Path, filename: str, payload: Dict) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    with (target_dir / filename).open("w", encoding="utf-8") as fp:
        json.dump(payload, fp, ensure_ascii=False, indent=2)


def _write_rules_file() -> None:
    RULES_DIR.mkdir(parents=True, exist_ok=True)
    rules_content = "\n".join(
        [
            "# DSL usage guidelines derived from the ontology",
            "- Respect the component order defined in each DSL query type.",
            "- Always include mandatory keywords/components marked as required.",
            "- When using aggregate functions (DEMM_JJ, TONGG_WW, TRUNGG_BINH_PP, ...), add NHOMM_THEO_YY unless the ontology marks it optional.",
            "- LOCJ_RR filters should rely on properties defined in the domain ontology.",
            "- Modifiers (SAP_XXEP_THEO_KK, GIOI_HHAN_RR, DICCH_CHUYEN_WW, KHAC_NHAU_PP) must be listed as allowed modifiers for the chosen query type.",
        ]
    )
    (RULES_DIR / "dsl_rules.txt").write_text(rules_content + "\n", encoding="utf-8")


def main() -> None:
    if not DOMAIN_SOURCE.exists():
        raise FileNotFoundError(f"Missing domain ontology: {DOMAIN_SOURCE}")
    if not DSL_SOURCE.exists():
        raise FileNotFoundError(f"Missing DSL ontology: {DSL_SOURCE}")

    domain_jsonld = _build_domain_jsonld(_load_json(DOMAIN_SOURCE))
    dsl_jsonld = _build_dsl_jsonld(_load_json(DSL_SOURCE))

    _write_jsonld(DOMAIN_TARGET_DIR, "domain_extended.jsonld", domain_jsonld)
    _write_jsonld(DSL_TARGET_DIR, "dsl_extended.jsonld", dsl_jsonld)
    _write_rules_file()

    print("Generated OG-RAG artifacts from the extended ontologies:")
    print(f"- Domain JSON-LD: {DOMAIN_TARGET_DIR / 'domain_extended.jsonld'}")
    print(f"- DSL JSON-LD:    {DSL_TARGET_DIR / 'dsl_extended.jsonld'}")
    print(f"- Rules file:     {RULES_DIR / 'dsl_rules.txt'}")
    print("\nRun: python query_llm.py --config_file configs/rag/config_domain_dsl.yaml")
    print("Then provide natural language instructions to obtain DSL outputs.")


if __name__ == "__main__":
    main()

