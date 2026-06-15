create database inventory_db;

use inventory_db;

CREATE VIEW monthly_purchase_summary as 
Select 
		VendorNumber,
		VendorName,
		Brand,
		DATEFROMPARTS(YEAR(PODate),Month(PODate),1) AS Purchasemonth,
		SUM(Quantity) as MonthlyPurchaseQty,
		SUM(Dollars) as MonthlyPurchaseDollars
From purchases
Group by VendorNumber,VendorName,Brand,DATEFROMPARTS(YEAR(PODate),Month(PODate),1);



CREATE VIEW monthly_sales_summary AS
SELECT
    VendorNo AS VendorNumber,
    VendorName,
    Brand,
    DATEFROMPARTS(YEAR(SalesDate), MONTH(SalesDate), 1) AS SalesMonth,
    SUM(SalesQuantity) AS MonthlySalesQty,
    SUM(SalesDollars)  AS MonthlySalesDollars,
    SUM(ExciseTax)     AS MonthlyExciseTax
FROM sales
GROUP BY VendorNo, VendorName, Brand,
         DATEFROMPARTS(YEAR(SalesDate), MONTH(SalesDate), 1);