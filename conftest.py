import os


def pytest_addoption(parser):
    parser.addoption('--no-skip', action='store_true', default=False, help='Run tests that are skipped for local builds')


def pytest_configure(config):
    if config.getoption('--no-skip'):
        os.environ['NO_SKIP'] = '1'