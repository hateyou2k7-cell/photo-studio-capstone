from datetime import datetime
from types import SimpleNamespace

import pytest
from app import create_app
from api.controllers import space_controller


def make_space(space_id=1, provider_id=1, name='Studio A', space_type='studio'):
    return SimpleNamespace(
        id=space_id, provider_id=provider_id, name=name, type=space_type,
        description='mo ta', address=None, max_capacity=10,
        base_price_per_hour=100.0, status=True,
        created_at=datetime.utcnow(), updated_at=datetime.utcnow(),
    )


class FakeService:
    def __init__(self):
        self.spaces = []
        self._id = 1

    def list(self):
        return list(self.spaces)

    def get(self, space_id):
        return next((s for s in self.spaces if s.id == space_id), None)

    def create(self, **kwargs):
        if kwargs.get('space_type') not in ('darkroom', 'studio'):
            raise ValueError("space_type must be 'darkroom' or 'studio'")
        space = make_space(space_id=self._id, name=kwargs['name'],
                           space_type=kwargs['space_type'], provider_id=kwargs['provider_id'])
        self._id += 1
        self.spaces.append(space)
        return space

    def update(self, **kwargs):
        existing = self.get(kwargs['space_id'])
        if not existing:
            raise ValueError('Space not found')
        if kwargs.get('space_type') not in ('darkroom', 'studio'):
            raise ValueError("space_type must be 'darkroom' or 'studio'")
        existing.name = kwargs['name']
        return existing

    def delete(self, space_id):
        existing = self.get(space_id)
        if not existing:
            raise ValueError('Space not found')
        self.spaces = [s for s in self.spaces if s.id != space_id]

    def search(self, filters):
        if filters.get('space_type') and filters['space_type'] not in ('darkroom', 'studio'):
            raise ValueError("space_type must be 'darkroom' or 'studio'")
        return self.spaces


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


@pytest.fixture
def fake():
    return FakeService()


@pytest.fixture(autouse=True)
def patch_service(monkeypatch, fake):
    monkeypatch.setattr(space_controller, 'space_service', fake)


def test_list_spaces(client, fake):
    fake.spaces.append(make_space(space_id=1))
    r = client.get('/spaces/')
    assert r.status_code == 200
    assert len(r.get_json()) == 1


def test_get_space(client, fake):
    fake.spaces.append(make_space(space_id=1))
    r = client.get('/spaces/1')
    assert r.status_code == 200
    assert r.get_json()['name'] == 'Studio A'
    assert r.get_json()['type'] == 'studio'


def test_get_space_not_found(client):
    assert client.get('/spaces/999').status_code == 404


def test_create_space(client):
    r = client.post('/spaces/', json={
        'provider_id': 1, 'name': 'New Studio', 'space_type': 'studio',
        'max_capacity': 5, 'base_price_per_hour': 250})
    assert r.status_code == 201
    assert r.get_json()['name'] == 'New Studio'


def test_create_space_missing_field(client):
    r = client.post('/spaces/', json={'provider_id': 1})
    assert r.status_code == 400


def test_create_space_invalid_type(client):
    r = client.post('/spaces/', json={
        'provider_id': 1, 'name': 'X', 'space_type': 'mansion'})
    assert r.status_code == 400


def test_update_space(client, fake):
    fake.spaces.append(make_space(space_id=1))
    r = client.put('/spaces/1', json={
        'provider_id': 1, 'name': 'Studio A VIP', 'space_type': 'darkroom'})
    assert r.status_code == 200
    assert r.get_json()['name'] == 'Studio A VIP'


def test_update_space_not_found(client):
    r = client.put('/spaces/999', json={
        'provider_id': 1, 'name': 'X', 'space_type': 'studio'})
    assert r.status_code == 404


def test_update_space_invalid_body(client, fake):
    fake.spaces.append(make_space(space_id=1))
    r = client.put('/spaces/1', json={})
    assert r.status_code == 400


def test_update_space_invalid_type(client, fake):
    fake.spaces.append(make_space(space_id=1))
    r = client.put('/spaces/1', json={
        'provider_id': 1, 'name': 'X', 'space_type': 'mansion'})
    assert r.status_code == 400


def test_delete_space(client, fake):
    fake.spaces.append(make_space(space_id=1))
    assert client.delete('/spaces/1').status_code == 204


def test_delete_space_not_found(client):
    assert client.delete('/spaces/999').status_code == 404


def test_search_spaces(client, fake):
    fake.spaces.append(make_space(space_id=1))
    r = client.get('/spaces/search?q=studio&space_type=studio&min_price=50&max_price=200&available=true')
    assert r.status_code == 200
    assert len(r.get_json()) == 1


def test_search_min_capacity(client, fake):
    fake.spaces.append(make_space(space_id=1))
    r = client.get('/spaces/search?min_capacity=4&available=false')
    assert r.status_code == 200
    assert len(r.get_json()) == 1


def test_search_invalid_type(client):
    r = client.get('/spaces/search?space_type=bad')
    assert r.status_code == 400