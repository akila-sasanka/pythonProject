import datetime
import json
import os
import uuid
from pathlib import Path

import click

from .customer_pos import Customer
from .item_pos import Item


class Order:
    __path = 'database/orders'

    def __init__(self, id=None, date=None, customer_id=None, order_details=None) -> None:
        self.id = id
        self.date = date
        self.customer_id = customer_id
        self.order_details = order_details

    @classmethod
    def init(cls):
        Path(Path.cwd() / cls.__path).mkdir(parents=True, exist_ok=True)

    def save(self):
        data = {
            'id': self.id,
            'date': self.date,
            'customer_id': self.customer_id,
            'order_details': self.order_details
        }
        if self.id is None:
            self.id = str(uuid.uuid4())
            data['id'] = self.id
        with open(f'{self.__path}/{self.id}.json', 'w') as file:
            json.dump(data, file, indent=2)

    @classmethod
    def __load(cls, id):
        try:
            with open(f'{cls.__path}/{id}', 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return None

    @classmethod
    def find_by_id(cls, id):
        data = cls.__load(f'{id}.json')
        if data is None:
            return None
        return Order(**data)

    @classmethod
    def get_all(cls):
        files = os.listdir(cls.__path)
        orders = []
        for file in files:
            data = cls.__load(file)
            if data is not None:
                orders.append(Order(**data))
        return orders

    @classmethod
    def search(cls, keyword: str):
        files = os.listdir(cls.__path)
        orders = []
        for file in files:
            data = cls.__load(file)
            if data is not None:
                for key in data:
                    if keyword.lower() in str(data[key]).lower():
                        orders.append(Order(**data))
        return orders

    def alter(self, date=None, customer_id=None):
        if date is not None:
            self.date = date
        if customer_id is not None:
            self.customer_id = customer_id
        self.save()

    def delete(self):
        if os.path.exists(f'{self.__path}/{self.id}.json'):
            os.remove(f'{self.__path}/{self.id}.json')

    def __str__(self):
        return f'Order(id={self.id}, date={self.date}, customer_id={self.customer_id}, order_details={self.order_details})'

    def __repr__(self):
        return f'Order(id={self.id}, date={self.date}, customer_id={self.customer_id}, order_details={self.order_details})'


@click.command('find', help='Find an order by id')
@click.option('--id', prompt='Order id', required=True)
def find(id) -> None:
    odr = Order.find_by_id(id)
    print(odr)


@click.command('all', help='Get All orders')
@click.option('--limit', type=int, required=False)
def all(limit) -> None:
    orders = Order.get_all()
    for idx, odr in enumerate(orders[:limit]):
        print(f'{idx + 1}.', odr)


@click.command('search', help='Search orders')
@click.option('--limit', type=int, required=False)
@click.option('--keyword', prompt='Keyword', required=True)
def search(limit, keyword) -> None:
    orders = Order.search(keyword)
    for idx, odr in enumerate(orders[:limit]):
        print(f'{idx + 1}.', odr)


@click.command('update', help='Update an Order')
@click.option('--id', prompt='Order id', required=True,
              help='If you do not know order id run customer all command')
@click.option('--date', required=False)
@click.option('--customer_id', required=False)
def update(id, date, customer_id) -> None:
    odr = Order.find_by_id(id)
    if odr is None:
        print('No order found')
    else:
        if customer_id is not None:
            cus = Customer.find_by_id(customer_id)
            if cus is None:
                print('Error: Invalid customer id')
            else:
                odr.alter(date=date, customer_id=customer_id)
                print('Order has updated', odr)
        else:
            odr.alter(date=date, customer_id=customer_id)
            print('Order has updated', odr)


@click.command('remove', help='Remove an order by id')
@click.option('--id', prompt='Order id', required=True)
def remove(id) -> None:
    odr = Order.find_by_id(id)
    if odr is None:
        print('No order found')
    else:
        odr.delete()
        print('Order has deleted', odr)


@click.command('create', help='Create an order')
@click.option('--date', help='Order date', required=False)
@click.option('--customer_id', prompt='Order customer id', required=True)
def create(date, customer_id) -> None:
    cus = Customer.find_by_id(customer_id)
    if cus is None:
        print('Error: Invalid customer id')
    else:
        print(cus)
        if date is None:
            date = str(datetime.datetime.now())
        order_details = []
        running = True
        while running:
            item_code = input('Item code: ')
            item = Item.find_by_id(item_code)
            if item is None:
                print('Error: Invalid item code')
                continue
            print(item)
            quantity = None
            while quantity is None:
                try:
                    quantity = int(input('Quantity: '))
                    if quantity < 1:
                        quantity = None
                        print('Invalid quantity')
                    elif item.quantity < quantity:
                        print('Error: Required quantity is greater than currently stock quantity')
                        quantity = None
                except ValueError:
                    print('Invalid quantity')
                    quantity = None
            unit_price = None
            while unit_price is None:
                try:
                    unit_price = float(input('Unit Price: '))
                    if unit_price < 1:
                        unit_price = None
                        print('Invalid unit price')
                except ValueError:
                    print('Invalid unit price')
                    unit_price = None
            order_details.append({
                'item_code': item_code,
                'quantity': quantity,
                'unit_price': unit_price
            })
            item.alter(quantity=item.quantity - quantity)
            close = input('Do you want to add another item to the order? (yes/no) ')
            if close.lower() != 'yes':
                running = False
        odr = Order(date=date, customer_id=customer_id, order_details=order_details)
        odr.save()
        print('Order has created:', odr)


@click.group()
def order():
    pass


order.add_command(find)
order.add_command(all)
order.add_command(update)
order.add_command(remove)
order.add_command(create)
order.add_command(search)
