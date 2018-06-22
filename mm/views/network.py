from mm import app, db, twil
from flask import request
from mm.views import APIBadRequestError
from mm.models import Subscriber, Network
from flask_apispec import use_kwargs, marshal_with
from marshmallow import Schema, fields

class SubscriberSchema(Schema):
    nickname = fields.Str()
    extension = fields.Int()
    extension_display = fields.Function(lambda s: s.get_ext_display())

class NetworkSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    subscribers = fields.Nested(SubscriberSchema, many=True)



@app.route('/api/network', methods=['GET'])
@marshal_with(NetworkSchema(strict=True, many=True))
def api_network_list():
    return Network.query.all()


@app.route('/api/network/<int:net_id>', methods=['GET'])
@marshal_with(NetworkSchema(strict=True))
def api_network_info(net_id):
    net = Network.query.get_or_404(net_id)
    return net
