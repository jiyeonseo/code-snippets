import datetime
import os
import configparser
import yaml

def make_dump(key, conf, ymdhms):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    mysql_conf = conf['mysql']
    dumppath = os.path.join(BASE_DIR, f'{key}-{ymdhms}.sql')
    
    dumpcmd = f"mysqldump --user={mysql_conf['user']} --password={mysql_conf['password']} --host={mysql_conf['host']} --port={mysql_conf['port']} --protocol=tcp --default-character-set=utf8 --single-transaction=TRUE --skip-triggers {mysql_conf['dbname']} > {dumppath}"
    os.system(dumpcmd)
    gzipcmd = f"gzip {dumppath}"
    os.system(gzipcmd)
    return f'{dumppath}.gz'


ymdhmsFormat = '%Y%m%d%H%M%S'

with open('config.yaml') as f: # load config
    
    conf = yaml.load(f)
    dt = datetime.datetime.now()
    ymdhms = dt.strftime(ymdhmsFormat)
    for key in conf:
        elem = conf[key]
        dumppath = make_dump(key, elem, ymdhms)
        
