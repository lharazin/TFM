ALTER TABLE [dbo].[EconomicIndicators] ADD [SymbolCode] VARCHAR(30) NULL

UPDATE [dbo].[EconomicIndicators] SET [SymbolCode] = 'CM.MKT.LCAP.CD' WHERE [Indicator] = 'Stock Market Cap' AND [Source] = 'World Bank'
UPDATE [dbo].[EconomicIndicators] SET [SymbolCode] = 'CM.MKT.LCAP.GD.ZS' WHERE [Indicator] = 'Stock Market Cap Pct of GDP' AND [Source] = 'World Bank'
UPDATE [dbo].[EconomicIndicators] SET [SymbolCode] = 'CM.MKT.LDOM.NO' WHERE [Indicator] = 'Listed Domestic Companies Total' AND [Source] = 'World Bank'
UPDATE [dbo].[EconomicIndicators] SET [SymbolCode] = 'CM.MKT.TRAD.CD' WHERE [Indicator] = 'Stocks Traded Total Value' AND [Source] = 'World Bank'
UPDATE [dbo].[EconomicIndicators] SET [SymbolCode] = 'CM.MKT.TRAD.GD.ZS' WHERE [Indicator] = 'Stocks Traded Total Value Pct of GDP' AND [Source] = 'World Bank'
UPDATE [dbo].[EconomicIndicators] SET [SymbolCode] = 'NY.GDP.MKTP.CD' WHERE [Indicator] = 'GDP' AND [Source] = 'World Bank'
UPDATE [dbo].[EconomicIndicators] SET [SymbolCode] = 'NY.GDP.PCAP.CD' WHERE [Indicator] = 'GDP Per Capita' AND [Source] = 'World Bank'
UPDATE [dbo].[EconomicIndicators] SET [SymbolCode] = 'SP.POP.TOTL' WHERE [Indicator] = 'Population' AND [Source] = 'World Bank'
UPDATE [dbo].[EconomicIndicators] SET [SymbolCode] = 'BN.CAB.XOKA.GD.ZS' WHERE [Indicator] = 'Current Account Pct of GDP' AND [Source] = 'World Bank'
UPDATE [dbo].[EconomicIndicators] SET [SymbolCode] = 'BN.CAB.XOKA.CD' WHERE [Indicator] = 'Current Account' AND [Source] = 'World Bank'
UPDATE [dbo].[EconomicIndicators] SET [SymbolCode] = 'GC.XPN.TOTL.GD.ZS' WHERE [Indicator] = 'Government Expense' AND [Source] = 'World Bank'