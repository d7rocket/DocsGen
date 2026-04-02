# Power BI Project: Sales Analytics Dashboard

## Overview

The Sales Analytics Dashboard provides real-time visibility into regional sales performance, pipeline health, and revenue forecasting for the North American division. Built on a star schema with fact tables for transactions and dimensions for products, regions, and time periods.

Key metrics tracked:
- Monthly Recurring Revenue (MRR) by region
- Sales pipeline conversion rates
- Year-over-year growth comparisons
- Top 10 products by revenue contribution

The dashboard serves both the executive leadership team (summary KPIs) and regional sales managers (detailed drill-through pages).

## Data Source

### Primary Sources

| Source | Type | Refresh | Description |
|--------|------|---------|-------------|
| SQL Server (PROD) | DirectQuery | Real-time | Main transactional database for orders and invoices |
| Dynamics 365 CRM | Import | Daily 6AM | Customer and pipeline data |
| SharePoint List | Import | Hourly | Regional targets and quotas |
| Excel (Finance) | Import | Weekly | Budget allocations and forecast adjustments |

### Connection Architecture

The data flows through a gateway-mediated connection to the on-premises SQL Server instance, while cloud sources connect directly through Power BI Service credentials. All connections use service accounts with read-only permissions.

## M Query

### Sales Fact Table Transform

```m
let
    Source = Sql.Database("sqlprod.company.com", "SalesDB"),
    Sales = Source{[Schema="dbo", Item="FactSales"]}[Data],
    FilteredRows = Table.SelectRows(Sales, each [OrderDate] >= #date(2024, 1, 1)),
    AddedMargin = Table.AddColumn(FilteredRows, "GrossMargin",
        each [Revenue] - [COGS], type number),
    RoundedMargin = Table.TransformColumns(AddedMargin,
        {{"GrossMargin", each Number.Round(_, 2), type number}})
in
    RoundedMargin
```

This query connects to the production SQL Server, filters to current-year data, and calculates gross margin as a computed column. The margin calculation is performed in Power Query rather than DAX to reduce model complexity.

### Date Dimension Generator

```m
let
    StartDate = #date(2020, 1, 1),
    EndDate = #date(2026, 12, 31),
    DateList = List.Dates(StartDate, Duration.Days(EndDate - StartDate) + 1, #duration(1,0,0,0)),
    DateTable = Table.FromList(DateList, Splitter.SplitByNothing(), {"Date"}),
    AddedYear = Table.AddColumn(DateTable, "Year", each Date.Year([Date]), Int64.Type),
    AddedMonth = Table.AddColumn(AddedYear, "Month", each Date.Month([Date]), Int64.Type),
    AddedQuarter = Table.AddColumn(AddedMonth, "Quarter", each "Q" & Text.From(Date.QuarterOfYear([Date])), type text)
in
    AddedQuarter
```

Custom date dimension generated entirely in M to avoid dependency on external calendar tables.
