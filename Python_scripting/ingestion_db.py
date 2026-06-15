import pandas as pd
import os
from sqlalchemy import create_engine
import logging 
import time

logging.basicConfig(
    filename = r"C:\Users\amand\Desktop\DataAnalytics\project\Vendor-performance-Analysis\logs\ingestion_db.log",
    level = logging.DEBUG,
    format = "%(asctime)s - %(levelname)s - %(message)s",
    filemode = "a"
)


from sqlalchemy import create_engine

engine = create_engine(
    "mssql+pyodbc://AYUSH\\MSSQLSERVER01/inventory_db?"
    "driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes")

# scripting is imp ....agar har 15 min mai data aa raha hai to scripting help karti hai update karne mai
def ingest_db(df, table_name, engine):
    df.to_sql(table_name, con = engine, if_exists = 'replace', index = False)


def load_raw_data():
    '''This function will load the CSVs as dataframe and ingest into db....'''
    
    start = time.time()

    folder_path = r'C:\Users\amand\Desktop\DataAnalytics\project\Vendor-performance-Analysis\data\raw\data'

    for file in os.listdir(folder_path):
        if file.lower().endswith('.csv'):  # safer CSV check
            file_path = os.path.join(folder_path,file)# full path
            df = pd.read_csv(file_path)
            
            logging.info(f'ingesting{file} in db')
            ingest_db(df, file[:-4], engine)

    end = time.time()
    total_time = (end - start)/ 60
    logging.info("-------------------Ingestion Complete-------------------")
    logging.info(f'\nTotal Time Taken :{total_time} minutes')


if __name__ == '__main__':
    load_raw_data()