"""Functionality for routing calls and messages."""
from twilio.twiml.messaging_response import MessagingResponse, Body, Message
from twilio.twiml.voice_response import VoiceResponse, Dial, Sim, Conference, Play
from mm.types import TwiML, TwilioCallbackRequest
from mm.models import Subscriber, Network
from typing import Optional
from mm import app
import logging

log = logging.getLogger(__name__)


class Dialplan:
    EXT_DIAL_PREFIX = app.config['DIALPLAN_EXT_DIAL_PREFIX']

    def make_message_response(self, from_: str, to: str, text: str) -> TwiML:
        """Return a text message."""
        response = MessagingResponse()
        response.message(text, to=from_, from_=to)
        return str(response)

    def make_say_response(self, text: str) -> TwiML:
        """Say something."""
        response = VoiceResponse()
        response.say(text)
        return str(response)

    def make_dialout_response(self, *, sim: str=None, to: str=None, from_: str=None) -> TwiML:
        """Dial a number."""
        response = VoiceResponse()
        if from_:
            dial = Dial(caller_id=f'+{from_}')
        else:
            dial = Dial()
        if sim:
            dial.sim(sim)
        elif to:
            dial.number(to)
        else:
            raise Exception("dialout response did not get anything to dial")
        response.append(dial)
        return str(response)

    def get_subscriber(self, sim_sid: str) -> Optional[Subscriber]:
        """Look up subscriber by SIM."""
        if sim_sid.startswith('sim:'):
            sim_sid = sim_sid.split('sim:', maxsplit=1)[0]
        return Subscriber.query.filter_by(sim_sid=sim_sid).one_or_none()

    def get_subscriber_by_dialed_number(self, *, network: Network, to: str) -> Optional[Subscriber]:
        """Match a subscriber in a network by dialed prefix/extension."""
        # remove dial prefix
        ext = to.replace(self.EXT_DIAL_PREFIX, '', 1)
        if not ext:
            return None

    def get_subscriber(self, sim_sid: str) -> Optional[Subscriber]:
        """Look up subscriber by SIM."""
        if sim_sid.startswith('sim:'):
            sim_sid = sim_sid.split('sim:')[1]
        return Subscriber.query.filter_by(sim_sid=sim_sid).one_or_none()

    def get_subscriber_by_dialed_number(self, *, network: Network, to: str) -> Optional[Subscriber]:
        """Match a subscriber in a network by dialed prefix/extension."""
        # remove dial prefix
        ext = to.replace(self.EXT_DIAL_PREFIX, '', 1)
        if not ext:
            return None

        # look up subscriber in this network with ext
        sub = network.subscribers_query.filter_by(extension=ext).one_or_none()
        return sub

    def get_register_url(self):
        return app.config['REGISTER_URL']

class SMSDialplan(Dialplan):

    def handle_outbound_sms(self, from_: str, to: str, req: TwilioCallbackRequest):
        sub = self.get_subscriber(sim_sid=from_)
        if not sub:
            return self.make_message_response(from_, to, f"You need to register with the network! Go to {self.get_register_url()}")

        if to == '420':
            return self.make_message_response(from_, to, "smoke weed EVERY day !")

        if len(to) < 10:
            return self.make_message_response(from_, to, """Ur ext: {sub.get_ext_display()}
            420: test""")

        return self.make_message_response(from_, to, "SMS outbound isn't enabled yet")


class VoiceDialplan(Dialplan):
   def handle_outbound_call(self, from_: str, to: str, req: TwilioCallbackRequest):
       # look up subscriber
       sub = self.get_subscriber(sim_sid=from_)
       if not sub:
           log.warning(f"no subscriber found for outbound call from {from_}")
           return self.make_say_response(f'You need to register with the network! Go to {self.get_register_url()}')

       # are they trying to dial a subscriber by extension?
       print(self.EXT_DIAL_PREFIX)
       if to[1:].startswith(self.EXT_DIAL_PREFIX):  # strip +
           dest_sub = self.get_subscriber_by_dialed_number(network=sub.network, to=to[1:])
           if dest_sub:
               return self.make_dialout_response(sim=dest_sub.sim_sid, from_=sub.get_ext_display())

       # we dont know what they are trying to do
       # should just try placing a normal call
       if len(to) < 10:
           return self.make_say_response("Sorry, this number isn't recognized. Text 42 for help.")

       # do dialout...
       return self.make_dialout_response(to=to)
