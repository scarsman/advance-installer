import os, sqlite3
import sys


## PyInstaller Default scl_db location
BASE_DIR = os.environ['LOCALAPPDATA']
DB_FILE_FTI = 'SCL_FTI3.db'
DB_FILE_Memory = 'SCL_FTI_memory.db'
DB_FILE_Memory_TEST = 'SCL_FTI_memory-TEST.db'
DB_FILE_SCL = 'scldb8.db' ##'scldb.db'
db_fti = os.path.join(BASE_DIR, DB_FILE_FTI)
db_memory = f'{BASE_DIR}%s{DB_FILE_Memory}' % os.sep
db_scl = os.path.join(BASE_DIR, DB_FILE_SCL)
db = db_scl

class DB:
    """  Database setup and properties """
    def __init__(self , DBType):
        self.db = ''

        if DBType is 'FileManagement' or DBType is "":
            self.db = db_scl
            print("IFFFFF")
        elif DBType is 'SCLFTI3':
            print("SCLFTTTT")
            self.db = db_fti
        else:
            print("ELSEEEEE")
            self.db = db_memory

        if not os.path.isfile(self.db):
            print("SCL scl_db is not Found!")
            sys.exit(0)

    def connect(self):
        """ Database object """
        print("\nDB_CONNECT ----  Connect to db\n")
        try:
            return sqlite3.connect(self.db)
        except Exception as Ex:
            print("DB_Name : " + str(self.db))
            print("EXception =>"+str(Ex))

    def close(self, db):
        """ Close database connection
        """
        print("\nDB_CONNECT ----  close to db\n")
        return db.close()


# if __name__ == "__main__":
#     db = scl_db("SCLFTI3")
#     con = db.connect()
#     print(db.connect())
