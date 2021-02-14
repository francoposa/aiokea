import uuid
from datetime import datetime

import attr
from attr.validators import instance_of, optional


@attr.s
class User:
    username = attr.ib(validator=instance_of(str))
    email = attr.ib(validator=instance_of(str))

    # Auto-generated on creation of a entity
    id = attr.ib(validator=instance_of(str))
    is_enabled = attr.ib(validator=instance_of(bool), default=True)

    # Repo auto created
    # When we create new entities in the app or from a POST, these will not be set.
    # The field values will be set by the service when records are created or updated
    # Structs that are deserialized from the service will then have these fields set
    created_at = attr.ib(validator=optional(instance_of(datetime)), default=None)
    updated_at = attr.ib(validator=optional(instance_of(datetime)), default=None)

    @id.default
    def generate_uuid(self) -> str:
        return str(uuid.uuid4())


stub_users = [
    User(username="domtoretto", email="americanmuscle@fastnfurious.com"),
    User(username="brian", email="importtuners@fastnfurious.com"),
    User(username="roman", email="ejectoseat@fastnfurious.com"),
    User(username="han", email="betterlucktomorrow@fastnfurious.com", is_enabled=False),
]
