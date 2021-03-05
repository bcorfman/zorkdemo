"""models.py for DB Models"""

from datetime import datetime
import peewee as pw
from playhouse.db_url import connect

database = pw.DatabaseProxy()


class BaseModel(pw.Model):
    class Meta:
        database = database


class AdventureStore(BaseModel):
    """AdventureStore DB model for saving Adventure state save data"""

    session_id = pw.CharField(unique=True)
    create_ts = pw.DateTimeField(default=datetime.utcnow)
    updated_ts = pw.DateTimeField(default=datetime.utcnow)
    save_data = pw.CharField(default="")

    def save(self, *args, **kwargs):
        """overriden save method to update updated_ts"""
        self.updated_ts = datetime.utcnow()
        super().save(*args, **kwargs)

    def to_json(self):
        return {
            "session_id": self.session_id,
            "create_ts": self.create_ts.isoformat(),
            "updated_ts": self.updated_ts.isoformat(),
            "save_data": self.save_data,
        }


def init_db(connection_url):
    database.initialize(connect(connection_url))
    try:
        database.create_tables([AdventureStore], safe=True)
        database.close()
    except pw.OperationalError:
        pass


def create_tables():
    database.create_tables([AdventureStore], safe=True)


def drop_tables():
    database.drop_tables([AdventureStore])
