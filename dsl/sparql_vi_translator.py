"""
SPARQL-VI: Vietnamese SPARQL Translator
Translates between SPARQL and Vietnamese keywords to ensure LLM relies on context
"""

import re
from typing import Dict, Tuple

class SPARQLVITranslator:
    """Translator between SPARQL and SPARQL-VI (Vietnamese)"""
    
    # Keyword mapping: SPARQL -> Vietnamese (obfuscated with noise characters)
    # Pattern: Add random characters (J, W, R, II, XX, YY, ZZ, KK, PP, QQ) to make it unpredictable
    SPARQL_TO_VI = {
        # Query types - Core commands with strong obfuscation
        "SELECT": "CHONJ_KW",
        "CONSTRUCT": "XAY_DUNGWJ",
        "ASK": "HOIQQ_YZ",
        "DESCRIBE": "MO_TAR_PP",
        
        # Clauses - Pattern variation to prevent pattern recognition
        "WHERE": "NOII_MA_KK",
        "FROM": "TU_XZ",
        "FILTER": "LOCJ_RR",
        "OPTIONAL": "TUYJ_CHON_PP",
        "UNION": "HOPP_QQ",
        "MINUS": "TRUU_WJ",
        "GROUP BY": "NHOMM_THEO_YY",
        "HAVING": "COO_ZZ",
        "ORDER BY": "SAP_XXEP_THEO_KK",
        "LIMIT": "GIOI_HHAN_RR",
        "OFFSET": "DICCH_CHUYEN_WW",
        
        # Modifiers - Mixed patterns
        "PREFIX": "TIENN_TO_QQ",
        "BASE": "CO_SOO_JJ",
        "DISTINCT": "PHANN_BIET_PP",
        "REDUCED": "GIAMM_RR",
        "AS": "GOI_LLA_KK",
        
        # Aggregate functions - Double consonants + noise
        "COUNT": "DEMM_JJ",
        "SUM": "TONGG_WW",
        "AVG": "TRUNGG_BINH_PP",
        "MIN": "NHOO_NHAT_QQ",
        "MAX": "LONN_NHAT_RR",
        "SAMPLE": "MAUU_ZZ",
        "GROUP_CONCAT": "NOII_NHOM_KK",
        
        # Operators - Short but obfuscated
        "AND": "VAA_JJ",
        "OR": "HOACC_WW",
        "NOT": "KHONGG_RR",
        
        # Built-in functions - Systematic noise injection
        "BOUND": "TONN_TAI_PP",
        "isIRI": "LAA_IRI_QQ",
        "isURI": "LAA_URI_RR",
        "isBLANK": "LAA_TRONG_KK",
        "isLITERAL": "LAA_LITERAL_WW",
        "isNUMERIC": "LAA_SO_JJ",
        "LANG": "NGONN_NGU_PP",
        "DATATYPE": "KIEUU_DU_LIEU_QQ",
        "STR": "CHUOII_RR",
        "STRLEN": "DOO_DAI_CHUOI_KK",
        "SUBSTR": "CHUOII_CON_WW",
        "UCASE": "CHUU_HOA_JJ",
        "LCASE": "CHUU_THUONG_PP",
        "CONCAT": "NOII_QQ",
        "CONTAINS": "CHUAA_RR",
        "STRSTARTS": "BATT_DAU_VOI_KK",
        "STRENDS": "KETT_THUC_VOI_WW",
        "REGEX": "BIEUU_THUC_CHINH_QUY_JJ",
        "REPLACE": "THAYY_THE_PP",
        
        # RDF terms - Even single letter gets noise
        "a": "laa_jj",  # rdf:type shorthand
        
        # Graph patterns - High-level constructs
        "GRAPH": "DOO_THI_RR",
        "SERVICE": "DICHH_VU_KK",
        "BIND": "RANGG_BUOC_WW",
        "VALUES": "GIAA_TRI_QQ",
        
        # Solution modifiers - Sorting operations
        "ASC": "TANGG_JJ",
        "DESC": "GIAMM_WW",
    }
    
    # Reverse mapping
    VI_TO_SPARQL = {v: k for k, v in SPARQL_TO_VI.items()}
    
    def __init__(self):
        # Compile regex patterns for efficient replacement
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for keyword replacement"""
        # SPARQL -> VI patterns (must match whole words)
        sparql_pattern = '|'.join(
            re.escape(key) for key in sorted(self.SPARQL_TO_VI.keys(), key=len, reverse=True)
        )
        self.sparql_to_vi_pattern = re.compile(r'\b(' + sparql_pattern + r')\b', re.IGNORECASE)
        
        # VI -> SPARQL patterns
        vi_pattern = '|'.join(
            re.escape(key) for key in sorted(self.VI_TO_SPARQL.keys(), key=len, reverse=True)
        )
        self.vi_to_sparql_pattern = re.compile(r'\b(' + vi_pattern + r')\b', re.IGNORECASE)
    
    def sparql_to_vi(self, sparql_query: str) -> str:
        """
        Convert SPARQL query to SPARQL-VI (Vietnamese keywords)
        
        Args:
            sparql_query: Original SPARQL query
            
        Returns:
            SPARQL-VI query with Vietnamese keywords
        """
        def replace_keyword(match):
            keyword = match.group(1)
            # Preserve case (uppercase -> uppercase)
            vi_keyword = self.SPARQL_TO_VI.get(keyword.upper(), keyword)
            return vi_keyword if keyword.isupper() else vi_keyword.lower()
        
        return self.sparql_to_vi_pattern.sub(replace_keyword, sparql_query)
    
    def vi_to_sparql(self, vi_query: str) -> str:
        """
        Convert SPARQL-VI query back to standard SPARQL
        
        Args:
            vi_query: SPARQL-VI query with Vietnamese keywords
            
        Returns:
            Standard SPARQL query
        """
        def replace_keyword(match):
            vi_keyword = match.group(1)
            sparql_keyword = self.VI_TO_SPARQL.get(vi_keyword.upper(), vi_keyword)
            return sparql_keyword if vi_keyword.isupper() else sparql_keyword.lower()
        
        return self.vi_to_sparql_pattern.sub(replace_keyword, vi_query)
    
    def validate_vi_query(self, vi_query: str) -> Tuple[bool, str]:
        """
        Validate SPARQL-VI query by converting to SPARQL and checking syntax
        
        Args:
            vi_query: SPARQL-VI query to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Convert to SPARQL
            sparql_query = self.vi_to_sparql(vi_query)
            
            # Basic syntax validation (can be enhanced with rdflib)
            if not any(keyword in sparql_query.upper() for keyword in ['SELECT', 'CONSTRUCT', 'ASK', 'DESCRIBE']):
                return False, "Missing query type (CHON/XAY_DUNG/HOI/MO_TA)"
            
            if 'WHERE' not in sparql_query.upper() and 'SELECT' in sparql_query.upper():
                return False, "Missing WHERE clause (NOI_MA)"
            
            # Check balanced braces
            if sparql_query.count('{') != sparql_query.count('}'):
                return False, "Unbalanced braces"
            
            return True, sparql_query
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def get_keyword_mapping(self) -> Dict[str, str]:
        """Get the complete SPARQL -> Vietnamese keyword mapping"""
        return self.SPARQL_TO_VI.copy()


