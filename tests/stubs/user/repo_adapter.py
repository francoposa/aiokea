from marshmallow import fields

from aiokea.repos.adapters import (
    BaseMarshmallowRepoSchema,
    BaseMarshmallowSQLAlchemyRepoAdapter,
)
from tests.stubs.user.entity import User


class UserRepoSchema(BaseMarshmallowRepoSchema):
    id = fields.Str(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Str(required=True)
    is_enabled = fields.Boolean()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class UserRepoAdapter(BaseMarshmallowSQLAlchemyRepoAdapter):
    def __init__(self):
        super().__init__(schema=UserRepoSchema(), entity_class=User)
