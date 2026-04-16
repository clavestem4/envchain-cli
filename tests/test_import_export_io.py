"""Tests for envchain.import_export_io module."""

import json
import pytest
from pathlib import Path

from envchain.import_export_io import (
    export_bundle,
    import_bundle,
    export_bundle_to_file,
    import_bundle_from_file,
)
from envchain.chain import add_chain, get_chain


PASSWORD = "test-secret"
CHAIN = "myproject"
VARS = {"DB_URL": "postgres://localhost/db", "SECRET_KEY": "abc123"}


@pytest.fixture
def tmp_store(tmp_path):
    return tmp_path / "store.json"


def test_export_bundle_returns_json_string(tmp_store):
    add_chain(CHAIN, VARS, PASSWORD, store_path=tmp_store)
    bundle_str = export_bundle(CHAIN, PASSWORD, store_path=tmp_store)
    bundle = json.loads(bundle_str)
    assert bundle["version"] == 1
    assert bundle["chain"] == CHAIN
    assert "data" in bundle


def test_import_bundle_roundtrip(tmp_store):
    add_chain(CHAIN, VARS, PASSWORD, store_path=tmp_store)
    bundle_str = export_bundle(CHAIN, PASSWORD, store_path=tmp_store)

    other_store = tmp_store.parent / "other_store.json"
    imported_name = import_bundle(bundle_str, PASSWORD, store_path=other_store)
    assert imported_name == CHAIN

    recovered = get_chain(CHAIN, PASSWORD, store_path=other_store)
    assert recovered == VARS


def test_import_bundle_with_rename(tmp_store):
    add_chain(CHAIN, VARS, PASSWORD, store_path=tmp_store)
    bundle_str = export_bundle(CHAIN, PASSWORD, store_path=tmp_store)

    other_store = tmp_store.parent / "renamed_store.json"
    imported_name = import_bundle(bundle_str, PASSWORD, chain_name="renamed", store_path=other_store)
    assert imported_name == "renamed"
    recovered = get_chain("renamed", PASSWORD, store_path=other_store)
    assert recovered == VARS


def test_import_bundle_raises_if_exists_no_overwrite(tmp_store):
    add_chain(CHAIN, VARS, PASSWORD, store_path=tmp_store)
    bundle_str = export_bundle(CHAIN, PASSWORD, store_path=tmp_store)
    with pytest.raises(ValueError, match="already exists"):
        import_bundle(bundle_str, PASSWORD, store_path=tmp_store)


def test_import_bundle_overwrite(tmp_store):
    add_chain(CHAIN, VARS, PASSWORD, store_path=tmp_store)
    bundle_str = export_bundle(CHAIN, PASSWORD, store_path=tmp_store)
    imported_name = import_bundle(bundle_str, PASSWORD, overwrite=True, store_path=tmp_store)
    assert imported_name == CHAIN


def test_import_bundle_wrong_password(tmp_store):
    add_chain(CHAIN, VARS, PASSWORD, store_path=tmp_store)
    bundle_str = export_bundle(CHAIN, PASSWORD, store_path=tmp_store)
    with pytest.raises(Exception):
        import_bundle(bundle_str, "wrong-password", store_path=tmp_store)


def test_export_and_import_via_file(tmp_store, tmp_path):
    add_chain(CHAIN, VARS, PASSWORD, store_path=tmp_store)
    bundle_file = tmp_path / "bundle.json"
    export_bundle_to_file(CHAIN, PASSWORD, bundle_file, store_path=tmp_store)
    assert bundle_file.exists()

    other_store = tmp_path / "imported_store.json"
    name = import_bundle_from_file(bundle_file, PASSWORD, store_path=other_store)
    assert name == CHAIN
    assert get_chain(CHAIN, PASSWORD, store_path=other_store) == VARS


def test_import_bundle_invalid_json(tmp_store):
    with pytest.raises(ValueError, match="Invalid bundle format"):
        import_bundle("not-json", PASSWORD, store_path=tmp_store)
