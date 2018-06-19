from mm import app, db
from flask import request
from mm.views import APIBadRequestError
from mm.models import Subscriber, Network


@app.route('/api/register', methods=['POST'])
def api_register():
    vals = request.get_json(force=True)
    sim_sid = vals.get('sim_sid')
    if not sim_sid:
        raise APIBadRequestError('sim_sid is required')

    network_id = vals.get('network_id')
    if not network_id:
        raise APIBadRequestError('network_id is required')
    network = Network.query.get(network_id)
    if not network:
        raise APIBadRequestError("invalid network")

    # look for an existing subscriber row
    sub = network.subscribers_query.filter_by(sim_sid=sim_sid).one_or_none()
    if not sub:
        # TODO: validate SID
        sub = Subscriber(sim_sid=sim_sid)
        network.subscribers.append(sub)
        # db.session.add(sub)  # insert the subscriber row

    # update row
    nickname = vals.get('nickname')
    sub.nickname = nickname
    db.session.commit()

    return "ok"
