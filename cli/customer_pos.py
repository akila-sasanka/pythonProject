import json
import os
import uuid
from pathlib import Path

import click


class Customer:
    __path = 'database/customers'

    def __init__(self, id=None, name=None, address=None, salary=None) -> None:
        self.id = id
        self.name = name
        self.address = address
        self.salary = salary

    @classmethod
    def init(cls):
        Path(Path.cwd() / cls.__path).mkdir(parents=True, exist_ok=True)

    def save(self):
        data = {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'salary': self.salary
        }
        if self.id is None:
            self.id = str(uuid.uuid4())
            data['id'] = self.id
        with open(f'{self.__path}/{self.id}.json', 'w') as file:
            json.dump(data, file)

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
        return Customer(**data)

    @classmethod
    def get_all(cls):
        files = os.listdir(cls.__path)
        customers = []
        for file in files:
            data = cls.__load(file)
            if data is not None:
                customers.append(Customer(**data))
        return customers

    @classmethod
    def search(cls, keyword: str):
        files = os.listdir(cls.__path)
        customers = []
        for file in files:
            data = cls.__load(file)
            if data is not None:
                for key in data:
                    if keyword.lower() in str(data[key]).lower():
                        customers.append(Customer(**data))
        return customers

    def alter(self, name=None, address=None, salary=None):
        if name is not None:
            self.name = name
        if address is not None:
            self.address = address
        if salary is not None:
            self.salary = salary
        self.save()

    def delete(self):
        if os.path.exists(f'{self.__path}/{self.id}.json'):
            os.remove(f'{self.__path}/{self.id}.json')

    def __str__(self):
        return f'Customer(id={self.id}, name={self.name}, address={self.address}, salary={self.salary})'

    def __repr__(self):
        return f'Customer(id={self.id}, name={self.name}, address={self.address}, salary={self.salary})'


@click.command('create', help='Create customer')
@click.option('--name', prompt='Customer name', required=True)
@click.option('--address', prompt='Customer address', required=True)
@click.option('--salary', prompt='Customer salary', required=True, type=float)
def create(name, address, salary) -> None:
    cus = Customer(name=name, address=address, salary=salary)
    cus.save()
    print('Customer has created:', cus)


@click.command('find', help='Find a customer by id')
@click.option('--id', prompt='Customer id', required=True)
def find(id) -> None:
    cus = Customer.find_by_id(id)
    print(cus)


@click.command('all', help='Get All customers')
@click.option('--limit', type=int, required=False)
def all(limit) -> None:
    customers = Customer.get_all()
    for idx, cus in enumerate(customers[:limit]):
        print(f'{idx + 1}.', cus)


@click.command('search', help='Search customers')
@click.option('--limit', type=int, required=False)
@click.option('--keyword', prompt='Keyword', required=True)
def search(limit, keyword) -> None:
    customers = Customer.search(keyword)
    for idx, cus in enumerate(customers[:limit]):
        print(f'{idx + 1}.', cus)


@click.command('update', help='Update Customer')
@click.option('--id', prompt='Customer id', required=True,
              help='If you do not know customer id run customer all or search command')
@click.option('--name', required=False)
@click.option('--address', required=False)
@click.option('--salary', required=False, type=float)
def update(id, name, address, salary) -> None:
    cus = Customer.find_by_id(id)
    if cus is None:
        print('No customer found')
    else:
        cus.alter(name=name, address=address, salary=salary)
        print('Customer has updated', cus)


@click.command('remove', help='Remove a customer by id')
@click.option('--id', prompt='Customer id', required=True)
def remove(id) -> None:
    cus = Customer.find_by_id(id)
    if cus is None:
        print('No customer found')
    else:
        cus.delete()
        print('Customer has deleted', cus)


@click.group()
def customer():
    pass


customer.add_command(create)
customer.add_command(find)
customer.add_command(all)
customer.add_command(update)
customer.add_command(remove)
customer.add_command(search)
