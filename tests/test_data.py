import os

from app import (
    compute_checksum,
    get_data_path,
    load_bundled_data,
    validate_api_data,
)

DATA_DIR = get_data_path()
BUNDLED_APIS_FILE = os.path.join(DATA_DIR, 'apis.json')
CHECKSUM_FILE = os.path.join(DATA_DIR, 'apis.json.sha256')


def test_data_directory_exists():
    assert os.path.isdir(DATA_DIR)


def test_apis_json_exists():
    assert os.path.isfile(BUNDLED_APIS_FILE)


def test_load_bundled_data():
    data = load_bundled_data()
    assert data is not None
    assert isinstance(data, list)
    assert len(data) > 0


def test_schema_validation_valid():
    sample = {
        'name': 'Test API',
        'category': 'Test',
        'description': 'A test API',
        'auth': 'none',
        'rate_limit': '100/min',
        'endpoints': [],
        'docs_url': 'https://example.com',
        'tags': ['test'],
    }
    valid, msg = validate_api_data([sample])
    assert valid is True
    assert msg is None


def test_schema_validation_missing_field():
    sample = {
        'name': 'Test API',
        'category': 'Test',
        'description': 'A test API',
        'auth': 'none',
        'rate_limit': '100/min',
        'endpoints': [],
        'docs_url': 'https://example.com',
    }
    valid, msg = validate_api_data([sample])
    assert valid is False
    assert 'tags' in msg


def test_schema_validation_not_list():
    valid, msg = validate_api_data({'not': 'a list'})
    assert valid is False
    assert 'not a list' in msg


def test_schema_validation_item_not_dict():
    valid, msg = validate_api_data(['not a dict'])
    assert valid is False
    assert 'not an object' in msg


def test_checksum_file_exists():
    assert os.path.isfile(CHECKSUM_FILE)


def test_checksum_verification():
    assert os.path.isfile(BUNDLED_APIS_FILE)
    actual_hash = compute_checksum(BUNDLED_APIS_FILE)
    with open(CHECKSUM_FILE) as f:
        expected_hash = f.read().strip()
    assert actual_hash == expected_hash


def test_checksum_mismatch_detected():
    actual_hash = compute_checksum(BUNDLED_APIS_FILE)
    fake_hash = '0' * 64
    assert actual_hash != fake_hash
