from marshmallow import fields

from app.infrastructure.server.schemas.base import BaseSchema


class UserSchema(BaseSchema):
    class Meta:
        type_ = "user"

    id = fields.Str(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Str(required=True)
    password = fields.Str(load_only=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
