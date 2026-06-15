use inventory_db;

SELECT table_name
FROM information_schema.tables
WHERE table_type = 'BASE TABLE';

select * from [dbo].[begin_inventory];

select * from [dbo].[end_inventory];

select * from [dbo].[purchase_prices];

alter table [dbo].[purchase_prices]
drop column Size;

select * from [dbo].[purchases];

select * from [dbo].[sales];

select * from [dbo].[vendor_invoice];