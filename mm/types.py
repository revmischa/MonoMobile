from typing import Dict, Optional, Union, List
import twilio.twiml

JSONV = Optional[Union[Dict, List, int, str, bool]]

TwilioCallbackRequest = Dict[str, JSONV]
TwiML = twilio.twiml.TwiML
