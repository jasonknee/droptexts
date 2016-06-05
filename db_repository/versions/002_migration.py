from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
profiles = Table('profiles', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('host_id', INTEGER),
    Column('name', VARCHAR(length=128)),
    Column('address', VARCHAR(length=128)),
    Column('message', VARCHAR(length=128)),
)

profiles = Table('profiles', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('user_id', Integer),
    Column('name', String(length=128)),
    Column('address', String(length=128)),
    Column('message', String(length=128)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['profiles'].columns['host_id'].drop()
    post_meta.tables['profiles'].columns['user_id'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['profiles'].columns['host_id'].create()
    post_meta.tables['profiles'].columns['user_id'].drop()
