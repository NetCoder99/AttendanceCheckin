from classes.imports.import_common import getImportSession, cloneRecord
from classes.sqlite_procs import getDbPath, getDbSession
from models import Belts
from datetime import datetime

def importBelts(srce_db_name: str, dest_db_name: str):
    excep_list    = []
    import_counts = {'records_read' : 0, 'records_inserted' : 0, 'records_updated' : 0, 'records_error' : 0 }
    try:
        srce_db = getDbPath(srce_db_name)
        dest_db = getDbPath(dest_db_name)

        db_session_srce = getImportSession(srce_db)
        db_session_dest = getImportSession(dest_db)

        print(f'srce_db: {srce_db}')

        updateDateTime       = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for import_record in db_session_srce.query(Belts):
            import_record_dest = cloneRecord(import_record)
            import_record_dest.createDateTime = import_record_dest.createDateTime if import_record_dest.createDateTime else updateDateTime
            import_record_dest.updateDateTime = updateDateTime
            merge_response = db_session_dest.merge(import_record_dest)
            db_session_dest.commit()

    except Exception as ex:
        print("\033[31m" + str(ex) + "\033[0m \n\n")
        excep_list.append(ex)

    if len(excep_list) > 0:
        return {'import_error' : {'import_error' : str(excep_list[0])}}
    else:
        return import_counts
