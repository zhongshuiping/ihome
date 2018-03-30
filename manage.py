import sys
import os
sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)))
from flask import Flask
from flask_migrate import Migrate, MigrateCommand
from flask_migrate import Manager
from config import Config
from ihome import app, db

manage = Manager(app)
Migrate(app, db)
manage.add_command('db', MigrateCommand)


if __name__ == '__main__':

    manage.run()
