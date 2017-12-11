import os
import sys
import csv
import glob
import fiona
from shapely.geometry import shape
import psycopg2

import cadutils

def load_ddl(conn, ddlfile):
    print("* Executing DDL %s" % os.path.basename(ddlfile))
    with open(ddlfile, 'r', encoding='utf-8') as infile:
        ddl_content = infile.read()
        cur = conn.cursor()
        cur.execute(ddl_content)
        conn.commit()

def copy_from_csv_to_postgres_copy(conn, csv_path, table_name, sep=',', skip_header=True):
    cur = conn.cursor()
    with open(csv_path, 'r') as csvfile:
        if skip_header:
            next(csvfile)  # Skip the header row.
        cur.copy_from(csvfile, table_name, sep)

    conn.commit()

def copy_from_csv_to_postgres_inserts(conn, csv_path, table_name, columns, sep=','):
    cur = conn.cursor()
    print("* Loading %s with %s" % (table_name, os.path.basename(csv_path)))
    with open(csv_path, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter=sep)
        for row in csvreader:
            column_names = ','.join(columns)
            vals = [row[column_name]for column_name in columns]
            query = 'INSERT INTO %s (%s) ' % (table_name, column_names)
            query += 'VALUES (' + ','.join(['%s' for column_name in columns]) +')'

            cur.execute(query, vals)
    conn.commit()

def create_tables(conn):
    for sqlfile in sorted(glob.glob(os.path.dirname(os.path.abspath(__file__))+'/ddl/*.sql')):
        load_ddl(conn, sqlfile)

def refresh_materialized_view(conn):
    print(" *Loading v_map_capa (materialized view) with fresh data")
    cur = conn.cursor()
    cur.execute("REFRESH MATERIALIZED VIEW v_map_capa")
    conn.commit()

def check_postgis():
    pass

def make_checks():
    check_postgis()

def load_shapefile(conn, table_name, shapefile_path, columns):
    cur = conn.cursor()
    print("* Loading %s with %s" % (table_name, os.path.basename(shapefile_path)))
    with fiona.open(shapefile_path) as shapefile:
        for feat in shapefile:
            the_geom = shape(feat['geometry'])
             #Lower case for CAPAKEY, CAPATY, SHAPE_AREA, SHEET
            column_names = ','.join(map(str.lower, columns))
            query = 'INSERT INTO %s (the_geom, %s) ' % (table_name, column_names)
            query += 'VALUES (ST_SetSRID(ST_GeomFromText(%s),31370), ' + ','.join(['%s' for column_name in columns]) +')'
            vals = [feat['properties'][column_name]for column_name in columns]
            vals = [the_geom.wkt] + vals
            cur.execute(query, vals)
    conn.commit()


def main():
    if os.environ["CADASTREDIR"] == "":
        print("Environment variable CADASTREDIR must be set and pointing to a directory")
        sys.exit(0)
    else:
        print("Using %s as working dir" % os.environ["CADASTREDIR"])
        print("*")

    path_to_data = os.environ["CADASTREDIR"]
    path_to_da = os.path.join(path_to_data, "o_da.csv")
    path_to_map = os.path.join(path_to_data, "o_map.csv")
    path_to_pe = os.path.join(path_to_data, "o_pe.csv")
    path_to_prc = os.path.join(path_to_data, "o_prc.csv")
    path_to_capa = os.path.join(path_to_data, "OB_CaPa.shp")
    path_to_cabu = os.path.join(path_to_data, "Plan/B_CaBu.shp")
    path_to_canu = os.path.join(path_to_data, "Plan/B_CaNu.shp")
    path_to_geli = os.path.join(path_to_data, "Plan/B_GeLi.shp")
    path_to_gepn = os.path.join(path_to_data, "Plan/B_GePn.shp")
    path_to_gept = os.path.join(path_to_data, "Plan/B_GePt.shp")
    path_to_inli = os.path.join(path_to_data, "Plan/B_InLi.shp")
    path_to_inpt = os.path.join(path_to_data, "Plan/B_InPt.shp")
    path_to_toli = os.path.join(path_to_data, "Plan/B_ToLi.shp")
    path_to_topt = os.path.join(path_to_data, "Plan/B_ToPt.shp")
    path_to_mu = os.path.join(path_to_data, "Plan/A_AdMu.shp")


    cadutils.checkFile(path_to_da)
    cadutils.checkFile(path_to_map)
    cadutils.checkFile(path_to_pe)
    cadutils.checkFile(path_to_prc)
    make_checks()

    pg_host = os.environ["CAD_PG_HOST"]
    database_name = os.environ["CAD_DATABASE_NAME"]
    user_name = os.environ["CAD_DB_USER_NAME"]
    user_password = os.environ["CAD_DB_USER_PASSWORD"]

    conn = psycopg2.connect("host=%s dbname=%s user=%s password=%s" % (pg_host, database_name, user_name, user_password))
    check_postgis()

    print("* \n Creating tables \n")
    create_tables(conn)
    print("* \n Loading tables \n")

    copy_from_csv_to_postgres_inserts(conn, path_to_da, "da", [
        "da", "divname"
    ], sep="|")
    copy_from_csv_to_postgres_inserts(conn, path_to_map, "map", [
        "capakey", "pe", "adr1", "adr2", "sl1", "prc", "na1"
    ], sep="|")
    copy_from_csv_to_postgres_inserts(conn, path_to_pe, "pe", [
        "pe", "adr1", "adr2", "daa"
    ], sep="|")
    copy_from_csv_to_postgres_inserts(conn, path_to_prc, "prc", [
        "capakey", "daa", "sl1", "prc", "na1","co1","ha1","ri1","rscod","ord"
    ], sep="|")

    load_shapefile(conn, "capa", path_to_capa, [
        'CAPAKEY', 'CAPATY', 'SHAPE_AREA', 'SHEET', 'da',
        'section', 'radical', 'exposant', 'bis', 'puissance'
    ])

    load_shapefile(conn, "cabu", path_to_cabu, [
        'CABUTY', 'SHEET'
    ])

    load_shapefile(conn, "canu", path_to_canu, [
        'CANUAN', 'CANUTX', 'SHEET'
    ])

    load_shapefile(conn, "geli", path_to_geli, [
        'GELITY', 'SHEET'
    ])

    load_shapefile(conn, "gepn", path_to_gepn, [
        'GEPNTY', 'GEPNNA', 'SHEET'
    ])

    load_shapefile(conn, "gept", path_to_gept, [
        'GEPTTY', 'GEPTNA', 'SHEET'
    ])

    load_shapefile(conn, "inli", path_to_inli, [
        'INLITY', 'INLITX', 'SHEET'
    ])

    load_shapefile(conn, "inpt", path_to_inpt, [
        'INPTTY', 'INPTTX', 'SHEET'
    ])

    load_shapefile(conn, "toli", path_to_toli, [
        'TOLITY', 'TOLITX', 'SHEET'
    ])

    load_shapefile(conn, "topt", path_to_topt, [
        'TOPTTY', 'TOPTTX', 'TOPTAN', 'SHEET'
    ])

    refresh_materialized_view(conn)
    print("* \n Done \n")

if __name__ == "__main__":
    main()
