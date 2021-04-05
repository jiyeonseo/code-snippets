
import requests
import logging
import json
import gzip
import configparser
import pymysql
import os.path
from pymysql.constants import CLIENT
from pprint import pprint
from PyInquirer import prompt, print_json, Separator
import os


config = configparser.ConfigParser()
config.read('restore_db_config.ini')

SQL_FILE = "backup.sql"

def main():
    start_restore(SQL_FILE)

def start_restore(selected_file):
    db_answer = prompt([
        {
            'type': 'list',
            'name': 'profile',
            'message': 'Choose a profile',
            'choices': config.keys()
        },
        {
            'type': 'password',
            'name': 'password',
            'message': 'Insert a password (user : root)'
        },
    ])

    profile = db_answer["profile"]
    db_info = config[profile]

    db_connect = pymysql.connect(
        user=db_info['user'],
        passwd=db_answer["password"],
        host=db_info['host'],
        port=int(db_info['port']),
        charset='utf8',
        client_flag= CLIENT.MULTI_STATEMENTS
    )

    cursor = db_connect.cursor(pymysql.cursors.DictCursor)
    cursor.execute("show schemas")
    
    db = prompt([
        {
            'type': 'list',
            'name': 'database',
            'message': 'Choose a schema to restore.',
            'choices': [d['Database'] for d in cursor.fetchall()]
        },
    ])['database']
    db_connect.select_db(db)

    restore_type = prompt([
        {
            'type': 'list',
            'name': 'restore_type',
            'message': 'Restore a whole tables or a table?',
            'choices': ["whole", "table"]
        },
    ])['restore_type']
    
    selected = None
    
    if restore_type != "whole":
        tables = extract_tables(selected_file)
        backup_table = prompt([
            {
                'type': 'list',
                'name': 'table',
                'message': 'Choose table to restore.',
                'choices': [t['table'] for t in tables]
            },
        ])["table"]

        selected = list(filter(lambda x: x["table"] == backup_table, tables))[0]

    backup_start_answer = prompt([
        {
            'type': 'confirm',
            'message': 'Ready to start?',
            'name': 'start',
            'default': True,
        },
    ])

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    target_file = os.path.join(BASE_DIR, selected_file)

    if backup_start_answer['start']:
        with open(target_file, "r") as file:
            lines = file.readlines()
            if selected:
                lines = lines[selected['start']:selected['end']]
                
            sql = "".join(filter(lambda x: not x.startswith(
                "--") and not x.startswith("/*!"), lines))
            
            sql = sql.replace("\n ","  ")

            cursor.execute(sql)

        db_connect.commit()
        print("😻 DONE 😻")
    else:
        print("👋 Good Bye 👋")

def extract_tables(selected_file):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    target_file = os.path.join(BASE_DIR, selected_file)

    available_tables = []

    with open(target_file, "r") as file:
        lines = file.readlines()
        for (idx, line) in enumerate(lines):
            if line.startswith("DROP TABLE IF EXISTS"):
                line = line.replace("DROP TABLE IF EXISTS `", "")
                table = line[:-3]
                if len(available_tables) == 0:
                    available_tables.append({
                        "table": table,
                        "start": idx
                    })
                else:
                    available_tables[len(available_tables)-1]["end"] = idx - 1
                    available_tables.append({
                        "table": table,
                        "start": idx
                    })
        available_tables[len(available_tables)-1]["end"] = idx - 1

    return available_tables


def unzip(selected_file):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    target_file = os.path.join(BASE_DIR, selected_file)
    with open(selected_file, "wb") as file:
        with gzip.open(target_file, "rb") as f:
            content = f.read()
            file.write(content)      # write to file


def download(url, file_name):
    with open(file_name, "wb") as file:   # open in binary mode
        response = requests.get(url)               # get request
        file.write(response.content)      # write to file


def get_endpoint(gateway):
    # get from gateway
    x = requests.get(gateway)
    endpoint = x.text
    logging.info(f'gateway={x.text}, endpoint={endpoint}')
    return endpoint


if __name__ == "__main__":
    main()
