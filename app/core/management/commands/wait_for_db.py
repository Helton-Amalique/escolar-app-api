""" comando d django para a espera pela base de dados"""
import time
from psycopg2 import OperationalError as Psycopg2OpError
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """comando django para esperar pela base de dados estar disponivel """

    def handle(self, *args, **options):
        self.stdout.write('Aguardando pela base de dados...')
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2OpError, OperationalError):
                self.stdout.write('Base de dados nao disponivel,' \
                                  'aguarde 1 segundo...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('base de dados disponivel'))
