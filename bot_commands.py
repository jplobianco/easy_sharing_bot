import sqlite3
from datetime import datetime
from typing import List

from _sqlite3 import Error

conn = sqlite3.connect("database.db")
# conn.row_factory = sqlite3.Row


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


conn.row_factory = dict_factory


def create_database():
    create_db_sql = """
            CREATE TABLE IF NOT EXISTS service(
                chat_id INT,
                name VARCHAR(100) NOT NULL, 
                url TEXT NULL,
                created_by varchar(100) NOT NULL,
                created_in TIMESTAMP NOT NULL,
                modified_by VARCHAR(100) NULL, 
                last_modified TIMESTAMP NULL,
                PRIMARY KEY (chat_id, name)
            );

            CREATE TABLE IF NOT EXISTS account(
                chat_id INT NOT NULL,
                service_name VARCHAR(100) NOT NULL, 
                username VARCHAR(100) NOT NULL, 
                passwd VARCHAR(100) NOT NULL, 
                created_by VARCHAR(100) NOT NULL, 
                created_in TIMESTAMP NOT NULL, 
                modified_by VARCHAR(100) NULL, 
                last_modified TIMESTAMP NULL,
                PRIMARY KEY (chat_id, service_name, username),
                FOREIGN KEY (chat_id) REFERENCES service(chat_id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (service_name) REFERENCES service(name) ON DELETE CASCADE ON UPDATE CASCADE           
            );

            CREATE TABLE IF NOT EXISTS action(
                id INT AUTO_INCREMENT,
                chat_id INT NOT NULL,
                service_name VARCHAR(100) NOT NULL, 
                username VARCHAR(100) NOT NULL, 
                type CHAR(1) NOT NULL, 
                created_by VARCHAR(100) NOT NULL,
                created_in TIMESTAMP NOT NULL,
                PRIMARY KEY (id),
                FOREIGN KEY (chat_id) REFERENCES account(chat_id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (service_name) REFERENCES account(service_name) ON DELETE CASCADE ON UPDATE CASCADE
            );
            """
    try:
        c = conn.cursor()
        c.executescript(create_db_sql)
    except Error as e:
        print(e)
        exit(1)


def services(chat_id: int) -> List[dict]:
    _services = []
    try:
        cur = conn.cursor()
        sql = """SELECT * FROM service WHERE chat_id = :chat_id ORDER BY name"""
        cur.execute(sql, {'chat_id': chat_id})
        _services = cur.fetchall()
    except Error as e:
        print(e)
    finally:
        cur.close()
    return _services


# create_service command
def create_service(chat_id: int, service: str, username: str) -> None:
    try:
        cur = conn.cursor()
        service = {'chat_id': chat_id,
                   'name': service,
                   'created_by': username,
                   'created_in': datetime.now()}
        sql = """INSERT INTO  service ('chat_id', 'name', 'created_by', 'created_in') 
                 VALUES (:chat_id, :name, :created_by, :created_in)"""
        cur.execute(sql, service)
        conn.commit()
    finally:
        cur.close()


# update_service command
def update_service(chat_id: int, service: str) -> None:
    pass


# delete_service command
def delete_service(chat_id: int, service: str) -> None:
    pass


def accounts(chat_id: int, service_name: str) -> List[dict]:
    _accounts = []
    try:
        cur = conn.cursor()
        account = {
            'chat_id': chat_id,
            'service_name': service_name
        }
        sql = """SELECT * FROM account WHERE chat_id = :chat_id AND service_name = :service_name ORDER BY username"""
        cur.execute(sql, account)
        _accounts = cur.fetchall()
    except Exception as e:
        print(e)
    finally:
        cur.close()
    return _accounts


# create_account command
def create_account(chat_id: int, service: str, username: str, password: str, created_by: str) -> None:
    try:
        cur = conn.cursor()
        account = {'chat_id': chat_id,
                   'service_name': service,
                   'username': username,
                   'password': password,
                   'created_by': created_by,
                   'created_in': datetime.now()
                   }
        sql = """INSERT INTO account ('chat_id', 'service_name', 'username', 'passwd', 'created_by', 'created_in') 
                 VALUES (:chat_id, :service_name, :username, :password, :created_by, :created_in)"""
        cur.execute(sql, account)
        conn.commit()
    except Error as e:
        print(e)
    finally:
        cur.close()


# update_account command
def update_account(chat_id: int, service: str, username: str, password: str) -> None:
    pass


# delete_account command
def delete_account(chat_id: int, service: str, username: str, password: str) -> None:
    pass




# status command
def status(chat_id: int, service: str) -> None:
    pass


# status_me command
def status_me(chat_id: int, ) -> None:
    pass


# ranking command
def ranking(chat_id: int, service: str) -> None:
    pass


# use command
def use(chat_id: int, service: str, account: str) -> None:
    pass


# release command
def release(chat_id: int, service: str, account: str) -> None:
    pass


# check command
def check(chat_id: int, service: str) -> None:
    pass


# report_broken command
def report_broken(chat_id: int, service: str, account: str) -> None:
    pass
