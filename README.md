# aiohttp-postgres
Asyncio Python CRUD app framework utilizing Clean Architecture concepts of Infrastructure, Entities, and Adapters

This "framework" utilizes the following libraries:
* aiohttp: async web framework
* aiopg: async Postgres driver with SQLAlchemy support
* attrs: easy creation and validation of entity-layer objects
* marshmallow: marshaling data between JSON web requests and entity-layer objects
* alembic: database migration and schema management with SQLAlchemy support
 
API Design
* GET request filter query design influenced by the LHS Brackets recommendation here: https://www.moesif.com/blog/technical/api-design/REST-API-Design-Filtering-Sorting-and-Pagination/

Local DB Migration:

    $ alembic upgrade head
    $ alembic -x db=aiohttp_crud_test upgrade head
