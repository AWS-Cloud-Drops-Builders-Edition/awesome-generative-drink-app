"""
Configuração global para testes pytest.
"""


def pytest_configure(config):
    """
    Registra os marcadores personalizados para os testes.
    """
    config.addinivalue_line("markers", "unit: marca testes de unidade")
    config.addinivalue_line("markers", "integration: marca testes de integração")
    config.addinivalue_line("markers", "e2e: marca testes end-to-end")
