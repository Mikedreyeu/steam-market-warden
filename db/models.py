from orator import Model
from orator.orm import has_many

from settings import db


Model.set_connection_resolver(db)


class Chat(Model):
    __table__ = 'chats'

    __fillable__ = ['chat_id']

    @has_many
    def jobs(self):
        return Job


class Job(Model):
    __table__ = 'jobs'

    __fillable__ = ['job_blob']
