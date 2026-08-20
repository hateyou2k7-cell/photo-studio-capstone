from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from api.schemas.auth import LoginUserRequestSchema, LoginUserResponseSchema, RigisterUserRequestSchema, RigisterUserResponseSchema
from api.schemas.todo import TodoRequestSchema, TodoResponseSchema
from api.schemas.room import RoomRequestSchema, RoomResponseSchema
from api.schemas.space_image import SpaceImageResponseSchema
from api.schemas.space_schedule import SpaceScheduleRequestSchema, SpaceScheduleResponseSchema
from api.schemas.space import SpaceRequestSchema, SpaceResponseSchema

spec = APISpec(
    title="Todo API",
    version="1.0.0",
    openapi_version="3.0.2",
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
)

# Đăng ký schema để tự động sinh model
spec.components.schema("TodoRequest", schema=TodoRequestSchema)
spec.components.schema("TodoResponse", schema=TodoResponseSchema)
spec.components.schema("LoginUserRequest", schema= LoginUserRequestSchema)
spec.components.schema("LoginUserResponse", schema= LoginUserResponseSchema)
spec.components.schema("RigisterUserRequest", schema= RigisterUserRequestSchema)
spec.components.schema("RigisterUserResponse", schema= RigisterUserResponseSchema)
spec.components.schema("RoomRequest", schema=RoomRequestSchema)
spec.components.schema("RoomResponse", schema=RoomResponseSchema)
spec.components.schema("SpaceImageResponse", schema=SpaceImageResponseSchema)
spec.components.schema("SpaceScheduleRequest", schema=SpaceScheduleRequestSchema)
spec.components.schema("SpaceScheduleResponse", schema=SpaceScheduleResponseSchema)
spec.components.schema("SpaceRequest", schema=SpaceRequestSchema)
spec.components.schema("SpaceResponse", schema=SpaceResponseSchema)