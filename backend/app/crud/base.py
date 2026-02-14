import logging
from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType]):
        self.model = model
        self.logger = logging.getLogger(self.__class__.__name__)

    def get(self, db: Session, id: Any) -> ModelType | None:
        return db.get(self.model, id)

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> list[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: CreateSchemaType | dict[str, Any]) -> ModelType:
        obj_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump()
        db_obj = self.model(**obj_data)
        try:
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        except SQLAlchemyError:
            db.rollback()
            self.logger.exception("Failed to create %s", self.model.__name__)
            raise
        return db_obj

    def update(
        self,
        db: Session,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any],
    ) -> ModelType:
        obj_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(
            exclude_unset=True
        )
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        try:
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        except SQLAlchemyError:
            db.rollback()
            self.logger.exception("Failed to update %s", self.model.__name__)
            raise
        return db_obj

    def delete(self, db: Session, id: Any) -> ModelType | None:
        obj = db.get(self.model, id)
        if obj is None:
            return None
        try:
            db.delete(obj)
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            self.logger.exception("Failed to delete %s", self.model.__name__)
            raise
        return obj

    def remove(self, db: Session, id: Any) -> ModelType | None:
        return self.delete(db, id)
