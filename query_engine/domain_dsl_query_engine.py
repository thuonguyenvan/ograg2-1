from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from llama_index.core.base.response.schema import Response
from llama_index.core.retrievers import VectorIndexRetriever

from query_engine.ontograph_query_engine import OntoHyperGraphQueryEngine
from utils import (
    create_or_load_index,
    get_documents,
)


DEFAULT_PROMPT_TEMPLATE = """You are an expert assistant that converts natural language requests into a domain-specific DSL.

Context about the business domain ontology:
{domain_context}

Context about the DSL grammar and valid constructs:
{dsl_context}

Additional rules and constraints (if any):
{rules}

Follow these instructions:
- Analyse the user request carefully.
- Use ONLY information present in the provided ontology context.
- Produce a syntactically correct DSL command that complies with the grammar.
- Do not invent functions or relations that are not present in the DSL context.
- If multiple options are possible, choose the one that best satisfies the rules.
- {output_format}

User request:
{user_query}

Return only the DSL command. If you cannot produce a valid command, reply with a short explanation starting with '#error'.
"""


def _format_context(context: Any) -> str:
    """Convert retrieved context (dict / list / str) into readable text."""
    if context is None:
        return "None"
    if isinstance(context, str):
        return context
    if isinstance(context, dict):
        return "\n".join(f"- {k}: {v}" for k, v in context.items())
    if isinstance(context, list):
        formatted_items: List[str] = []
        for item in context:
            formatted_items.append(_format_context(item))
        return "\n".join(formatted_items)
    try:
        return json.dumps(context, ensure_ascii=False, indent=2)
    except TypeError:
        return str(context)


@dataclass
class DomainDSLValidationResult:
    is_valid: bool
    errors: List[str]


class DomainDSLQueryEngine:
    """Combine domain ontology retrieval + DSL grammar retrieval to generate DSL commands."""

    def __init__(
        self,
        llm,
        domain_engine: OntoHyperGraphQueryEngine,
        dsl_engine: OntoHyperGraphQueryEngine,
        prompt_template: str = DEFAULT_PROMPT_TEMPLATE,
        output_format: str = "Return a single DSL command.",
        max_tokens: int = 768,
        validation_rules: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._llm = llm
        self._domain_engine = domain_engine
        self._dsl_engine = dsl_engine
        self._prompt_template = prompt_template
        self._output_format = output_format
        self._max_tokens = max_tokens
        self._validation_rules = validation_rules or {}

    @classmethod
    def from_config(
        cls,
        *,
        llm,
        embed_model,
        domain_config,
        dsl_config,
        service_context=None,
        prompt_template: Optional[str] = None,
        output_format: Optional[str] = None,
        max_tokens: Optional[int] = None,
        validation_rules: Optional[Dict[str, Any]] = None,
    ) -> "DomainDSLQueryEngine":
        domain_vector = _maybe_build_vector_retriever(
            dataset_config=domain_config,
            embed_model=embed_model,
            service_context=service_context,
        )
        dsl_vector = _maybe_build_vector_retriever(
            dataset_config=dsl_config,
            embed_model=embed_model,
            service_context=service_context,
        )

        domain_engine = OntoHyperGraphQueryEngine.from_ontology_path(
            ontology_nodes_path=domain_config.kg_storage_path,
            llm=llm,
            embed_model=embed_model,
            vector_retriever=domain_vector,
        )
        dsl_engine = OntoHyperGraphQueryEngine.from_ontology_path(
            ontology_nodes_path=dsl_config.kg_storage_path,
            llm=llm,
            embed_model=embed_model,
            vector_retriever=dsl_vector,
        )

        return cls(
            llm=llm,
            domain_engine=domain_engine,
            dsl_engine=dsl_engine,
            prompt_template=prompt_template or DEFAULT_PROMPT_TEMPLATE,
            output_format=output_format or "Return a single DSL command.",
            max_tokens=max_tokens or 768,
            validation_rules=validation_rules,
        )

    def query(
        self,
        query_str: str,
        *,
        domain_top_k: int = 5,
        domain_nodes_top_k: int = 25,
        dsl_top_k: int = 5,
        dsl_nodes_top_k: int = 25,
        return_context: bool = False,
        rules: Optional[List[str]] = None,
        **kwargs: Any,
    ):
        domain_nodes, domain_context = self._domain_engine.retrieve_context(
            query_str,
            top_k=domain_top_k,
            nodes_top_k=domain_nodes_top_k,
        )
        dsl_nodes, dsl_context = self._dsl_engine.retrieve_context(
            query_str,
            top_k=dsl_top_k,
            nodes_top_k=dsl_nodes_top_k,
        )

        formatted_domain_context = _format_context(domain_context)
        formatted_dsl_context = _format_context(dsl_context)

        prompt = self._prompt_template.format(
            domain_context=formatted_domain_context,
            dsl_context=formatted_dsl_context,
            rules=_format_context(rules) if rules else "None",
            output_format=self._output_format,
            user_query=query_str,
        )

        response = self._llm.invoke(prompt, max_tokens=self._max_tokens)
        response_text = getattr(response, "content", response)

        validation = self._validate_output(response_text)
        response_obj = Response(response_text, extra_info={"validation": validation.__dict__})

        if return_context:
            joined_context = {
                "domain_context": formatted_domain_context,
                "dsl_context": formatted_dsl_context,
                "validation": validation.__dict__,
            }
            return response_obj, joined_context

        return response_obj

    def _validate_output(self, response_text: str) -> DomainDSLValidationResult:
        errors: List[str] = []
        cleaned = (response_text or "").strip()

        if not cleaned:
            errors.append("Empty response produced by the model.")

        keywords: List[str] = self._validation_rules.get("require_keywords", [])
        for keyword in keywords:
            if keyword not in cleaned:
                errors.append(f"Missing required keyword: {keyword}")

        disallowed: List[str] = self._validation_rules.get("forbid_keywords", [])
        for keyword in disallowed:
            if keyword in cleaned:
                errors.append(f"Disallowed keyword present: {keyword}")

        return DomainDSLValidationResult(is_valid=len(errors) == 0, errors=errors)


def _maybe_build_vector_retriever(
    *,
    dataset_config,
    embed_model,
    service_context=None,
) -> Optional[VectorIndexRetriever]:
    """Build a vector retriever when configuration requests it."""
    use_vector_index = bool(getattr(dataset_config, "use_vector_index", False))
    index_dir = getattr(dataset_config, "index_dir", None)
    documents_dir = getattr(dataset_config, "documents_dir", None)

    if not use_vector_index or not index_dir or not service_context:
        return None

    documents = get_documents(
        documents_dir,
        subdir=getattr(dataset_config, "subdir", False),
        smart_pdf=getattr(dataset_config, "smart_pdf", True),
        full_text=getattr(dataset_config, "full_text", False),
    )

    vector_index = create_or_load_index(
        index_directory=index_dir,
        service_context=service_context,
        documents=documents,
    )

    return VectorIndexRetriever(index=vector_index)

