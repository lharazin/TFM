INSERT INTO [dbo].[EconomicIndicators] ([Indicator], [Category], [Source], [Frequency], [Measure])
VALUES ('GDP Annual Growth Rate', 'GDP', 'Investing', 'Q', 'Growth YoY'),
	('GDP Growth Rate', 'GDP', 'Investing', 'Q', 'Growth QoQ'),	
	('Unemployment Rate', 'Labour', 'Investing', 'M', 'Level'),
	('Inflation Rate', 'Prices', 'Investing', 'M', 'Growth YoY'),
	('Inflation Rate MoM', 'Prices', 'Investing', 'M', 'Growth MoM'),
	('Manufacturing PMI', 'Bussiness', 'Investing', 'M', 'Index'),
	('Services PMI', 'Bussiness', 'Investing', 'M', 'Index')