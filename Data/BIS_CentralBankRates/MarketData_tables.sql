CREATE TABLE [MarketSymbols] (
    [Code] VARCHAR(10) NOT NULL PRIMARY KEY,
    [Description] VARCHAR(50) NULL,
	[Category] VARCHAR(20) NOT NULL,
    [Country] VARCHAR(50) NOT NULL,
	[Source] VARCHAR(20) NOT NULL
)
GO

CREATE TABLE [MarketData] (
    [DataId] INT IDENTITY(1,1) PRIMARY KEY,
    [SymbolCode] VARCHAR(10) NOT NULL,
    [Date] DATE NOT NULL,
    [Value] DECIMAL(18, 4) NOT NULL,
	FOREIGN KEY (SymbolCode) REFERENCES MarketSymbols(Code)
)
GO