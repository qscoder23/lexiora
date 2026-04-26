from src.agents.coordinator import identify_domain, DOMAIN_MAP


def test_domain_map_covers_all_internal_domains():
    """DOMAIN_MAP应覆盖所有定义的领域"""
    mapped_values = set(DOMAIN_MAP.values())
    for domain in ["civil_law", "criminal_law", "labor_law", "admin_law"]:
        assert domain in mapped_values