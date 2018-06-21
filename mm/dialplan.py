"""Functionality for routing calls and messages."""
from twilio.twiml.messaging_response import MessagingResponse, Body, Message
from twilio.twiml.voice_response import VoiceResponse, Dial, Sim, Conference, Play
from mm.types import TwiML, TwilioCallbackRequest
from mm.models import Subscriber, Network
from typing import Optional
from mm import app


class Dialplan:
    EXT_DIAL_PREFIX = app.config['DIALPLAN_EXT_DIAL_PREFIX']

    def make_message_response(self, text: str) -> TwiML:
        """Return a text message."""
        response = MessagingResponse()
        message = Message()
        message.body(text)
        response.append(message)
        return str(response)

    def make_dialout_response(self, *, sim: str=None) -> TwiML:
        """Dial a number."""
        response = VoiceResponse()
        dial = Dial()
        if sim:
            dsim = Sim(sim)
            dial.append(dsim)
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

        # look up subscriber in this network with ext
        sub = network.subscribers_query.filter_by(extension=ext).one_or_none()
        return sub

class SMSDialplan(Dialplan):

    def handle_outbound_sms(self, from_: str, to: str, req: TwilioCallbackRequest):
        if to == '420':
            return self.make_message_response("special number")
        else:
            return self.make_message_response("unknown number")


class VoiceDialplan(Dialplan):
   def handle_outbound_call(self, from_: str, to: str, req: TwilioCallbackRequest):
       # look up subscriber
       sub = self.get_subscriber(sim_sid=from_)
       if not sub:
           raise Exception(f"no subscriber found for outbound call from {from_}")

       # are they trying to dial a subscriber by extension?
       if to.startswith(self.EXT_DIAL_PREFIX):
           dest_sub = self.get_subscriber_by_dialed_number(network=sub.network, to=to)
           if dest_sub:
               return self.make_dialout_response(sim=dest_sub.sim_sid)

        # we dont know what they are trying to do
        # should just try placing a normal call
