import io
import os
import sys
import csv
import glob
import fiona
from shapely.geometry import shape
import psycopg2
import xlrd
import cadutils
import pandas
import networkx


def load_ddl(conn, ddlfile):
    print("* Executing DDL %s" % os.path.basename(ddlfile))
    with open(ddlfile, 'r', encoding='utf-8') as infile:
        ddl_content = infile.read()
        cur = conn.cursor()
        cur.execute(ddl_content)
        conn.commit()


def copy_from_csv_to_postgres_copy(conn, csv_path, table_name, sep=',', skip_header=True, encoding='iso8859-1'):
    cur = conn.cursor()
    cur.execute("SET DateStyle='DMY'")
    with open(csv_path, 'r', encoding=encoding) as csvfile:
        if skip_header:
            next(csvfile)  # Skip the header row.
        cur.copy_from(csvfile, table_name, sep, null='')

    conn.commit()


def copy_from_array_to_postgres(conn, array, table_name, sep=';', skip_header=True, encoding='iso8859-1'):
    cur = conn.cursor()
    cur.execute("SET DateStyle='DMY'")
    with io.StringIO(array.to_csv(sep=sep, index=False)) as csvfile:
        if skip_header:
            next(csvfile)  # Skip the header row.
        cur.copy_from(csvfile, table_name, sep, null='')

    conn.commit()


def copy_from_parcel_codes_to_postgres(conn, path_to_parcel_codes,
                                       table_name, sep=',', skip_header=True):
    cur = conn.cursor()
    book = xlrd.open_workbook(filename=path_to_parcel_codes,
                              encoding_override='latin_1')
    sheet = book.sheet_by_name("Nature")
    query = """
    INSERT INTO GLOBAL_NATURES (Nature_PK, Nature_FR, Nature_NL, obsolete)
    VALUES (%s, %s, %s, %s)
    """
    for r in range(2, sheet.nrows):
        nature_pk = sheet.cell(r, 0).value
        nature_fr = sheet.cell(r, 1).value
        nature_nl = sheet.cell(r, 2).value
        values = (nature_pk, nature_fr, nature_nl, 'false')
        cur.execute(query, values)

    conn.commit()


def copy_division_to_postgres(conn, path_to_parcel_codes,
                              table_name, sep=',', skip_header=True):
    cur = conn.cursor()
    book = xlrd.open_workbook(filename=path_to_parcel_codes,
                              encoding_override='latin_1')
    sheet = book.sheet_by_name("divCad ")
    query = """
    INSERT INTO Divisions (da, dan1, divname)
    VALUES (%s, %s, %s)
    """
    for r in range(2, sheet.nrows):
        divcode = sheet.cell(r, 0).value
        divname = sheet.cell(r, 1).value
        values = (divcode, divname, divname)
        cur.execute(query, values)

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
            query += 'VALUES (' + ','.join(['%s' for column_name in columns]) + ')'

            cur.execute(query, vals)
    conn.commit()


def create_tables(conn, cadastre_date):
    for sqlfile in sorted(glob.glob(os.path.dirname(os.path.abspath(__file__)) + '/ddl' + cadastre_date + '/c*.sql')):
        load_ddl(conn, sqlfile)


def filling_tables(conn, cadastre_date):
    for sqlfile in sorted(glob.glob(os.path.dirname(os.path.abspath(__file__)) + '/ddl' + cadastre_date + '/i*.sql')):
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
    if os.path.exists(shapefile_path):
        cur = conn.cursor()
        print("* Loading %s with %s" % (table_name, os.path.basename(shapefile_path)))
        with fiona.open(shapefile_path) as shapefile:
          for feat in shapefile:
             the_geom = shape(feat['geometry'])
             # Lower case for CAPAKEY, CAPATY, SHAPE_AREA, SHEET
             column_names = ','.join(map(str.lower, columns))
             query = 'INSERT INTO %s (the_geom, %s) ' % (table_name, column_names)
             query += 'VALUES (ST_SetSRID(ST_GeomFromText(%s),31370), ' + ','.join(['%s' for column_name in columns]) + ')'
             vals = [feat['properties'][column_name]for column_name in columns]
             vals = [the_geom.wkt] + vals
             cur.execute(query, vals)
        conn.commit()


