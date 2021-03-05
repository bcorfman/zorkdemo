""" PyTest Configuration """
import os
import pytest
from .models import create_tables, drop_tables


def pytest_configure(config):
    """setup configuration"""
    os.environ["HUG_SETTINGS"] = "test"
    os.environ["SECRET_KEY"] = "test secret key"


def pytest_unconfigure(config):
    """teardown configuration"""
    pass


@pytest.fixture(autouse=True)
def db_wrapper():
    # NOTE: before test is run
    create_tables()
    # run the actual test
    yield
    # NOTE: after test is run
    drop_tables()
