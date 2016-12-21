import sqlite3 
import csv
from pprint import pprint


sqlite_file = 'OSM.db'

csv_files = {'nodes':'nodes.csv',
             'nodes_tags':'nodes_tags.csv',
             'ways':'ways.csv',
             'ways_tags' : 'ways_tags.csv',
             'ways_nodes': 'ways_nodes.csv'}

SQL_TABLES = {
    "nodes" : """
    CREATE TABLE nodes (
    id INTEGER PRIMARY KEY NOT NULL,
    lat REAL,
    lon REAL,
    user TEXT,
    uid INTEGER,
    version INTEGER,
    changeset INTEGER,
    timestamp TEXT
);""",
    "nodes_tags": """
    CREATE TABLE nodes_tags (
    id INTEGER,
    key TEXT,
    value TEXT,
    type TEXT,
    FOREIGN KEY (id) REFERENCES nodes(id)
);""",
    "ways" : """
    CREATE TABLE ways (
    id INTEGER PRIMARY KEY NOT NULL,
    user TEXT,
    uid INTEGER,
    version TEXT,
    changeset INTEGER,
    timestamp TEXT
);""",
    "ways_tags" : """
    CREATE TABLE ways_tags (
    id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    type TEXT,
    FOREIGN KEY (id) REFERENCES ways(id)
);""",
    "ways_nodes" : """
    CREATE TABLE ways_nodes (
    id INTEGER NOT NULL,
    node_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    FOREIGN KEY (id) REFERENCES ways(id),
    FOREIGN KEY (node_id) REFERENCES nodes(id)
);"""
}

def create_tables() :
    conn = sqlite3.connect(sqlite_file)

    cur = conn.cursor()

    for t_name, sql in SQL_TABLES.iteritems() :

        sql_drop = """DROP TABLE IF EXISTS """+str(t_name)+""";"""

        cur.execute(sql_drop)
        conn.commit()
        cur.execute(sql)
        conn.commit()
        print 'Table',t_name,'is created.'
    
    conn.close()
def get_csv() :
    return csv_files