# Example usage
if __name__ == "__main__":
    translator = SPARQLVITranslator()
    
    # Example 1: Simple query
    sparql_query = """
    PREFIX ex: <http://example.org/>
    SELECT ?name
    WHERE {
        ?person a ex:Person ;
                ex:hasName ?name .
        FILTER(?age > 18)
    }
    """
    
    print("=== Original SPARQL ===")
    print(sparql_query)
    
    vi_query = translator.sparql_to_vi(sparql_query)
    print("\n=== SPARQL-VI ===")
    print(vi_query)
    
    back_to_sparql = translator.vi_to_sparql(vi_query)
    print("\n=== Back to SPARQL ===")
    print(back_to_sparql)
    
    # Example 2: Complex query
    complex_sparql = """
    PREFIX ex: <http://example.org/>
    SELECT DISTINCT ?person (COUNT(?book) as ?count)
    WHERE {
        ?person rdf:type ex:Person ;
                ex:hasAge ?age ;
                ex:borrowed ?book .
        FILTER(?age > 18)
        OPTIONAL { ?person ex:email ?email }
    }
    GROUP BY ?person
    HAVING (COUNT(?book) > 5)
    ORDER BY DESC(?count)
    LIMIT 10
    """
    
    print("\n\n=== Complex SPARQL ===")
    print(complex_sparql)
    
    complex_vi = translator.sparql_to_vi(complex_sparql)
    print("\n=== Complex SPARQL-VI ===")
    print(complex_vi)
    
    # Validate
    is_valid, result = translator.validate_vi_query(complex_vi)
    print(f"\n=== Validation ===")
    print(f"Valid: {is_valid}")
    if is_valid:
        print("Converted back successfully!")
