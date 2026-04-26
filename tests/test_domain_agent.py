from src.agents.domain_agent import DomainAgent


def test_domain_agent_loads_criminal_law_config():
    agent = DomainAgent("criminal_law")
    assert agent.domain == "criminal_law"
    assert "刑法" in agent.system_prompt


def test_domain_agent_falls_back_to_general():
    agent = DomainAgent("nonexistent_domain")
    assert agent.domain == "nonexistent_domain"
    assert "法律咨询" in agent.system_prompt