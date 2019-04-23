import click
import app
from app import db


@app.cli.command()
@click.option('--drop', is_flag = True, help='Create after drop.') #设置选项
def initdb(drop):
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')

