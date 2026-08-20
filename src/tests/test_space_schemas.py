from types import SimpleNamespace

from api.schemas.space import SpaceRequestSchema, SpaceResponseSchema

request_schema = SpaceRequestSchema()
response_schema = SpaceResponseSchema()


def test_request_valid():
    data = {'provider_id': 1, 'name': 'A', 'space_type': 'studio'}
    errors = request_schema.validate(data)
    assert errors == {}


def test_request_missing_required():
    errors = request_schema.validate({})
    assert 'provider_id' in errors
    assert 'name' in errors
    assert 'space_type' in errors


def test_request_optional_fields():
    data = {'provider_id': 1, 'name': 'A', 'space_type': 'studio',
            'description': 'x', 'max_capacity': 5, 'base_price_per_hour': 100, 'status': False}
    assert request_schema.validate(data) == {}


def test_request_invalid_price_type():
    errors = request_schema.validate({'provider_id': 1, 'name': 'A', 'space_type': 'studio',
                                      'base_price_per_hour': 'abc'})
    assert 'base_price_per_hour' in errors


def test_response_dump_enum_type():
    space = SimpleNamespace(
        id=1, provider_id=1, name='A',
        type=SimpleNamespace(value='studio'),
        description=None, address=None, max_capacity=None,
        base_price_per_hour=100.0, status=True, created_at=None, updated_at=None)
    data = response_schema.dump(space)
    assert data['type'] == 'studio'
    assert data['id'] == 1
    assert data['base_price_per_hour'] == 100.0


def test_response_dump_string_type():
    space = SimpleNamespace(
        id=1, provider_id=1, name='A', type='darkroom',
        description=None, address=None, max_capacity=None,
        base_price_per_hour=0.0, status=True, created_at=None, updated_at=None)
    assert response_schema.dump(space)['type'] == 'darkroom'