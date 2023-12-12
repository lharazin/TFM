CREATE TABLE [EconomicIndicators] (
    [IndicatorId] INT IDENTITY(1,1) PRIMARY KEY,
	[Indicator] VARCHAR(50) NOT NULL,
	[Category] VARCHAR(20) NOT NULL,
	[Source] VARCHAR(20) NOT NULL,
	[Frequency] CHAR(1) NOT NULL,
	[Measure] VARCHAR(100) NOT NULL
)
GO

CREATE TABLE [IndicatorsValues] (
    [ValueId] INT IDENTITY(1,1) PRIMARY KEY,
    [IndicatorId] INT NOT NULL,
    [Period] DATETIME NOT NULL,
    [Country] VARCHAR(50) NOT NULL,
    [Value] DECIMAL(18, 4) NOT NULL,
	FOREIGN KEY (IndicatorId) REFERENCES EconomicIndicators(IndicatorId)
)
GO