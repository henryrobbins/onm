import os
import pytest
from onm.sources import Sources
from onm.source.plaid_source import PlaidSource

pytestmark = pytest.mark.unit


def test_sources_get_plaid_source():
    sources_path = os.path.join(os.path.dirname(__file__), "resources/sources.ini")
    sources = Sources(sources_path)
    source = sources.get_source("platypus_bank")
    assert PlaidSource == type(source)
    assert "access-sandbox-a4a6c36b-0276-431d-a843-65c30b506e77" == source.access_token
    account_id_map = source.account_id_map
    assert "checking" == account_id_map["6886e1c6916351f894255ef738176744"]
    assert "savings" == account_id_map["9217d6c969ac114533812fdacb15b11a"]


def test_sources_add_plaid_source():
    sources_path = os.path.join(os.path.dirname(__file__), "resources/test-sources.ini")
    sources = Sources(sources_path)
    source = PlaidSource(
        name="onm_bank",
        access_token="access-sandbox-a4a6c36b-0276-431d-a843-65c30b506e77",
        account_id_map={
            "a927faed81ca48916e56e6ccda63fe09": "checking",
            "76b069b74b582f62f4890a88b14402a6": "savings",
        },
    )
    sources.add_source(source)

    source = sources.get_source("onm_bank")
    assert PlaidSource == type(source)
    assert "access-sandbox-a4a6c36b-0276-431d-a843-65c30b506e77" == source.access_token
    account_id_map = source.account_id_map
    assert "checking" == account_id_map["a927faed81ca48916e56e6ccda63fe09"]
    assert "savings" == account_id_map["76b069b74b582f62f4890a88b14402a6"]

    os.remove(sources_path)
