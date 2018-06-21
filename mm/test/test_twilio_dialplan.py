import pytest
import os

os.environ['MM_CONFIG'] = 'mm.config.TestingConfig'


from mm import app
from mm.test.sample.twilio import outbound_dial


@pytest.fixture
def client():
    import pprint
    pprint.pprint(app.config)
    app.config['TESTING'] = True
    client = app.test_client()

    yield client


def test_outbound_dial(client):
    res = client.post('/voice/out', data=outbound_dial)

    import pprint
    pprint.pprint(res)
