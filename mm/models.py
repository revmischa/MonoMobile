from mm.app import db, app
from flask import url_for
from sqlalchemy import func, DDL, Table
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, Text, TIMESTAMP, Boolean
from sqlalchemy.event import listen
from functools import partial
import logging

log = logging.getLogger(__name__)


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

    @classmethod
    def get_default(cls):
        # for now just return first
        # this should look up by name from config
        net = cls.query.first()
        return net


class Subscriber(db.Model):
    id = Column(Integer, primary_key=True)
    created = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    network_id = Column(Integer, ForeignKey('network.id', name='sub_net_fk'), nullable=False)
    network = db.relationship(Network, back_populates='subscribers', foreign_keys=[network_id])
    sim_sid = Column(Text, nullable=False)
    iccid = Column(Text, nullable=True)
    email = Column(Text, nullable=True)
    nickname = Column(Text, nullable=True)
    stripe_customer_id = Column(Text)
    extension = Column(Integer, nullable=False)
    sent_welcome_message = Column(Boolean, nullable=False, server_default='F')
    onboarded = Column(Boolean, nullable=False, server_default='F')

    def get_ext_display(self):
        prefix = app.config['DIALPLAN_EXT_DIAL_PREFIX']
        return f'{prefix}{self.extension}'

    def get_dest_addr(self):
        return f'sim:{self.sim_sid}'

    def configure_webhooks(self):
        from mm import twil
        sid = self.sim_sid
        update = dict(
            voice_method='POST',
            voice_url=url_for('twil_voice_out', _external=True),
            sms_method='POST',
            sms_url=url_for('twil_sms_out', _external=True),
            rate_plan=app.config.get('RATE_PLAN'),
            status='active',
        )
        if self.nickname:
            update['unique_name'] = f"{self.id}:{self.nickname}"
        twil.wireless.sims(sid).update(**update)
        log.info(f"Configured webhooks for {sid} ({self.nickname})")

    def send_registered_messsage(self):
        from mm import twil
        sid = self.sim_sid
        # problem: can't text a SIM directly
        twil.messages.create(
            body=f"Welcome to the {self.network.name} network! Your extension is {self.get_ext_display()}.",
            from_=app.config['MASTER_PHONE_NUMBER'],
            to=f"sim:{self.sid}",
        )


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
