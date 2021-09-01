import pytest
from hktkzyx_toolbox_web import create_app


@pytest.fixture
def app():
    test_config = {'TESTING': True, 'SECRET_KEY': 'testing'}
    app = create_app(test_config)
    yield app


@pytest.fixture
def client(app):
    return app.test_client()