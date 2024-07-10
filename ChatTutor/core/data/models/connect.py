from sqlmodel import Field, Session, SQLModel, create_engine, select, delete, MetaData, Table
import os
import threading
import functools


def synchronized(wrapped):
    lock = threading.Lock()

    @functools.wraps(wrapped)
    def _wrap(*args, **kwargs):
        print("Calling '%s' with Lock %s", (wrapped.__name__, id(lock)))
        with lock:
            return wrapped(*args, **kwargs)

    return _wrap


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            print(cls)
            cls._locked_call(*args, **kwargs)
        return cls._instances[cls]

    @synchronized
    def _locked_call(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)


def drop_table(engine, table_name):
    metadata = SQLModel.metadata
    # metadata.create_all(bind=engine)
    table = Table(table_name, metadata)
    table.drop(engine)


# Python3
class Connection(metaclass=Singleton):
    def __init__(self) -> None:
        print("Initializing DataBase connection")
        connection_string = "mysql+pymysql://%s:%s@%s/%s" % (
            os.getenv("SQL_DB_USER"),
            os.getenv("SQL_DB_PASSWORD"),
            os.getenv("SQL_DB_HOST"),
            os.getenv("SQL_DB"),
        )
        self.engine = create_engine(connection_string, echo=True)
        # Only use these when resetting the tables

        SQLModel.metadata.create_all(self.engine)

    def get_engine(self):
        return self.engine

    def session(self):
        return Session(self.engine)
