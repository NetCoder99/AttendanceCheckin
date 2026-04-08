from flask import render_template

from classes.create_procs import getAllTableDefinitions
from models import Base

def displayAllTables():
    table_defs = getAllTableDefinitions()
    all_models = getAllModelDefinitions()
    return render_template('tables.html')


def getAllModelDefinitions():
    all_models = Base.metadata
    print("List of all registered models (table names):")
    for table_name in all_models.tables.keys():
        print(
            f"* [Table: {table_name}]")  # The URL link will point to the general docs

    return all_models.tables.keys()