from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
profiles = Table('profiles', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('user_id', Integer),
    Column('name', String(length=128)),
    Column('address', String(length=128)),
    Column('message', String(length=128)),
    Column('front_image_URL', String(length=128)),
    Column('back_image_URL', String(length=128)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['profiles'].columns['back_image_URL'].create()
    post_meta.tables['profiles'].columns['front_image_URL'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['profiles'].columns['back_image_URL'].drop()
    post_meta.tables['profiles'].columns['front_image_URL'].drop()
