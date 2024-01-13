def pytest_addoption(parser):
    parser.addoption("--client_id", action="append", default=[])
    parser.addoption("--secret", action="append", default=[])


def pytest_generate_tests(metafunc):
    if "client_id" in metafunc.fixturenames:
        metafunc.parametrize("client_id", metafunc.config.getoption("client_id"))
    if "secret" in metafunc.fixturenames:
        metafunc.parametrize("secret", metafunc.config.getoption("secret"))
