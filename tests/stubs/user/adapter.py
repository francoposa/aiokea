from marshmallow import fields

from aiokea.http.adapters import BaseHTTPSchema, BaseHTTPAdapter
from tests.stubs.user.struct import User


class UserHTTPSchema(BaseHTTPSchema):
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
        super().__init__(schema=UserHTTPSchema(), struct_class=User)
