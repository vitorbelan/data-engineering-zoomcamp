#!/usr/bin/env python
# coding: utf-8

# # Ingerindo o dataset
import pandas as pd
import argparse
import os
from sqlalchemy import create_engine
from time import time


def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url

    csv_name = 'output.csv'
    os.system(f"wget {url} ")
    os.system("gzip -d yellow_tripdata_2019-01.csv.gz")
    os.system("mv yellow_tripdata_2019-01.csv output.csv")

    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

    df_iter = pd.read_csv(f'{csv_name}', iterator = True, chunksize = 100000)

    df = next(df_iter)

    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    df.head(n=0).to_sql(name = f'{table_name}', con = engine, if_exists = 'replace')

    df.to_sql(name = f'{table_name}', con = engine, if_exists = 'append')

    while True:
        try:
            t_start = time()
            
            df = next(df_iter)
            
            df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
            df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
            
            df.to_sql(name = table_name, con = engine, if_exists = 'append')
            
            t_end = time()
            
            print("Inserido outro chunck..., e levou %.3f seconds"%(t_end-t_start))
        except StopIteration:
            print('Ingestao finalizada')
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingestao de dados CSV para o Postgres')
    parser.add_argument('--user',         help = 'entre com seu user') 
    parser.add_argument('--password',     help = 'entre com seu password')
    parser.add_argument('--host',         help = 'entre com seu host')
    parser.add_argument('--port',         help = 'entre com seu port')
    parser.add_argument('--db',           help = 'entre com seu db')
    parser.add_argument('--table_name',   help = 'entre com table_name onde escreveremos a tabela')
    parser.add_argument('--url',          help = 'entre com seu url do csv')

    args = parser.parse_args()
    # print(args.accumulate(args.integers))

    main(args)

