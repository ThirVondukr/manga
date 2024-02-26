import uuid

import pytest

from app.core.domain.groups.repositories import GroupRepository
from app.db.models import Group, User
from lib.db import DBContext
from tests.types import Resolver


@pytest.fixture
async def group(db_context: DBContext, user: User) -> Group:
    group = Group(name=str(uuid.uuid4()), created_by=user)
    db_context.add(group)
    await db_context.flush()
    return group


@pytest.fixture
async def group_repository(resolver: Resolver) -> GroupRepository:
    return await resolver(GroupRepository)
