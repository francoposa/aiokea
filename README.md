# Aiokea
**Aiokea** is an async Python framework organizing popular libraries into clean architecture layers suitable for building REST APIs and web services.

**Aiokea** is a portmanteau of the `aio` prefix used to denote many async I/O Python libraries and `Ikea`, to evoke that Aiokea provides the components and tools create an application and encourages you to put it together yourself, much like a piece of Ikea furniture.

**Aiokea** intends to provide implementations based on more than one popular Python library for each architecture layer, allowing you to pick and choose while still following the Aiokea vision for application structure, in the same way that Ikea allows you put together various styles of furniture together and still acheive a cohesive room design.

### Aiokea Principles

Aiokea's design vision is influenced by SOLID principles plus a few more:

##### Explicit over Implicit; Boilerplate over Magic

When you put it together yourself, know how to take it apart. Heavy, impenetrable, hyperdynamic, tightly coupled patterns such as ORMs are avoided. These magical creatures and their many-tentacled features increase initial productivity but eventually drag you down when your needs no longer align with the patterns, opinions, and limitations of the library.

### Aiokea Supported Libraries

The first version of Aiokea intends to support the following libraries. These choices are not based on any particular method or benchmarks -  these are just what I am already familiar with.
* `aiohttp`: async web server and http framework
* `aiopg`: async Postgres driver with SQLAlchemy support
* `attrs`: easy creation and validation of usecase-layer classes
* `marshmallow`: adapter for marshaling raw infrastructure-layer data to and from usecase-layer objects
* `alembic`: database migration and schema management with SQLAlchemy support

In the future, I plan to expand Aiokea to support other libraries, with an emphasis on libraries that are more performant and/or popular than the original set. These include:
* `starlette` - highly performant async-compatible http framework
* `asyncpg` - highly performant Postgres driver with SQLAlchemy support and no dependency on psycopg2

API Design
* GET request filter query design influenced by the LHS Brackets recommendation here: https://www.moesif.com/blog/technical/api-design/REST-API-Design-Filtering-Sorting-and-Pagination/

Local DB Migration:
```
$ psql -U postgres -c "CREATE DATABASE aiokea_test;"
$ alembic upgrade head
$ alembic -x db=aiokea_test upgrade head
```
