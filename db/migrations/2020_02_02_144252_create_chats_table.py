from orator.migrations import Migration


class CreateChatsTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('chats') as table:
            table.increments('id')
            table.integer('chat_id').unique()
            table.timestamps()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('chats')
