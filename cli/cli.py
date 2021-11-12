import shutil
from pathlib import Path

import click

from .customer_pos import Customer, customer
from .item_pos import Item, item
from .order_pos import Order, order


@click.command('init', help='Initialize app')
def init() -> None:
    try:
        Customer.init()
        Item.init()
        Order.init()
        print('Initialization complete')
    except OSError:
        print('Error occurred during initialization')


@click.command('destroy', help='Destroy initialized app')
def destroy() -> None:
    try:
        shutil.rmtree(Path.cwd() / 'db')
        print('App destroyed')
    except OSError:
        pass


@click.group()
def cli() -> None:
    pass


cli.add_command(init)
cli.add_command(destroy)
cli.add_command(customer)
cli.add_command(item)
cli.add_command(order)
