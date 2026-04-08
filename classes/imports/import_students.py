from sqlalchemy import select, create_engine, inspect
from sqlalchemy.orm import sessionmaker

from classes.sqlite_procs import getDbPath, getDbSession
from models import Students
from datetime import datetime

def importStudents(srce_db_name: str, dest_db_name: str):
    excep_list    = []
    import_counts = {'records_read' : 0, 'records_inserted' : 0, 'records_updated' : 0, 'records_error' : 0 }
    try:
        srce_db = getDbPath(srce_db_name)
        dest_db = getDbPath(dest_db_name)

        db_session_srce = getImportSession(srce_db)
        db_session_dest = getImportSession(dest_db)

        print(f'srce_db: {srce_db}')

        updateDateTime       = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # student_record_srce  = db_session_srce.query(Students).filter_by(badgeNumber=100).first()
        # student_record_dest  = cloneRecord(student_record_srce)
        # student_record_dest.createDateTime = student_record_dest.createDateTime if student_record_dest.createDateTime else updateDateTime
        # student_record_dest.updateDateTime = updateDateTime
        # db_session_dest.merge(student_record_dest)
        # db_session_dest.commit()

        for student_record in db_session_srce.query(Students):
            #student_record_srce = db_session_srce.query(Students).filter_by(badgeNumber=100).first()
            student_record_dest = cloneRecord(student_record)
            student_record_dest.createDateTime = student_record_dest.createDateTime if student_record_dest.createDateTime else updateDateTime
            student_record_dest.updateDateTime = updateDateTime
            db_session_dest.merge(student_record_dest)
            db_session_dest.commit()

    except Exception as ex:
        print("\033[31m" + str(ex) + "\033[0m \n\n")
        excep_list.append(ex)

    if len(excep_list) > 0:
        raise excep_list[0]
    else:
        return import_counts


def getImportSession(db_path: str):
    engine  = create_engine(f'sqlite:///{db_path}')
    Session = sessionmaker(bind=engine)
    return Session()


def cloneRecord(instance):
    mapper = inspect(instance).mapper
    for col in mapper.column_attrs:
        print(f'col: {col}')

    #cols = [c.key for c in mapper.column_attrs if not c.primary_key]
    cols = [c.key for c in mapper.column_attrs]
    print(f'cols: {cols}')
    data = {c: getattr(instance, c) for c in cols}
    return instance.__class__(**data)