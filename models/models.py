from orator import Model

from settings import db

Model.set_connection_resolver(db)


class User(Model):
    __table__ = 'users'
