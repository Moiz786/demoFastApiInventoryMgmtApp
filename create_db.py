import sqlalchemy.exc

from db_init import engine
from models import Base

print("Creating database ....")

try:
    print("dropping tables")
    Base.metadata.drop_all(engine)
except sqlalchemy.exc.OperationalError as e:
    print("Failed dropping existing DB....DB does not exist")

Base.metadata.create_all(engine)
