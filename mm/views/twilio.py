from mm import app, voice_dialplan, sms_dialplan
from mm.types import TwilioCallbackRequest
from flask import request


@app.route('/sms/out', methods=['POST'])
def twil_sms_out():
    req: TwilioCallbackRequest = request.form
    print(req.__class__)
    import pprint
    pprint.pprint(req)
    from_: str = req['From']
    to: str = req['To']
    return sms_dialplan.handle_outbound_sms(from_=from_, to=to, req=req)

@app.route('/voice/out', methods=['POST'])
def twil_voice_out():
    req: TwilioCallbackRequest = request.form
    print(req.__class__)
    import pprint
    pprint.pprint(req)
    from_: str = req['From']
    to: str = req['To']
    return voice_dialplan.handle_outbound_call(from_=from_, to=to, req=req)

@app.route('/send-test')
def send_test_sms():
    from mm import twil
    message = twil.messages \
                    .create(
                        body="Hi from Monocle Mobile!",
                        from_='+15104078539',
                        to='sim:DEab9edfc32ff90819cdde794c6a2d917f'
                        # to='+15104078539'
                    )
