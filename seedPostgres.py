import os
import sys
import csv
import glob
import fiona
from shapely.geometry import shape
import psycopg2
import xlrd
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
    cur.execute ("SET DateStyle='DMY'")
    with open(csv_path, 'r', encoding='iso8859-1') as csvfile:
        if skip_header:
            next(csvfile)  # Skip the header row.
        cur.copy_from(csvfile, table_name, sep, null = '')

    conn.commit()

def copy_from_parcel_codes_to_postgres(conn, path_to_parcel_codes,
                                       table_name, sep=',', skip_header=True):
    cur = conn.cursor()
    book = xlrd.open_workbook(filename = path_to_parcel_codes,
                              encoding_override = 'latin_1')
    sheet = book.sheet_by_name("Nature")
    query = """
    INSERT INTO GLOBAL_NATURES (Nature_PK, Nature_FR, Nature_NL, obsolete)
    VALUES (%s, %s, %s, %s)
    """
    for r in range (2, sheet.nrows):
        nature_pk = sheet.cell(r,0).value
        nature_fr = sheet.cell(r,1).value
        nature_nl = sheet.cell(r,2).value
        values = (nature_pk, nature_fr, nature_nl, 'false')
        cur.execute (query, values)

    conn.commit()

def copy_division_to_postgres(conn, path_to_parcel_codes,
                                       table_name, sep=',', skip_header=True):
    cur = conn.cursor()
    book = xlrd.open_workbook(filename = path_to_parcel_codes,
                              encoding_override = 'latin_1')
    sheet = book.sheet_by_name("divCad ")
    query = """
    INSERT INTO Divisions (da, dan1, divname)
    VALUES (%s, %s, %s)
    """
    for r in range (2, sheet.nrows):
        divcode = sheet.cell(r,0).value
        divname = sheet.cell(r,1).value
        values = (divcode, divname, divname)
        cur.execute (query, values)

    conn.commit()

def clean_unused_division(conn):
    print(" *Cleaning unused divisions")
    cur = conn.cursor()
    cur.execute("delete from divisions where da not in (select distinct(divcad) from parcels)")
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

def create_tables(conn, cadastre_date):
    for sqlfile in sorted(glob.glob(os.path.dirname(os.path.abspath(__file__))+
        '/ddl' + cadastre_date + '/c*.sql')):
        load_ddl(conn, sqlfile)

def filling_tables(conn, cadastre_date):
    for sqlfile in sorted(glob.glob(os.path.dirname(os.path.abspath(__file__))+
        '/ddl' + cadastre_date + '/i*.sql')):
        load_ddl(conn, sqlfile)

def refresh_materialized_view(conn):
    print(" *Loading v_map_capa (materialized view) with fresh data")
    cur = conn.cursor()
    cur.execute("REFRESH MATERIALIZED VIEW vm_map_capa")
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

    cadastre_date = os.environ["CADASTREDATE"]
    path_to_data = os.environ["CADASTREDIR"]
    path_to_owner = os.path.join(path_to_data, "Matrice/Owner.csv")
    path_to_parcel = os.path.join(path_to_data, "Matrice/Parcel.csv")
    path_to_parcel_codes = os.path.join(path_to_data, "Matrice_doc/OUTPUT PARCELS_.xlsx")

    path_to_capa = os.path.join(path_to_data, "Plan/Bpn_CaPa.shp")
    path_to_cabu = os.path.join(path_to_data, "Plan/Bpn_CaBu.shp")

    cadutils.checkFile(path_to_owner)
    cadutils.checkFile(path_to_parcel)
    make_checks()
    pg_host = os.environ["CAD_PG_HOST"]
    database_name = os.environ["CAD_DATABASE_NAME"]
    user_name = os.environ["CAD_DB_USER_NAME"]
    user_password = os.environ["CAD_DB_USER_PASSWORD"]
    conn = psycopg2.connect("host=%s dbname=%s user=%s password=%s" % (pg_host, database_name, user_name, user_password))
    check_postgis()
    print("* Creating tables")
    create_tables(conn, cadastre_date)
    print("* Importing data")
    copy_from_csv_to_postgres_copy(conn, path_to_owner,"Owners_imp",sep=';'
                                   , skip_header=True)
    copy_from_csv_to_postgres_copy(conn, path_to_parcel,"Parcels_imp",sep=';'
                                   , skip_header=True)
    copy_from_parcel_codes_to_postgres(conn, path_to_parcel_codes,
                        "Global_Natures",sep=';' , skip_header=True)

    print("* Filling tables")
    filling_tables(conn, cadastre_date)

    copy_division_to_postgres(conn, path_to_parcel_codes,
                        "Global_Natures",sep=';' , skip_header=True)
    clean_unused_division(conn)

    load_shapefile(conn, "capa", path_to_capa, [
         'CaPaKey',  'CaSeKey' 
    ])

    load_shapefile(conn, "cabu", path_to_cabu, [
         'RecId', 'Type'
    ])
 

    print("* Done \n")

if __name__ == "__main__":
    main()

