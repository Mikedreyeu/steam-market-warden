from orator.migrations import Migration


class CreateWhitelistTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('whitelist') as table:
            table.increments('id')
            table.integer('user_id').unique()
            table.timestamps()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('whitelist')
