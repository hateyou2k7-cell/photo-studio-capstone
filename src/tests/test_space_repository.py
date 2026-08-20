from datetime import datetime, time
from unittest.mock import MagicMock

import pytest
from infrastructure.repositories.space_repository import SpaceRepository
from infrastructure.models.film_space_model import SpaceType
from domain.models.space import Space


def make_domain_space(space_id=None):
    return Space(id=space_id, provider_id=1, name='Studio A', space_type='studio',
                 description='mo ta', max_capacity=10, base_price_per_hour=100, status=True)


class FakeQuery:
    def __init__(self, result=None):
        self.result = result if result is not None else []

    def filter(self, *a, **k):
        return self

    def filter_by(self, *a, **k):
        return self

    def order_by(self, *a, **k):
        return self

    def all(self):
        return self.result

    def first(self):
        return self.result[0] if self.result else None

    def update(self, *a, **k):
        return 1


@pytest.fixture
def session():
    return MagicMock()


def test_add_success(session):
    repo = SpaceRepository(session)
    repo.add(make_domain_space())
    session.add.assert_called_once()
    session.commit.assert_called_once()
    session.refresh.assert_called_once()


def test_add_failure(session):
    session.add.side_effect = Exception('boom')
    repo = SpaceRepository(session)
    with pytest.raises(ValueError):
        repo.add(make_domain_space())


def test_get_by_id(session):
    model = MagicMock()
    session.query.return_value.filter_by.return_value.first.return_value = model
    repo = SpaceRepository(session)
    assert repo.get_by_id(1) is model


def test_list(session):
    session.query.return_value.all.return_value = [MagicMock(), MagicMock()]
    repo = SpaceRepository(session)
    assert len(repo.list()) == 2


def test_search_no_filters(session):
    session.query.return_value.all.return_value = []
    repo = SpaceRepository(session)
    assert repo.search({}) == []


def test_search_with_all_filters(session):
    q = FakeQuery([MagicMock()])
    session.query.return_value = q
    repo = SpaceRepository(session)
    result = repo.search({
        'q': 'studio', 'space_type': 'studio', 'min_price': 50, 'max_price': 200,
        'min_capacity': 5, 'available': True})
    assert len(result) == 1


def test_update_success(session):
    model = MagicMock()
    session.query.return_value.filter_by.return_value.first.return_value = model
    repo = SpaceRepository(session)
    result = repo.update(make_domain_space(space_id=1))
    assert result is model
    session.commit.assert_called_once()


def test_update_not_found(session):
    session.query.return_value.filter_by.return_value.first.return_value = None
    repo = SpaceRepository(session)
    with pytest.raises(ValueError):
        repo.update(make_domain_space(space_id=1))


def test_delete_success(session):
    model = MagicMock()
    session.query.return_value.filter_by.return_value.first.return_value = model
    repo = SpaceRepository(session)
    repo.delete(1)
    session.delete.assert_called_once_with(model)
    session.commit.assert_called_once()


def test_delete_not_found(session):
    session.query.return_value.filter_by.return_value.first.return_value = None
    repo = SpaceRepository(session)
    with pytest.raises(ValueError):
        repo.delete(1)


def test_space_type_enum_values():
    assert SpaceType('studio').value == 'studio'
    assert SpaceType('darkroom').value == 'darkroom'