def get_historic_array(path):
    """ """
    merged_arrays = None
    for file_name in os.listdir(path):
        full_path = os.path.join(path, file_name)
        read_args = {
            'filepath_or_buffer': full_path,
            'sep': ';',
            'header': 0,
            'encoding': 'iso8859-1',
            'na_filter': False
        }
        # check header
        base_file = open(full_path, 'r')
        header = base_file.readline()
        # if no header, add one
        if not header.startswith('propertySituationIdf_av;divCad_av;'):
            base_file.close()
            read_args['names'] = ['propertySituationIdf_av', 'divCad_av', 'articleNumber_av', 'articleOrder_av', 'section_av', 'primaryNumber_av', 'bisNumber_av', 'exponentLetter_av', 'exponentNumber_av', 'partNumber_av', 'noParcel_av', 'parclCadStatu_av', 'flagAnnul', 'flagInterm_av', 'descriptPrivate_av', 'yearBegin_av', 'yearEnd_av', 'yearAnnul_av', 'propertySituationIdf_ap', 'divCad_ap', 'articleNumber_ap', 'articleOrder_ap', 'section_ap', 'primaryNumber_ap', 'bisNumber_ap', 'exponentLetter_ap', 'exponentNumber_ap', 'partNumber_ap', 'noParcel_ap', 'parclCadStatu_ap', 'flagInterm_ap', 'descriptPrivate_ap', 'yearBegin_ap', 'yearEnd_ap', 'yearAnnul_ap', 'dossier', 'sketch']
        array = pandas.read_csv(**read_args, low_memory=False)
        if merged_arrays is None:
            merged_arrays = array
        else:
            merged_arrays = merged_arrays.append(array, ignore_index=True)
    return merged_arrays


def add_capakey_columns(array):
    array = array.assign(capakey_av=lambda x: '')
    array['capakey_av'] = array.apply(
        lambda row: generate_capakey(
            row.divCad_av,
            row.section_av,
            row.primaryNumber_av,
            row.bisNumber_av,
            row.exponentLetter_av,
            row.exponentNumber_av,
        ),
        axis=1
    )
    array = array.assign(capakey_ap=lambda x: '')
    array['capakey_ap'] = array.apply(
        lambda row: generate_capakey(
            row.divCad_ap,
            row.section_ap,
            row.primaryNumber_ap,
            row.bisNumber_ap,
            row.exponentLetter_ap,
            row.exponentNumber_ap,
        ),
        axis=1
    )
    return array


def generate_capakey(div, section, primary, bis, exponent_l, exponent_n):
    if not section:
        return ''

    capakey = '{:0>5}{}{:0>4}/{:0>2}{:_>1}{:0>3}'.format(
        div,
        section,
        primary,
        bis,
        exponent_l,
        exponent_n,
    )
    return capakey


def reduce_old_parcels_array(array, time='av'):
    to_drop = time == 'av' and 'ap' or 'av'
    array = array.drop(columns=[
        'articleNumber_av',
        'articleOrder_av',
        'noParcel_av',
        'parclCadStatu_av',
        'flagAnnul',
        'flagInterm_av',
        'descriptPrivate_av',
        'articleNumber_ap',
        'articleOrder_ap',
        'noParcel_ap',
        'parclCadStatu_ap',
        'flagInterm_ap',
        'descriptPrivate_ap',
        'dossier',
        'sketch',
        'propertySituationIdf_{}'.format(to_drop),
        'divCad_{}'.format(to_drop),
        'section_{}'.format(to_drop),
        'primaryNumber_{}'.format(to_drop),
        'bisNumber_{}'.format(to_drop),
        'exponentLetter_{}'.format(to_drop),
        'exponentNumber_{}'.format(to_drop),
        'partNumber_{}'.format(to_drop),
        'yearBegin_{}'.format(to_drop),
        'yearEnd_{}'.format(to_drop),
        'yearAnnul_{}'.format(to_drop),
        'capakey_{}'.format(to_drop),
    ])
    array = array.rename(
        index=str,
        columns={
            'propertySituationIdf_{}'.format(time): 'propertySituationId',
            'divCad_{}'.format(time): 'divCad',
            'section_{}'.format(time): 'section',
            'primaryNumber_{}'.format(time): 'primaryNumber',
            'bisNumber_{}'.format(time): 'bisNumber',
            'exponentLetter_{}'.format(time): 'exponentLetter',
            'exponentNumber_{}'.format(time): 'exponentNumber',
            'partNumber_{}'.format(time): 'partNumber',
            'yearBegin_{}'.format(time): 'yearBegin',
            'yearEnd_{}'.format(time): 'yearEnd',
            'yearAnnul_{}'.format(time): 'yearAnnul',
            'capakey_{}'.format(time): 'capakey',
        },
    )
    array = array.assign(
        partNumber=lambda array: array['partNumber'].replace('', 'P0000'),
    )
    array = array.drop_duplicates()
    reorder = [
        'capakey',
        'divCad',
        'section',
        'primaryNumber',
        'bisNumber',
        'exponentLetter',
        'exponentNumber',
        'partNumber',
        'yearAnnul',
        'yearBegin',
        'yearEnd',
        'propertySituationId',
    ]
    array = array[reorder]
    return array


