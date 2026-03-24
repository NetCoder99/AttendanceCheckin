import os
import platform

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db_session = None

def getDbPath():
    if platform.system() == 'Windows':
        return os.path.join(os.getenv('APPDATA'), 'Attendance', 'AttendanceV2.db')
    else:
        return os.path.join('/', 'Attendance', 'AttendanceV2.db')

def getDbSession():
    global db_session
    if db_session is None:
        engine = create_engine(f'sqlite:///{getDbPath()}')
        Session = sessionmaker(bind=engine)
        db_session = Session()
    return db_session
