from sqlmodel import Field, Session, SQLModel, create_engine, select, delete
import os

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

#Python3
class Connection(metaclass=Singleton):
    def __init__(self) -> None:
        print("Initializing DataBase connection")
        connection_string = "mysql+pymysql://%s:%s@%s/%s" % (os.getenv('SQL_DB_USER'), os.getenv('SQL_DB_PASSWORD'), os.getenv('SQL_DB_HOST'), os.getenv('SQL_DB'))
        self.engine = create_engine(connection_string, echo=True)
        # SQLModel.metadata.drop_all(self.engine)
        # SQLModel.metadata.create_all(self.engine)
    
    def get_engine(self):
        return self.engine
    
    def session(self):
        return Session(self.engine)
