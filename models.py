import peewee
from dynaconf import settings

db = peewee.SqliteDatabase(settings.BOT_DATABASE)


class Status(peewee.Model):
    is_open = peewee.BooleanField()
    date = peewee.DateTimeField()
    last_change = peewee.DateTimeField()
    who = peewee.CharField(null=True)
    n_unknown_macs = peewee.IntegerField(null=True)

    class Meta:
        database = db
