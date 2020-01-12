from marshmallow import fields

from app.infrastructure.server.http.adapters.base import BaseSchema, BaseHTTPAdapter
from app.entities.resources.user import User


class UserSchema(BaseSchema):
    """User Serializer"""

    class Meta:
        """Meta data for UserSchema."""

        record_type = "user"
        patchable_fields = ["username", "email", "is_enabled"]

    id = fields.Str(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Str(required=True)
    is_enabled = fields.Boolean()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class UserHTTPAdapter(BaseHTTPAdapter):
    def __init__(self):
        super().__init__(schema=UserSchema(), entity_class=User)