def get_old_parcels_array(array):
    array_av = reduce_old_parcels_array(array, 'av')
    array_ap = reduce_old_parcels_array(array, 'ap')
    merged_array = array_av.append(array_ap)
    merged_array = merged_array.drop_duplicates()
    to_drop = []
    for index, row in merged_array.iterrows():
        if not row.capakey:
            to_drop.append(index)
    merged_array = merged_array.drop(to_drop)
    return merged_array


def reduce_historic_array(array):
    array = array.drop(columns=[
        'propertySituationIdf_av',
        'articleNumber_av',
        'articleOrder_av',
        'noParcel_av',
        'parclCadStatu_av',
        'flagAnnul',
        'flagInterm_av',
        'descriptPrivate_av',
        'yearBegin_av',
        'yearEnd_av',
        'yearAnnul_av',
        'propertySituationIdf_ap',
        'articleNumber_ap',
        'articleOrder_ap',
        'noParcel_ap',
        'parclCadStatu_ap',
        'flagInterm_ap',
        'descriptPrivate_ap',
        'yearBegin_ap',
        'yearEnd_ap',
        'yearAnnul_ap',
        'dossier', 'sketch'
    ])
    array = array.assign(
        partNumber_av=lambda array: array['partNumber_av'].replace('', 'P0000'),
        partNumber_ap=lambda array: array['partNumber_ap'].replace('', 'P0000'),
    )
    array = array.drop_duplicates()
    to_drop = []
    for index, row in array.iterrows():
        if row.capakey_av == row.capakey_ap and row.partNumber_av == row.partNumber_ap:
            to_drop.append(index)
    cleaned_array = array.drop(to_drop)
    return cleaned_array


def reduce_historic_to_capakey_only(array):
    array = array.drop(columns=[
        'partNumber_av',
        'partNumber_ap',
    ])
    to_drop = []
    for index, row in array.iterrows():
        if row.capakey_av == row.capakey_ap:
            to_drop.append(index)
    array = array.drop(to_drop)
    return array


def create_full_historic_graph(array):
    graph = networkx.DiGraph()
    for row in array.itertuples():
        before = (row.capakey_av, row.partNumber_av)
        after = (row.capakey_ap, row.partNumber_ap)
        if before[0] and after[0]:
            graph.add_node(before)
            graph.add_node(after)
            graph.add_edge(before, after)
    return graph


def create_capakey_historic_graph(array):
    graph = networkx.DiGraph()
    for row in array.itertuples():
        before = row.capakey_av
        after = row.capakey_ap
        if before and after:
            graph.add_node(before)
            graph.add_node(after)
            graph.add_edge(before, after)
    return graph


def get_successors(graph, node, checked=set([])):
    successors = {}
    checked.add(node)
    for subnode in graph.successors(node):
        if subnode not in checked:
            successors[subnode] = get_successors(graph, subnode, checked)
    return successors


def get_predecessors(graph, node, checked=set([])):
    predecessors = {}
    checked.add(node)
    for subnode in graph.predecessors(node):
        if subnode not in checked:
            predecessors[subnode] = get_predecessors(graph, subnode, checked)
    return predecessors


