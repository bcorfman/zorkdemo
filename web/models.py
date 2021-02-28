"""models.py for DB Models"""

from datetime import datetime
import peewee as db
from playhouse.flask_utils import FlaskDB

db_wrapper = FlaskDB()


class AdventureStore(db_wrapper.Model):
    """AdventureStore DB model for saving Adventure state save data"""

    session_id = db.CharField(unique=True)
    create_ts = db.DateTimeField(default=datetime.utcnow)
    updated_ts = db.DateTimeField(default=datetime.utcnow)
    save_data = db.CharField(default="")

    def save(self, *args, **kwargs):
        """overriden save method to update updated_ts"""
        self.updated_ts = datetime.utcnow()
        super().save(*args, **kwargs)
