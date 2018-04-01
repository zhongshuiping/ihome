from flask_migrate import Migrate, MigrateCommand
from flask_migrate import Manager
from ihome import genarate, db
from ihome.models import *

app = genarate('dev')


manage = Manager(app)
Migrate(app, db)
manage.add_command('db', MigrateCommand)

if __name__ == '__main__':
    print(app.url_map)
    manage.run()