def build_full_genealogy(array):
    columns = ['capakey', 'partNumber', 'predecessors', 'successors']
    graph = create_full_historic_graph(array)
    new_historic = []
    for node in graph.nodes():
        capakey = node[0]
        part = node[1]
        predecessors = str(get_predecessors(graph, node, checked=set([])))
        successors = str(get_successors(graph, node, checked=set([])))
        new_historic.append([capakey, part, predecessors, successors])

    new_array = pandas.DataFrame(
        data=new_historic,
        columns=columns
    )
    return new_array


def build_capakey_genealogy(array):
    columns = ['capakey', 'predecessors', 'successors']
    graph = create_capakey_historic_graph(array)
    new_historic = []
    for node in graph.nodes():
        capakey = node
        predecessors = str(get_predecessors(graph, node, checked=set([])))
        successors = str(get_successors(graph, node, checked=set([])))
        new_historic.append([capakey, predecessors, successors])

    new_array = pandas.DataFrame(
        data=new_historic,
        columns=columns
    )
    return new_array


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
    path_to_historic = os.path.join(path_to_data, "Historique")

    path_to_capa = os.path.join(path_to_data, "Plan/Bpn_CaPa.shp")
    path_to_cabu = os.path.join(path_to_data, "Plan/Bpn_CaBu.shp")
    path_to_rebu = os.path.join(path_to_data, "Plan/Bpn_ReBu.shp")

    cadutils.checkFile(path_to_owner)
    cadutils.checkFile(path_to_parcel)
    make_checks()
    pg_host = os.environ["CAD_PG_HOST"]
    database_name = os.environ["CAD_DATABASE_NAME"]
    user_name = os.environ["CAD_DB_USER_NAME"]
    user_password = os.environ["CAD_DB_USER_PASSWORD"]
    port = os.environ["CAD_PG_PORT"]
    conn = psycopg2.connect("host=%s dbname=%s user=%s password=%s port=%s" % (pg_host, database_name, user_name, user_password, port))
    check_postgis()
    print("* Creating tables")
    create_tables(conn, cadastre_date)
    print("* Importing data")
    historic_array = get_historic_array(path_to_historic)
    new_historic_array = add_capakey_columns(historic_array)
    print("* Importing historic data")
    copy_from_array_to_postgres(conn, new_historic_array, "parcels_historic",
                                skip_header=True)
    print("* Importing old parcels")
    old_parcels_array = get_old_parcels_array(new_historic_array)
    copy_from_array_to_postgres(conn, old_parcels_array, "old_parcels", skip_header=True)
    reduced_historic_array = reduce_historic_array(new_historic_array)
    print("* Importing reduced historic data")
    copy_from_array_to_postgres(conn, reduced_historic_array, "reduced_parcels_historic", sep=';',
                                skip_header=True)
    genealogy_array = build_full_genealogy(reduced_historic_array)
    print("* Importing genealogy of each capakey")
    copy_from_array_to_postgres(conn, genealogy_array, "complete_parcels_genealogy",
                                skip_header=True)
    capakey_historic_array = reduce_historic_to_capakey_only(reduced_historic_array)
    capakey_genealogy_array = build_capakey_genealogy(capakey_historic_array)
    copy_from_array_to_postgres(conn, capakey_genealogy_array, "parcels_genealogy",
                                skip_header=True)
    copy_from_csv_to_postgres_copy(conn, path_to_owner, "owners_imp", sep=';',
                                   skip_header=True)
    copy_from_csv_to_postgres_copy(conn, path_to_parcel, "parcels_imp", sep=';',
                                   skip_header=True)
    copy_from_parcel_codes_to_postgres(conn, path_to_parcel_codes, "global_Natures",
                                       sep=';', skip_header=True)
    print("* Filling tables")
    filling_tables(conn, cadastre_date)

    copy_division_to_postgres(conn, path_to_parcel_codes, "global_Natures",
                              sep=';', skip_header=True)
    clean_unused_division(conn)

    load_shapefile(conn, "capa", path_to_capa, [
        'CaPaKey', 'CaSeKey'
    ])

#    load_shapefile(conn, "cabu", path_to_cabu, [
#        'RecId', 'Type'
#    ])
#
#    load_shapefile(conn, "rebu", path_to_rebu, [
#        'ID_ORIG', 'Type'
#    ])

    print("* Done \n")


if __name__ == "__main__":
    main()
