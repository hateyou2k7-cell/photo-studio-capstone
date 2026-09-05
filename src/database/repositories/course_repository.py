from typing import List, Optional
from business.models.icourse_repository import ICourseRepository
from business.models.course import Course
from database.models.course_model import CourseModel
from database.databases.factory_database import FactoryDatabase as db_factory


class CourseRepository(ICourseRepository):

    def add(self, course: Course) -> Course:
        db_session = db_factory.get_database('POSTGREE').session
        try:
            model = CourseModel(
                course_name=course.course_name,
                description=course.description,
                status=course.status,
                start_date=course.start_date,
                end_date=course.end_date,
                created_at=course.created_at,
                updated_at=course.updated_at,
            )
            db_session.add(model)
            db_session.commit()
            return Course(
                id=model.id,
                course_name=model.course_name,
                description=model.description,
                status=model.status,
                start_date=model.start_date,
                end_date=model.end_date,
                created_at=model.created_at,
                updated_at=model.updated_at,
            )
        except Exception as e:
            db_session.rollback()
            raise e

    def get_by_id(self, course_id: int) -> Optional[Course]:
        db_session = db_factory.get_database('POSTGREE').session
        model = db_session.query(CourseModel).filter(CourseModel.id == course_id).first()
        if not model:
            return None
        return Course(
            id=model.id,
            course_name=model.course_name,
            description=model.description,
            status=model.status,
            start_date=model.start_date,
            end_date=model.end_date,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def list(self) -> List[Course]:
        db_session = db_factory.get_database('POSTGREE').session
        models = db_session.query(CourseModel).all()
        return [
            Course(
                id=m.id,
                course_name=m.course_name,
                description=m.description,
                status=m.status,
                start_date=m.start_date,
                end_date=m.end_date,
                created_at=m.created_at,
                updated_at=m.updated_at,
            )
            for m in models
        ]

    def update(self, course: Course) -> Course:
        db_session = db_factory.get_database('POSTGREE').session
        try:
            model = db_session.query(CourseModel).filter(CourseModel.id == course.id).first()
            if not model:
                raise ValueError("Course not found")
            model.course_name = course.course_name
            model.description = course.description
            model.status = course.status
            model.start_date = course.start_date
            model.end_date = course.end_date
            model.updated_at = course.updated_at
            db_session.commit()
            return Course(
                id=model.id,
                course_name=model.course_name,
                description=model.description,
                status=model.status,
                start_date=model.start_date,
                end_date=model.end_date,
                created_at=model.created_at,
                updated_at=model.updated_at,
            )
        except Exception as e:
            db_session.rollback()
            raise e

    def delete(self, course_id: int) -> None:
        db_session = db_factory.get_database('POSTGREE').session
        try:
            model = db_session.query(CourseModel).filter(CourseModel.id == course_id).first()
            if model:
                db_session.delete(model)
                db_session.commit()
        except Exception as e:
            db_session.rollback()
            raise e
