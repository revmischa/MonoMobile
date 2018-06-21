import twilio.rest
import twilio.rest.wireless
from mm import app
from typing import List


SIMInstance = twilio.rest.wireless.v1.sim.SimInstance


class Twil(twilio.rest.Client):
    def __init__(self, sid=None, secret=None):
        if not sid and not secret:
            sid = app.config.get('TWILIO_ACCT_SID')
            secret = app.config.get('TWILIO_AUTH_TOKEN')
        super().__init__(sid, secret)


    def find_sim(self, *, iccid_last5: str) -> SIMInstance:
        """Look up twilio SIM instance record by ICCID last 5."""
        assert len(iccid_last5) == 5
        # we don't want the 'F' on the end - it's just for decoration
        iccid_last4 = iccid_last5[0:4]
        # get list of SIMs
        sim_list: List[SIMInstance] = self.wireless.sims.list()
        # TODO: handle paging, this only returns a page
        matching = [s for s in sim_list if s.iccid.endswith(iccid_last4)]
        return matching[0] if matching else None
