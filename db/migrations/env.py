import asyncio 
import os 
from logging.config import fileConfig 

from sqlalchemy import pool 
from sqlalchemy.engine import Connection 
from sqlalchemy.ext.asyncio import async_engine_from_config 

from alembic import context 

config = context.config  # load all the configuration from alembic.ini file

if config.config_file_name is not None:
    fileConfig(config.config_file_name)  #enable loggings using the filename (root logger, sqlalchemy logger, alembic logger)
    

database_url = os.environ.get("DATABASE_URL", config.get_main_option("sqlalchemy.url"))
config.set_main_option("sqlalchemy.url", database_url)

target_metadata = None 


'''
Run migration will run all the migrations without connecting to the database.
This is needed for debugging purpose

Although it is totally optional
'''
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url = url,
        target_metadata = target_metadata,
        literal_binds = True,
        dialect_opts = {"paramstyle": "named"},
        
    )
    
    with context.begin_transaction():
        context.run_migration()

'''
Actual execution of data migration using database connection.
It will attach the database connection to the alembic.
All the migration files which are in the migrations >> version folder will be executed
'''
def do_run_migrations(connection: Connection) -> None:
    context.configure(connection = connection, target_metadata = target_metadata)
    with context.begin_transaction():
        context.run_migration()

'''
Migrations should be able to run asynchronously.
It will async db engine from alembic.ini
All the configurations from alembic.ini will be read 
'''
async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix = "sqlalchemy.",
        poolclass = pool.NullPool
        
    )
    
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()
    

def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())
    

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
    
    
    

        
