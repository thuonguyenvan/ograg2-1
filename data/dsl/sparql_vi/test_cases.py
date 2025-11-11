"""
SPARQL-VI Test Dataset
30 test cases from simple to complex
"""

import json

TEST_CASES = [
    # ============================================
    # LEVEL 1: Simple CHONJ_KW queries (10 cases)
    # ============================================
    {
        "id": 1,
        "level": "simple",
        "category": "basic_select",
        "nl_query": "Tìm tên của tất cả người dùng",
        "expected_vi": "CHONJ_KW ?ten NOII_MA_KK { ?nguoi :coTen ?ten }",
        "expected_sparql": "SELECT ?name WHERE { ?person :hasName ?name }",
        "concepts": ["CHONJ_KW", "NOII_MA_KK", "triple_pattern"],
        "validation": {"syntax_valid": True}
    },
    {
        "id": 2,
        "level": "simple",
        "category": "basic_select",
        "nl_query": "Lấy danh sách email của người dùng",
        "expected_vi": "CHONJ_KW ?email NOII_MA_KK { ?nguoi :coEmail ?email }",
        "expected_sparql": "SELECT ?email WHERE { ?person :hasEmail ?email }",
        "concepts": ["CHONJ_KW", "NOII_MA_KK"],
        "validation": {"syntax_valid": True}
    },
    {
        "id": 3,
        "level": "simple",
        "category": "filter",
        "nl_query": "Tìm người có tuổi lớn hơn 18",
        "expected_vi": "CHONJ_KW ?nguoi NOII_MA_KK { ?nguoi :coTuoi ?tuoi . LOCJ_RR(?tuoi > 18) }",
        "expected_sparql": "SELECT ?person WHERE { ?person :hasAge ?age . FILTER(?age > 18) }",
        "concepts": ["CHONJ_KW", "NOII_MA_KK", "LOCJ_RR", "comparison"],
        "validation": {"syntax_valid": True}
    },
    {
        "id": 4,
        "level": "simple",
        "category": "filter",
        "nl_query": "Lấy sách có giá dưới 100000",
        "expected_vi": "CHONJ_KW ?sach ?gia NOII_MA_KK { ?sach :coGia ?gia . LOCJ_RR(?gia < 100000) }",
        "expected_sparql": "SELECT ?book ?price WHERE { ?book :hasPrice ?price . FILTER(?price < 100000) }",
        "concepts": ["CHONJ_KW", "NOII_MA_KK", "LOCJ_RR"],
        "validation": {"syntax_valid": True}
    },
    {
        "id": 5,
        "level": "simple",
        "category": "multiple_patterns",
        "nl_query": "Tìm tên và email của người dùng",
        "expected_vi": "CHONJ_KW ?ten ?email NOII_MA_KK { ?nguoi :coTen ?ten ; :coEmail ?email }",
        "expected_sparql": "SELECT ?name ?email WHERE { ?person :hasName ?name ; :hasEmail ?email }",
        "concepts": ["CHONJ_KW", "NOII_MA_KK", "property_path"],
        "validation": {"syntax_valid": True}
    },
    {
        "id": 6,
        "level": "simple",
        "category": "optional",
        "nl_query": "Lấy tên người dùng và số điện thoại nếu có",
        "expected_vi": "CHONJ_KW ?ten ?sdt NOII_MA_KK { ?nguoi :coTen ?ten . TUYJ_CHON_PP { ?nguoi :coDienThoai ?sdt } }",
        "expected_sparql": "SELECT ?name ?phone WHERE { ?person :hasName ?name . OPTIONAL { ?person :hasPhone ?phone } }",
        "concepts": ["CHONJ_KW", "NOII_MA_KK", "TUYJ_CHON_PP"],
        "validation": {"syntax_valid": True}
    },
    {
        "id": 7,
        "level": "simple",
        "category": "distinct",
        "nl_query": "Lấy danh sách các thành phố (không trùng lặp)",
        "expected_vi": "CHONJ_KW PHANN_BIET_PP ?thanh_pho NOII_MA_KK { ?nguoi :song_tai ?thanh_pho }",
        "expected_sparql": "SELECT DISTINCT ?city WHERE { ?person :livesIn ?city }",
        "concepts": ["CHONJ_KW", "PHANN_BIET_PP", "NOII_MA_KK"],
        "validation": {"syntax_valid": True}
    },
    {
        "id": 8,
        "level": "simple",
        "category": "limit",
        "nl_query": "Lấy 10 người dùng đầu tiên",
        "expected_vi": "CHONJ_KW ?nguoi NOII_MA_KK { ?nguoi :coTen ?ten } GIOI_HHAN_RR 10",
        "expected_sparql": "SELECT ?person WHERE { ?person :hasName ?name } LIMIT 10",
        "concepts": ["CHONJ_KW", "NOII_MA_KK", "GIOI_HHAN_RR"],
        "validation": {"syntax_valid": True}
    },
    {
        "id": 9,
        "level": "simple",
        "category": "order",
        "nl_query": "Sắp xếp người dùng theo tuổi tăng dần",
        "expected_vi": "CHONJ_KW ?nguoi ?tuoi NOII_MA_KK { ?nguoi :coTuoi ?tuoi } SAP_XXEP_THEO_KK TANGG_JJ(?tuoi)",
        "expected_sparql": "SELECT ?person ?age WHERE { ?person :hasAge ?age } ORDER BY ASC(?age)",
        "concepts": ["CHONJ_KW", "NOII_MA_KK", "SAP_XXEP_THEO_KK", "TANGG_JJ"],
        "validation": {"syntax_valid": True}
    },
    {
        "id": 10,
        "level": "simple",
        "category": "ask",
        "nl_query": "Có người nào trên 100 tuổi không?",
        "expected_vi": "HOIQQ_YZ NOII_MA_KK { ?nguoi :coTuoi ?tuoi . LOCJ_RR(?tuoi > 100) }",
        "expected_sparql": "ASK WHERE { ?person :hasAge ?age . FILTER(?age > 100) }",
        "concepts": ["HOIQQ_YZ", "NOII_MA_KK", "LOCJ_RR"],
        "validation": {"syntax_valid": True}
    },
    
    # ============================================
    # LEVEL 2: Medium complexity (10 cases)
    # ============================================
    {
        "id": 11,
        "level": "medium",
        "category": "aggregation",
        "nl_query": "Đếm số người ở mỗi thành phố",
        "expected_vi": "CHONJ_KW ?thanh_pho (DEMM_JJ(?nguoi) GOI_LLA_KK ?so_luong) NOII_MA_KK { ?nguoi :song_tai ?thanh_pho } NHOMM_THEO_YY ?thanh_pho",
        "expected_sparql": "SELECT ?city (COUNT(?person) AS ?count) WHERE { ?person :livesIn ?city } GROUP BY ?city",
        "concepts": ["CHONJ_KW", "NOII_MA_KK", "DEMM_JJ", "GOI_LLA_KK", "NHOMM_THEO_YY"],
        "validation": {"syntax_valid": True, "requires_groupby": True}
    },
    {
        "id": 12,
        "level": "medium",
        "category": "aggregation",
        "nl_query": "Tính tổng giá trị đơn hàng theo khách hàng",
        "expected_vi": "CHONJ_KW ?khach (TONGG_WW(?gia) GOI_LLA_KK ?tong) NOII_MA_KK { ?don :cua_khach ?khach ; :co_gia ?gia } NHOMM_THEO_YY ?khach",
        "expected_sparql": "SELECT ?customer (SUM(?price) AS ?total) WHERE { ?order :ofCustomer ?customer ; :hasPrice ?price } GROUP BY ?customer",
        "concepts": ["CHONJ_KW", "NOII_MA_KK", "TONGG_WW", "NHOMM_THEO_YY"],
        "validation": {"syntax_valid": True, "requires_groupby": True}
    },
    {
        "id": 13,
        "level": "medium",
        "category": "having",
        "nl_query": "Tìm thành phố có hơn 5 người",
        "expected_vi": "CHONJ_KW ?thanh_pho (DEMM_JJ(?nguoi) GOI_LLA_KK ?so) NOII_MA_KK { ?nguoi :song_tai ?thanh_pho } NHOMM_THEO_YY ?thanh_pho COO_ZZ (DEMM_JJ(?nguoi) > 5)",
        "expected_sparql": "SELECT ?city (COUNT(?person) AS ?count) WHERE { ?person :livesIn ?city } GROUP BY ?city HAVING (COUNT(?person) > 5)",
        "concepts": ["CHONJ_KW", "NOII_MA_KK", "DEMM_JJ", "NHOMM_THEO_YY", "COO_ZZ"],
        "validation": {"syntax_valid": True, "requires_groupby": True, "requires_having": True}
    },
    {
        "id": 14,
        "level": "medium",
        "category": "order_desc",
        "nl_query": "Sắp xếp sản phẩm theo giá giảm dần",
        "expected_vi": "CHONJ_KW ?san_pham ?gia NOII_MA_KK { ?san_pham :co_gia ?gia } SAP_XXEP_THEO_KK GIAMM_WW(?gia)",
        "expected_sparql": "SELECT ?product ?price WHERE { ?product :hasPrice ?price } ORDER BY DESC(?price)",
        "concepts": ["CHONJ_KW", "NOII_MA_KK", "SAP_XXEP_THEO_KK", "GIAMM_WW"],
        "validation": {"syntax_valid": True}
    },
    {
        "id": 15,
        "level": "medium",
        "category": "union",
        "nl_query": "Lấy tên hoặc nickname của người dùng",
        "expected_vi": "CHONJ_KW ?label NOII_MA_KK { { ?nguoi :coTen ?label } HOPP_QQ { ?nguoi :co_nick ?label } }",
        "expected_sparql": "SELECT ?label WHERE { { ?person :hasName ?label } UNION { ?person :hasNick ?label } }",
        "concepts": ["CHONJ_KW", "NOII_MA_KK", "HOPP_QQ"],
        "validation": {"syntax_valid": True}
    },
    {
        "id": 16,
        "level": "medium",
        "category": "multiple_filters",
        "nl_query": "Tìm người từ 18 đến 65 tuổi",
        "expected_vi": "CHONJ_KW ?nguoi ?tuoi NOII_MA_KK { ?nguoi :coTuoi ?tuoi . LOCJ_RR(?tuoi >= 18 VAA_JJ ?tuoi <= 65) }",
        "expected_sparql": "SELECT ?person ?age WHERE { ?person :hasAge ?age . FILTER(?age >= 18 && ?age <= 65) }",
        "concepts": ["CHONJ_KW", "NOII_MA_KK", "LOCJ_RR", "VAA_JJ"],
        "validation": {"syntax_valid": True}
    },
    {
        "id": 17,
        "level": "medium",
        "category": "string_filter",
        "nl_query": "Tìm người có tên bắt đầu bằng 'Nguyen'",
        "expected_vi": "CHONJ_KW ?nguoi ?ten NOII_MA_KK { ?nguoi :coTen ?ten . LOCJ_RR(BATT_DAU_VOI_KK(?ten, 'Nguyen')) }",
        "expected_sparql": "SELECT ?person ?name WHERE { ?person :hasName ?name . FILTER(STRSTARTS(?name, 'Nguyen')) }",
        "concepts": ["CHONJ_KW", "NOII_MA_KK", "LOCJ_RR", "BATT_DAU_VOI_KK"],
        "validation": {"syntax_valid": True}
    },
    {
        "id": 18,
        "level": "medium",
        "category": "avg",
        "nl_query": "Tính tuổi trung bình của người dùng",
        "expected_vi": "CHONJ_KW (TRUNGG_BINH_PP(?tuoi) GOI_LLA_KK ?tuoi_tb) NOII_MA_KK { ?nguoi :coTuoi ?tuoi }",
        "expected_sparql": "SELECT (AVG(?age) AS ?avg_age) WHERE { ?person :hasAge ?age }",
        "concepts": ["CHONJ_KW", "NOII_MA_KK", "TRUNGG_BINH_PP", "GOI_LLA_KK"],
        "validation": {"syntax_valid": True}
    },
    {
        "id": 19,
        "level": "medium",
        "category": "construct",
        "nl_query": "Tạo quan hệ bạn bè từ cùng thành phố",
        "expected_vi": "XAY_DUNGWJ { ?nguoi1 :ban_cua ?nguoi2 } NOII_MA_KK { ?nguoi1 :song_tai ?tp . ?nguoi2 :song_tai ?tp . LOCJ_RR(?nguoi1 != ?nguoi2) }",
        "expected_sparql": "CONSTRUCT { ?p1 :friendOf ?p2 } WHERE { ?p1 :livesIn ?city . ?p2 :livesIn ?city . FILTER(?p1 != ?p2) }",
        "concepts": ["XAY_DUNGWJ", "NOII_MA_KK", "LOCJ_RR"],
        "validation": {"syntax_valid": True}
    },
    {
        "id": 20,
        "level": "medium",
        "category": "offset",
        "nl_query": "Lấy 10 người tiếp theo sau 20 người đầu",
        "expected_vi": "CHONJ_KW ?nguoi NOII_MA_KK { ?nguoi :coTen ?ten } GIOI_HHAN_RR 10 DICCH_CHUYEN_WW 20",
        "expected_sparql": "SELECT ?person WHERE { ?person :hasName ?name } LIMIT 10 OFFSET 20",
        "concepts": ["CHONJ_KW", "NOII_MA_KK", "GIOI_HHAN_RR", "DICCH_CHUYEN_WW"],
        "validation": {"syntax_valid": True}
    },
    
    # ============================================
    # LEVEL 3: Complex queries (10 cases)
    # ============================================
    {
        "id": 21,
        "level": "complex",
        "category": "nested_aggregation",
        "nl_query": "Tìm top 10 thành phố có nhiều người nhất",
        "expected_vi": "CHONJ_KW ?thanh_pho (DEMM_JJ(?nguoi) GOI_LLA_KK ?so) NOII_MA_KK { ?nguoi :song_tai ?thanh_pho } NHOMM_THEO_YY ?thanh_pho SAP_XXEP_THEO_KK GIAMM_WW(?so) GIOI_HHAN_RR 10",
        "expected_sparql": "SELECT ?city (COUNT(?person) AS ?count) WHERE { ?person :livesIn ?city } GROUP BY ?city ORDER BY DESC(?count) LIMIT 10",
        "concepts": ["CHONJ_KW", "NOII_MA_KK", "DEMM_JJ", "NHOMM_THEO_YY", "SAP_XXEP_THEO_KK", "GIAMM_WW", "GIOI_HHAN_RR"],
        "validation": {"syntax_valid": True, "requires_groupby": True}
    },
    {
        "id": 22,
        "level": "complex",
        "category": "multiple_aggregates",
        "nl_query": "Thống kê số lượng và giá trung bình theo danh mục sản phẩm",
        "expected_vi": "CHONJ_KW ?danh_muc (DEMM_JJ(?sp) GOI_LLA_KK ?so) (TRUNGG_BINH_PP(?gia) GOI_LLA_KK ?gia_tb) NOII_MA_KK { ?sp :thuoc_danh_muc ?danh_muc ; :co_gia ?gia } NHOMM_THEO_YY ?danh_muc",
        "expected_sparql": "SELECT ?category (COUNT(?product) AS ?count) (AVG(?price) AS ?avg) WHERE { ?product :inCategory ?category ; :hasPrice ?price } GROUP BY ?category",
        "concepts": ["CHONJ_KW", "NOII_MA_KK", "DEMM_JJ", "TRUNGG_BINH_PP", "NHOMM_THEO_YY"],
        "validation": {"syntax_valid": True, "requires_groupby": True}
    },
    {
        "id": 23,
        "level": "complex",
        "category": "complex_filter",
        "nl_query": "Tìm sản phẩm có giá cao hơn trung bình",
        "expected_vi": "CHONJ_KW ?sp ?gia NOII_MA_KK { ?sp :co_gia ?gia . { CHONJ_KW (TRUNGG_BINH_PP(?g) GOI_LLA_KK ?tb) NOII_MA_KK { ?s :co_gia ?g } } LOCJ_RR(?gia > ?tb) }",
        "expected_sparql": "SELECT ?p ?price WHERE { ?p :hasPrice ?price . { SELECT (AVG(?pr) AS ?avg) WHERE { ?prod :hasPrice ?pr } } FILTER(?price > ?avg) }",
        "concepts": ["CHONJ_KW", "NOII_MA_KK", "LOCJ_RR", "subquery", "TRUNGG_BINH_PP"],
        "validation": {"syntax_valid": True, "has_subquery": True}
    },
    {
        "id": 24,
        "level": "complex",
        "category": "complex_having",
        "nl_query": "Tìm khách hàng có tổng đơn hàng trên 1 triệu và số đơn trên 5",
        "expected_vi": "CHONJ_KW ?khach (TONGG_WW(?gia) GOI_LLA_KK ?tong) (DEMM_JJ(?don) GOI_LLA_KK ?so_don) NOII_MA_KK { ?don :cua_khach ?khach ; :co_gia ?gia } NHOMM_THEO_YY ?khach COO_ZZ (TONGG_WW(?gia) > 1000000 VAA_JJ DEMM_JJ(?don) > 5)",
        "expected_sparql": "SELECT ?customer (SUM(?price) AS ?total) (COUNT(?order) AS ?num) WHERE { ?order :ofCustomer ?customer ; :hasPrice ?price } GROUP BY ?customer HAVING (SUM(?price) > 1000000 && COUNT(?order) > 5)",
        "concepts": ["CHONJ_KW", "NOII_MA_KK", "TONGG_WW", "DEMM_JJ", "NHOMM_THEO_YY", "COO_ZZ", "VAA_JJ"],
        "validation": {"syntax_valid": True, "requires_groupby": True, "requires_having": True}
    },
    {
        "id": 25,
        "level": "complex",
        "category": "union_filter",
        "nl_query": "Tìm người có email Gmail hoặc Yahoo",
        "expected_vi": "CHONJ_KW ?nguoi ?email NOII_MA_KK { ?nguoi :co_email ?email . LOCJ_RR(CHUAA_RR(?email, '@gmail.com') HOACC_WW CHUAA_RR(?email, '@yahoo.com')) }",
        "expected_sparql": "SELECT ?person ?email WHERE { ?person :hasEmail ?email . FILTER(CONTAINS(?email, '@gmail.com') || CONTAINS(?email, '@yahoo.com')) }",
        "concepts": ["CHONJ_KW", "NOII_MA_KK", "LOCJ_RR", "CHUAA_RR", "HOACC_WW"],
        "validation": {"syntax_valid": True}
    },
    {
        "id": 26,
        "level": "complex",
        "category": "optional_aggregation",
        "nl_query": "Đếm số đơn hàng của mỗi khách (bao gồm cả khách chưa có đơn)",
        "expected_vi": "CHONJ_KW ?khach (DEMM_JJ(?don) GOI_LLA_KK ?so) NOII_MA_KK { ?khach laa_jj :KhachHang . TUYJ_CHON_PP { ?don :cua_khach ?khach } } NHOMM_THEO_YY ?khach",
        "expected_sparql": "SELECT ?customer (COUNT(?order) AS ?count) WHERE { ?customer a :Customer . OPTIONAL { ?order :ofCustomer ?customer } } GROUP BY ?customer",
        "concepts": ["CHONJ_KW", "NOII_MA_KK", "TUYJ_CHON_PP", "DEMM_JJ", "NHOMM_THEO_YY"],
        "validation": {"syntax_valid": True, "requires_groupby": True}
    },
    {
        "id": 27,
        "level": "complex",
        "category": "max_min",
        "nl_query": "Tìm giá cao nhất và thấp nhất của mỗi danh mục",
        "expected_vi": "CHONJ_KW ?danh_muc (LONN_NHAT_RR(?gia) GOI_LLA_KK ?gia_max) (NHOO_NHAT_QQ(?gia) GOI_LLA_KK ?gia_min) NOII_MA_KK { ?sp :thuoc_danh_muc ?danh_muc ; :co_gia ?gia } NHOMM_THEO_YY ?danh_muc",
        "expected_sparql": "SELECT ?category (MAX(?price) AS ?max) (MIN(?price) AS ?min) WHERE { ?product :inCategory ?category ; :hasPrice ?price } GROUP BY ?category",
        "concepts": ["CHONJ_KW", "NOII_MA_KK", "LONN_NHAT_RR", "NHOO_NHAT_QQ", "NHOMM_THEO_YY"],
        "validation": {"syntax_valid": True, "requires_groupby": True}
    },
    {
        "id": 28,
        "level": "complex",
        "category": "regex",
        "nl_query": "Tìm người có số điện thoại theo định dạng 09xx-xxx-xxx",
        "expected_vi": "CHONJ_KW ?nguoi ?sdt NOII_MA_KK { ?nguoi :co_dien_thoai ?sdt . LOCJ_RR(BIEUU_THUC_CHINH_QUY_JJ(?sdt, '^09[0-9]{2}-[0-9]{3}-[0-9]{3}$')) }",
        "expected_sparql": "SELECT ?person ?phone WHERE { ?person :hasPhone ?phone . FILTER(REGEX(?phone, '^09[0-9]{2}-[0-9]{3}-[0-9]{3}$')) }",
        "concepts": ["CHONJ_KW", "NOII_MA_KK", "LOCJ_RR", "BIEUU_THUC_CHINH_QUY_JJ"],
        "validation": {"syntax_valid": True}
    },
    {
        "id": 29,
        "level": "complex",
        "category": "multi_optional",
        "nl_query": "Lấy thông tin người dùng với email và số điện thoại (nếu có)",
        "expected_vi": "CHONJ_KW ?nguoi ?ten ?email ?sdt NOII_MA_KK { ?nguoi :co_ten ?ten . TUYJ_CHON_PP { ?nguoi :co_email ?email } TUYJ_CHON_PP { ?nguoi :co_dien_thoai ?sdt } }",
        "expected_sparql": "SELECT ?person ?name ?email ?phone WHERE { ?person :hasName ?name . OPTIONAL { ?person :hasEmail ?email } OPTIONAL { ?person :hasPhone ?phone } }",
        "concepts": ["CHONJ_KW", "NOII_MA_KK", "TUYJ_CHON_PP"],
        "validation": {"syntax_valid": True}
    },
    {
        "id": 30,
        "level": "complex",
        "category": "full_pipeline",
        "nl_query": "Top 5 danh mục có doanh thu cao nhất với số sản phẩm trên 10",
        "expected_vi": "CHONJ_KW ?danh_muc (TONGG_WW(?gia) GOI_LLA_KK ?doanh_thu) (DEMM_JJ(?sp) GOI_LLA_KK ?so_sp) NOII_MA_KK { ?sp :thuoc_danh_muc ?danh_muc ; :co_gia ?gia } NHOMM_THEO_YY ?danh_muc COO_ZZ (DEMM_JJ(?sp) > 10) SAP_XXEP_THEO_KK GIAMM_WW(?doanh_thu) GIOI_HHAN_RR 5",
        "expected_sparql": "SELECT ?category (SUM(?price) AS ?revenue) (COUNT(?product) AS ?count) WHERE { ?product :inCategory ?category ; :hasPrice ?price } GROUP BY ?category HAVING (COUNT(?product) > 10) ORDER BY DESC(?revenue) LIMIT 5",
        "concepts": ["CHONJ_KW", "NOII_MA_KK", "TONGG_WW", "DEMM_JJ", "NHOMM_THEO_YY", "COO_ZZ", "SAP_XXEP_THEO_KK", "GIAMM_WW", "GIOI_HHAN_RR"],
        "validation": {"syntax_valid": True, "requires_groupby": True, "requires_having": True}
    }
]

def save_test_cases():
    """Save test cases to JSON file"""
    output_path = "/media/thuongnv/New Volume/Code/Github/ograg2-1/data/dsl/sparql_vi/test_cases.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(TEST_CASES, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved {len(TEST_CASES)} test cases to {output_path}")
    
    # Statistics
    by_level = {}
    by_category = {}
    for tc in TEST_CASES:
        level = tc['level']
        category = tc['category']
        by_level[level] = by_level.get(level, 0) + 1
        by_category[category] = by_category.get(category, 0) + 1
    
    print(f"\n📊 Statistics:")
    print(f"  By Level: {by_level}")
    print(f"  By Category: {len(by_category)} categories")
    print(f"  Categories: {list(by_category.keys())}")

if __name__ == "__main__":
    save_test_cases()
