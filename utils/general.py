import sqlite3

def init_db_connection():
    cn = sqlite3.connect('hospital.db')
    cn.row_factory = sqlite3.Row
    return cn

def convert_records_to_dicts(cursor, records):
    column_names = [desc[0] for desc in cursor.description]
    records_list = [dict(zip(column_names, record)) for record in records]
    return records_list

def convert_single_record_to_dict(cursor, record):
    column_names = [desc[0] for desc in cursor.description]
    record_dict = dict(zip(column_names, record))
    return record_dict