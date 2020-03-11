from marshmallow import fields

from aiokea.rest.adapters import BaseSchema, BaseHTTPAdapter
from tests.stubs.users.struct import User


class UserSchema(BaseSchema):
    class Meta:
        patchable_fields = ["username", "email", "is_enabled"]

    id = fields.Str(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Str(required=True)
    is_enabled = fields.Boolean()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class UserHTTPAdapter(BaseHTTPAdapter):
    def __init__(self):
        super().__init__(schema=UserSchema(), struct_class=User)
