import logging

from sqlalchemy import select, insert, update, delete
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError, NoResultFound

from src.users_db import engine

logger = logging.getLogger(__name__)


class BaseRepository:
    model = None
    schema: BaseModel = None

    def __init__(self, session):
        self.session = session

    async def get_filtered(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        return [self.schema.model_validate(model, from_attributes=True) for model in result.scalars().all()]

    async def get_all(self, *args, **kwargs):
        return await self.get_filtered()

    async def get_one_or_none(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if model is None:
            raise NoResultFound
        return self.schema.model_validate(model, from_attributes=True)

    async def get_data_by_id(self, data_id: int):
        query = select(self.model).filter_by(id=data_id)
        result = await self.session.execute(query)
        model = result.scalars().one()
        return self.schema.model_validate(model, from_attributes=True)

    async def add(self, data: BaseModel):
        add_data_stmt = (
            insert(self.model)
            .values(**data.model_dump())
            .returning(self.model)
        )
        logger.info(add_data_stmt.compile(engine, compile_kwargs={"literal_binds": True}))
        try:
            result = await self.session.execute(add_data_stmt)
        except IntegrityError:
            raise
        model = result.scalars().one()
        return self.schema.model_validate(model)

    async def edit(
            self, data: BaseModel,
            exclude_unset: bool = False,
            **filter_by
    ):
        try:
            update_data_stmt = (
                update(self.model)
                .filter_by(**filter_by)
                .values(**data.model_dump(exclude_unset=exclude_unset))
            )
        except IntegrityError:
            raise
        print(update_data_stmt.compile(engine, compile_kwargs={"literal_binds": True}))
        await self.session.execute(update_data_stmt)

    async def delete(self, **filter_by):
        delete_data_stmt = delete(self.model).filter_by(**filter_by)
        print(delete_data_stmt.compile(engine, compile_kwargs={"literal_binds": True}))
        await self.session.execute(delete_data_stmt)
