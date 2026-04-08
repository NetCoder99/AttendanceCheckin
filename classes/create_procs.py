from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import sqlite

from models import Belts, Base


def getAllTableDefinitions():
    excep_list = []
    for mapper in Base.registry.mappers:
        try:
            model_class = mapper.class_
            print(f"Model Name: {model_class.__name__}")
            print(f"Table Name: {model_class.__tablename__}")
            table_def = CreateTable(mapper.tables[0]).compile(dialect=sqlite.dialect())
            print(f"Table DDL: {table_def}")
        except Exception as ex:
            print("\033[31m" +  str(ex) + "\033[0m \n\n")
            excep_list.append(ex)

    if len(excep_list) > 0:
        return excep_list[0]

