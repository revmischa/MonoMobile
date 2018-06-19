from mm.app import db
from sqlalchemy import func, DDL, Table
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, Text, TIMESTAMP, Boolean
from sqlalchemy.event import listen
from functools import partial


def on_table_create(class_, ddl):
    """Run DDL on model class `class_` after creation, whether in migration or in deploy (as in tests)."""
    def listener(tablename, ddl, table, bind, **kw):
        if table.name == tablename:
            ddl(table, bind, **kw)

    listen(Table,
           'after_create',
           partial(listener, class_.__table__.name, ddl))


class Network(db.Model):
    id = Column(Integer, primary_key=True)
    created = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    name = Column(Text, nullable=False)
    subscribers = db.relationship('Subscriber', back_populates='network')
    subscribers_query = db.relationship('Subscriber', back_populates='network', lazy='dynamic')


class Subscriber(db.Model):
    id = Column(Integer, primary_key=True)
    created = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    network_id = Column(Integer, ForeignKey('network.id', name='sub_net_fk'), nullable=False)
    network = db.relationship(Network, back_populates='subscribers', foreign_keys=[network_id])
    sim_sid = Column(Text, nullable=False)
    email = Column(Text, nullable=True)
    nickname = Column(Text, nullable=True)
    stripe_customer_id = Column(Text)
    extension = Column(Integer, nullable=False)
    sent_welcome_message = Column(Boolean, nullable=False, server_default='F')
    onboarded = Column(Boolean, nullable=False, server_default='F')


# auto-generate extensions for new subscribers
on_table_create(
    Subscriber,
    DDL("""
    CREATE FUNCTION gen_subscriber_extension() RETURNS trigger AS $$
    DECLARE
      MAX_EXT INTEGER;
    BEGIN
      -- get max extension from network
      SELECT COALESCE(MAX(extension), 0) INTO MAX_EXT FROM subscriber WHERE network_id=NEW.network_id;
      NEW.extension = MAX_EXT + 1;
      RETURN NEW;
    END;
    $$ LANGUAGE 'plpgsql';

    CREATE TRIGGER subscriber_gen_extension BEFORE INSERT ON subscriber
      FOR EACH ROW EXECUTE PROCEDURE gen_subscriber_extension();
"""))
