INSERT INTO [dbo].[EconomicIndicators] ([Indicator], [Category], [Source], [Frequency], [Measure])
VALUES ('Stock Market Cap', 'Stock Market', 'World Bank', 'Y', 'Current US Dollars'),
	('Stock Market Cap Pct of GDP', 'Stock Market', 'World Bank', 'Y', 'Pct of GDP'),
	('Listed Domestic Companies Total', 'Stock Market', 'World Bank', 'Y', 'Count'),
	('Stocks Traded Total Value', 'Stock Market', 'World Bank', 'Y', 'Current US Dollars'),
	('Stocks Traded Total Value Pct of GDP', 'Stock Market', 'World Bank', 'Y', 'Pct of GDP'),
	('GDP', 'GDP', 'World Bank', 'Y', 'Current US Dollars'),
	('GDP Per Capita', 'GDP', 'World Bank', 'Y', 'Current US Dollars'),
	('Population', 'Labour', 'World Bank', 'Y', 'Count'),
	('Current Account Pct of GDP', 'Trade', 'World Bank', 'Y', 'Pct of GDP'),
	('Current Account', 'Trade', 'World Bank', 'Y', 'Current US Dollars'),
	('Government Expense', 'Government', 'World Bank', 'Y', 'Pct of GDP')