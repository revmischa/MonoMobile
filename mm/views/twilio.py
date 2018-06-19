from mm import app, voice_dialplan, sms_dialplan
from mm.types import TwilioCallbackRequest
from flask import request


@app.route('/sms/out', methods=['POST'])
def twil_sms_out():
    req: TwilioCallbackRequest = request.form
    print(req.__class__)
    import pprint
    pprint.pprint(req)
    to: str = req['To']
    return sms_dialplan.handle_outbound_sms(to, req)

@app.route('/voice/out', methods=['POST'])
def twil_voice_out():
    req: TwilioCallbackRequest = request.form
    print(req.__class__)
    import pprint
    pprint.pprint(req)
    to: str = req['To']
    return voice_dialplan.handle_outbound_call(to, req)

@app.route('/send-test')
def send_test_sms():
    from mm import twil
    message = twil.messages \
                    .create(
                        body="Hi from Monocle Mobile!",
                        from_='+15104078539',
                        # to='sim:DE0256f9649bc4fbbc65d3d4c4c55f08b6'
                        to='+15104078539'
                    )
