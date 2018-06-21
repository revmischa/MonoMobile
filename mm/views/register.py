from mm import app, db, twil
from flask import request
from mm.views import APIBadRequestError
from mm.models import Subscriber, Network


@app.route('/api/register', methods=['POST'])
def api_register():
    vals = request.get_json(force=True)
    iccid_last5 = vals.get('iccid_last5')
    if not iccid_last5:
        raise APIBadRequestError('iccid_last5 is required')

    email = vals.get('email')
    if not email:
        raise APIBadRequestError('Please enter an email address')

    nick = vals.get('nickname')
    if not nick:
        raise APIBadRequestError('Please enter a nickname to use on the service')

    if len(iccid_last5) != 5 or not iccid_last5.upper().endswith('F'):
        raise APIBadRequestError('Invalid ICCID. Must be five digits and end with "F"')

    network_id = vals.get('network_id')
    if network_id:
        network = Network.query.get(network_id)
        if not network:
            raise APIBadRequestError("invalid network ID")
    else:
        network = Network.get_default()
        if not network:
            raise APIBadRequestError('network_id is required')

    sim = twil.find_sim(iccid_last5=iccid_last5)
    if not sim:
        raise APIBadRequestError(f"ICCID {iccid_last5} not found.")

    sid = sim.sid

    # look for an existing subscriber row
    sub = network.subscribers_query.filter_by(sim_sid=sid).one_or_none()
    if not sub:
        # TODO: validate SID
        sub = Subscriber(sim_sid=sid)
        network.subscribers.append(sub)
        # db.session.add(sub)  # insert the subscriber row

    # update row
    nickname = vals.get('nickname')
    sub.nickname = nickname
    sub.email = email
    sub.iccid = sim.iccid
    sub.sid = sim.sid
    db.session.commit()

    sub.configure_webhooks()
    # sub.send_registered_messsage()

    return "ok"
