import pytest
from services.space_service import SpaceService, SPACE_TYPES


class FakeRepo:
    def __init__(self):
        self.spaces = []

    def add(self, space):
        space.id = len(self.spaces) + 1
        self.spaces.append(space)
        return space

    def get_by_id(self, space_id):
        return next((s for s in self.spaces if s.id == space_id), None)

    def list(self):
        return list(self.spaces)

    def search(self, filters):
        return [s for s in self.spaces]

    def update(self, space):
        for i, s in enumerate(self.spaces):
            if s.id == space.id:
                self.spaces[i] = space
                return space
        raise ValueError('Space not found')

    def delete(self, space_id):
        self.spaces = [s for s in self.spaces if s.id != space_id]


@pytest.fixture
def service():
    return SpaceService(FakeRepo())


def test_create_success(service):
    space = service.create(provider_id=1, name='Studio A', space_type='studio',
                           description='mo ta', max_capacity=10, base_price_per_hour=100)
    assert space.id == 1
    assert space.name == 'Studio A'
    assert space.space_type == 'studio'
    assert space.provider_id == 1


def test_create_darkroom(service):
    space = service.create(provider_id=1, name='Darkroom B', space_type='darkroom')
    assert space.space_type == 'darkroom'


def test_create_invalid_type(service):
    with pytest.raises(ValueError):
        service.create(provider_id=1, name='X', space_type='mansion')


def test_get_success(service):
    service.create(provider_id=1, name='A', space_type='studio')
    result = service.get(1)
    assert result is not None and result.name == 'A'


def test_get_not_found(service):
    assert service.get(999) is None


def test_list(service):
    service.create(provider_id=1, name='A', space_type='studio')
    service.create(provider_id=1, name='B', space_type='darkroom')
    assert len(service.list()) == 2


def test_update_success(service):
    service.create(provider_id=1, name='A', space_type='studio')
    updated = service.update(1, provider_id=1, name='A VIP', space_type='darkroom',
                             max_capacity=20, base_price_per_hour=300, status=False)
    assert updated.name == 'A VIP'
    assert updated.space_type == 'darkroom'
    assert updated.status is False


def test_update_invalid_type(service):
    service.create(provider_id=1, name='A', space_type='studio')
    with pytest.raises(ValueError):
        service.update(1, provider_id=1, name='A', space_type='bad')


def test_update_not_found(service):
    with pytest.raises(ValueError):
        service.update(999, provider_id=1, name='A', space_type='studio')


def test_delete(service):
    service.create(provider_id=1, name='A', space_type='studio')
    service.delete(1)
    assert service.get(1) is None


def test_search_success(service):
    service.create(provider_id=1, name='Studio', space_type='studio', base_price_per_hour=100)
    result = service.search({'q': 'studio', 'space_type': 'studio', 'min_price': 50, 'max_price': 200})
    assert len(result) == 1


def test_search_invalid_type(service):
    with pytest.raises(ValueError):
        service.search({'space_type': 'bad'})


def test_search_min_gt_max(service):
    with pytest.raises(ValueError):
        service.search({'min_price': 300, 'max_price': 100})


def test_search_empty_filters(service):
    service.create(provider_id=1, name='A', space_type='studio')
    assert len(service.search({})) == 1


def test_spaces_types():
    assert SPACE_TYPES == {'darkroom', 'studio'}