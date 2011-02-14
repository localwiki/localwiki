


= Migrations / syncdb =
Each versioned model has a corresponding *_history table.  So when you change the schema of models you have versioned you'll need to execute similar SQL / migrations on the history tables as your model tables.

For instance:

  * Model 'member' is stored in my members_member table.  I'd normally run (postgres, adjust accordingly) ALTER TABLE members_member ADD COLUMN newcolumn varchar(10);  Because the members object is set to be a versioned model, I'll also want to run ALTER TABLE members_member_history ADD COLUMN newcolumn varchar(10);

  * I haven't used any of the automated Django schema migration utilities, but I assume they will either 1) work automatically, as they will detect the schema change or 2) need a bit of direction to do whatever they do to the base model to the versioned model as well.

Because there's no magic here -- there's really a separate _history table for each of your model's tables, migrations should be straightforward.
