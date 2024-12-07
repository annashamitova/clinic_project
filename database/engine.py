from sqlalchemy import Engine, create_engine
from config import URL


def get_engine() -> Engine:
    engine = create_engine(
        url=URL,
        echo=True,
        pool_size=2,
        pool_pre_ping=True)
    return engine
