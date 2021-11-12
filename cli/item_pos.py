import json
import os
import uuid
from pathlib import Path

import click


class Item:
    __path = 'database/items'

    def __init__(self, code=None, name=None, price=None, quantity=None) -> None:
        self.code = code
        self.name = name
        self.price = price
        self.quantity = quantity

    @classmethod
    def init(cls):
        Path(Path.cwd() / cls.__path).mkdir(parents=True, exist_ok=True)

    def save(self):
        data = {
            'code': self.code,
            'name': self.name,
            'price': self.price,
            'quantity': self.quantity
        }
        if self.code is None:
            self.code = str(uuid.uuid4())
            data['code'] = self.code
        with open(f'{self.__path}/{self.code}.json', 'w') as file:
            json.dump(data, file)

    @classmethod
    def __load(cls, code):
        try:
            with open(f'{cls.__path}/{code}', 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return None

    @classmethod
    def find_by_id(cls, code):
        data = cls.__load(f'{code}.json')
        if data is None:
            return None
        return Item(**data)

    @classmethod
    def get_all(cls):
        files = os.listdir(cls.__path)
        items = []
        for file in files:
            data = cls.__load(file)
            if data is not None:
                items.append(Item(**data))
        return items

    @classmethod
    def search(cls, keyword: str):
        files = os.listdir(cls.__path)
        items = []
        for file in files:
            data = cls.__load(file)
            if data is not None:
                for key in data:
                    if keyword.lower() in str(data[key]).lower():
                        items.append(Item(**data))
        return items

    def alter(self, name=None, price=None, quantity=None):
        if name is not None:
            self.name = name
        if price is not None:
            self.price = price
        if quantity is not None:
            self.quantity = quantity
        self.save()

    def delete(self):
        if os.path.exists(f'{self.__path}/{self.code}.json'):
            os.remove(f'{self.__path}/{self.code}.json')

    def __str__(self):
        return f'Item(code={self.code}, name={self.name}, price={self.price}, quantity={self.quantity})'

    def __repr__(self):
        return f'Item(code={self.code}, name={self.name}, price={self.price}, quantity={self.quantity})'


@click.command('create', help='Create item')
@click.option('--name', prompt='Item name', required=True)
@click.option('--price', prompt='Item price', required=True, type=float)
@click.option('--quantity', prompt='Item quantity', required=True, type=int)
def create(name, price, quantity) -> None:
    item = Item(name=name, price=price, quantity=quantity)
    item.save()
    print('Item has created:', item)


@click.command('find', help='Find a item by code')
@click.option('--code', prompt='Item code', required=True)
def find(code) -> None:
    item = Item.find_by_id(code)
    print(item)


@click.command('all', help='Get All items')
@click.option('--limit', type=int, required=False)
def all(limit) -> None:
    items = Item.get_all()
    for idx, cus in enumerate(items[:limit]):
        print(f'{idx + 1}.', cus)


@click.command('search', help='Search items')
@click.option('--limit', type=int, required=False)
@click.option('--keyword', prompt='Keyword', required=True)
def search(limit, keyword) -> None:
    items = Item.search(keyword)
    for idx, cus in enumerate(items[:limit]):
        print(f'{idx + 1}.', cus)


@click.command('update', help='Update item')
@click.option('--code', prompt='Item code', required=True,
              help='If you do not know item code run item all or search command')
@click.option('--name', required=False)
@click.option('--price', required=False, type=float)
@click.option('--quantity', required=False, type=int)
def update(code, name, price, quantity) -> None:
    item = Item.find_by_id(code)
    if item is None:
        print('No item found')
    else:
        item.alter(name=name, price=price, quantity=quantity)
        print('Item has updated', item)


@click.command('remove', help='Remove a item by code')
@click.option('--code', prompt='Item code', required=True)
def remove(code) -> None:
    item = Item.find_by_id(code)
    if item is None:
        print('No item found')
    else:
        item.delete()
        print('Item has deleted', item)


@click.group()
def item():
    pass


item.add_command(create)
item.add_command(find)
item.add_command(all)
item.add_command(update)
item.add_command(remove)
item.add_command(search)
