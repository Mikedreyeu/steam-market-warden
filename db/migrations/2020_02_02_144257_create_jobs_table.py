from orator.migrations import Migration


class CreateJobsTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('jobs') as table:
            table.increments('id')
            table.binary('job_blob')
            table.integer('chat_id').unsigned().nullable()
            table.foreign('chat_id')\
                .references('id').on('chats')\
                .on_delete('cascade')
            table.timestamps()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('jobs')
