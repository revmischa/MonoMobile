from flask.cli import AppGroup
import click
from mm.models import Subscriber
from mm import app


subscriber_cli = AppGroup('sub')

@subscriber_cli.command('register')
@click.argument('sim')
@click.argument('nickname')
def register_subscriber(sim, nickname):
    printf("Registering {sim} as nickname {nickname}")
