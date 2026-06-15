import pandas as pd
import os
from sqlalchemy import create_engine
import logging 
import time
from  ingestion_db import ingest_db

logging.basicConfig(
    filename = r"C:\Users\amand\Desktop\DataAnalytics\project\Vendor-performance-Analysis\logs\get_vendor_summary.log",
    level = logging.DEBUG,
    format = "%(asctime)s - %(levelname)s - %(message)s",
    filemode = "a",
    force=True
)

def create_vendor_summary(engine):
    '''this function will merge the differnet tables to  get the overall vendor
    summary and adding new columns in the  resultant data'''

    vendor_sales_summary = pd.read_sql("""
       
        WITH FreightSummary AS (

            SELECT 
                VendorNumber,
                SUM(Freight) AS FreightCost

            FROM vendor_invoice

            GROUP BY VendorNumber
        ),

        PurchaseSummary AS (

            SELECT 
                p.VendorNumber,
                p.VendorName,
                p.Brand,
                p.Description,
                p.PurchasePrice,

                pp.Price AS ActualPrice,
                pp.Volume,

                SUM(p.Quantity) AS TotalPurchaseQuantity,
                SUM(p.Dollars) AS TotalPurchaseDollars

            FROM purchases p

            JOIN purchase_prices pp
                ON p.Brand = pp.Brand

            WHERE p.PurchasePrice > 0

            GROUP BY 
                p.VendorNumber,
                p.VendorName,
                p.Brand,
                p.Description,
                p.PurchasePrice,
                pp.Price,
                pp.Volume
        ),

        SalesSummary AS (

            SELECT 
                VendorNo,
                Brand,

                SUM(SalesDollars) AS TotalSalesDollars,
                SUM(SalesPrice) AS TotalSalesPrice,
                SUM(SalesQuantity) AS TotalSalesQuantity,
                SUM(ExciseTax) AS TotalExciseTax

            FROM sales

            GROUP BY VendorNo, Brand
        )

        SELECT 

            ps.VendorNumber,
            ps.VendorName,
            ps.Brand,
            ps.Description,
            ps.PurchasePrice,

            ps.ActualPrice,
            ps.Volume,

            ps.TotalPurchaseQuantity,
            ps.TotalPurchaseDollars,

            ss.TotalSalesQuantity,
            ss.TotalSalesDollars,
            ss.TotalSalesPrice,
            ss.TotalExciseTax,

            fs.FreightCost

        FROM PurchaseSummary ps

        LEFT JOIN SalesSummary ss
            ON ps.VendorNumber = ss.VendorNo
            AND ps.Brand = ss.Brand

        LEFT JOIN FreightSummary fs
            ON ps.VendorNumber = fs.VendorNumber

        ORDER BY ps.TotalPurchaseDollars DESC

        """, engine)
    
    return vendor_sales_summary


def clean_data(df):
    '''this function will clean the data'''
    # changing datatype  to float

    df['Volume'] = df['Volume'].astype('float')

    # filling missing value with 0
    df.fillna(0,inplace = True)

    # removing spaces from categorical columns
    df['VendorName'] = df['VendorName'].str.strip()
    df['Description'] = df['Description'].str.strip()

    # creating new columns for better analysis
    df['GrossProfit'] = df['TotalSalesDollars'] - df['TotalPurchaseDollars']
    df['ProfitMargin'] = (df['GrossProfit']/df['TotalSalesDollars'])*100
    df['StockTurnover'] = df['TotalSalesQuantity']/df['TotalPurchaseQuantity']
    df['SalesPurchaseRatio'] = df['TotalSalesDollars']/df['TotalPurchaseDollars']

    
    import numpy as np

    df.replace([np.inf, -np.inf], 0, inplace=True)

    float_cols = [
        'PurchasePrice',
        'ActualPrice',
        'TotalPurchaseDollars',
        'TotalSalesDollars',
        'TotalSalesPrice',
        'TotalExciseTax',
        'FreightCost',
        'GrossProfit',
        'ProfitMargin',
        'StockTurnover',
        'SalesPurchaseRatio'
    ]

    df[float_cols] = df[float_cols].round(2)

    return df
    


if __name__ == '__main__':

    try:

        engine = create_engine(
            "mssql+pyodbc://AYUSH\\MSSQLSERVER01/inventory_db?"
            "driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes"
        )

        start = time.time()

        logging.info('Creating Vendor Summary Table.....')

        summary_df = create_vendor_summary(engine)

        logging.info(summary_df.head())

        logging.info('Cleaning Data.....')

        clean_df = clean_data(summary_df)

        logging.info(clean_df.head())

        logging.info('Ingesting data.....')

        ingest_db(clean_df, 'vendor_sales_summary', engine)

        end = time.time()

        logging.info(f'Completed in {end-start} seconds')

    except Exception as e:

        logging.error(f"Error occurred: {e}", exc_info=True)