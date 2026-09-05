from typing import List, Optional
from sqlalchemy.orm import Session
from business.models.itodo_repository import ITodoRepository
from business.models.todo import Todo
from database.models.todo_model import TodoModel
from database.databases.factory_database import FactoryDatabase as db_factory


class TodoRepository(ITodoRepository):
    def __init__(self, session: Session = None):
        self.session = session or db_factory.get_database('POSTGREE').session

    def add(self, todo: Todo) -> TodoModel:
        try:
            model = TodoModel(
                title=todo.title,
                description=todo.description,
                status=todo.status,
                created_at=todo.created_at,
                updated_at=todo.updated_at
            )
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return model
        except Exception:
            self.session.rollback()
            raise ValueError('Could not create todo')

    def get_by_id(self, todo_id: int) -> Optional[TodoModel]:
        return self.session.query(TodoModel).filter_by(id=todo_id).first()

    def list(self) -> List[TodoModel]:
        return self.session.query(TodoModel).all()

    def update(self, todo: Todo) -> TodoModel:
        try:
            existing = self.session.query(TodoModel).filter_by(id=todo.id).first()
            if not existing:
                raise ValueError('Todo not found')
            existing.title = todo.title
            existing.description = todo.description
            existing.status = todo.status
            existing.created_at = todo.created_at
            existing.updated_at = todo.updated_at
            self.session.commit()
            self.session.refresh(existing)
            return existing
        except ValueError:
            self.session.rollback()
            raise
        except Exception:
            self.session.rollback()
            raise ValueError('Could not update todo')

    def delete(self, todo_id: int) -> None:
        try:
            model = self.session.query(TodoModel).filter_by(id=todo_id).first()
            if model:
                self.session.delete(model)
                self.session.commit()
            else:
                raise ValueError('Todo not found')
        except ValueError:
            raise
        except Exception:
            self.session.rollback()
            raise ValueError('Todo not found')
