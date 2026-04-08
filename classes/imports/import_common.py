from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

def getTableByClassName(base, class_name):
    for mapper in base.registry.mappers:
        if mapper.class_.__name__ == class_name:
            return mapper.local_table
    return None

def getImportSession(db_path: str):
    engine  = create_engine(f'sqlite:///{db_path}')
    Session = sessionmaker(bind=engine)
    return Session()


def cloneRecord(instance):
    mapper = inspect(instance).mapper
    cols = [c.key for c in mapper.column_attrs]
    print(f'cols: {cols}')
    data = {c: getattr(instance, c) for c in cols}
    return instance.__class__(**data)