"""
SPARQL-VI: Vietnamese SPARQL Translator
Translates between SPARQL and Vietnamese keywords to ensure LLM relies on context
"""

import re
from typing import Dict, Tuple

class SPARQLVITranslator:
    """Translator between SPARQL and SPARQL-VI (Vietnamese)"""
    
    # Keyword mapping: SPARQL -> Vietnamese
    SPARQL_TO_VI = {
        # Query types
        "SELECT": "CHONJ",
        "CONSTRUCT": "XAY_DUNGWJ",
        "ASK": "HOI",
        "DESCRIBE": "MO_TAR",
        
        # Clauses
        "WHERE": "NOII_MA",
        "FROM": "TU",
        "FILTER": "LOCJ",
        "OPTIONAL": "TUYJ_CHON",
        "UNION": "HOP",
        "MINUS": "TRU",
        "GROUP BY": "NHOM_THEO",
        "HAVING": "CO",
        "ORDER BY": "SAP_XXEP_THEO",
        "LIMIT": "GIOI_HHAN",
        "OFFSET": "DICCH_CHUYEN",
        
        # Modifiers
        "PREFIX": "TIENN_TO",
        "BASE": "CO_SO",
        "DISTINCT": "PHAN_BIET",
        "REDUCED": "GIAM",
        "AS": "GOI_LLA",
        
        # Aggregate functions
        "COUNT": "DEM",
        "SUM": "TONG",
        "AVG": "TRUNG_BINH",
        "MIN": "NHO_NHAT",
        "MAX": "LON_NHAT",
        "SAMPLE": "MAU",
        "GROUP_CONCAT": "NOI_NHOM",
        
        # Operators
        "AND": "VA",
        "OR": "HOAC",
        "NOT": "KHONG",
        
        # Built-in functions
        "BOUND": "TON_TAI",
        "isIRI": "LA_IRI",
        "isURI": "LA_URI",
        "isBLANK": "LA_TRONG",
        "isLITERAL": "LA_LITERAL",
        "isNUMERIC": "LA_SO",
        "LANG": "NGON_NGU",
        "DATATYPE": "KIEU_DU_LIEU",
        "STR": "CHUOI",
        "STRLEN": "DO_DAI_CHUOI",
        "SUBSTR": "CHUOI_CON",
        "UCASE": "CHU_HOA",
        "LCASE": "CHU_THUONG",
        "CONCAT": "NOI",
        "CONTAINS": "CHUA",
        "STRSTARTS": "BAT_DAU_VOI",
        "STRENDS": "KET_THUC_VOI",
        "REGEX": "BIEU_THUC_CHINH_QUY",
        "REPLACE": "THAY_THE",
        
        # RDF terms
        "a": "la",  # rdf:type shorthand
        
        # Graph patterns
        "GRAPH": "DO_THI",
        "SERVICE": "DICH_VU",
        "BIND": "RANG_BUOC",
        "VALUES": "GIA_TRI",
        
        # Solution modifiers
        "ASC": "TANG",
        "DESC": "GIAM",
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
