# 🚍 Port Authority Bus Terminal Passenger Forecasting & Analytics

## 📊 Project Overview
Comprehensive end-to-end data analytics solution forecasting passenger demand at the Port Authority Bus Terminal from 2026-2030 using **SARIMAX time-series modeling**. This project consolidates 168+ Excel sheets (2020-2025 historical data), builds a SQL Server data warehouse with automated ETL pipelines, develops advanced SARIMA forecasting models in R, and delivers interactive Power BI dashboards to support capacity planning and operational decision-making.

**Key Business Question:** How can the Port Authority design temporary staging facilities to accommodate projected passenger volumes while optimizing for seasonal peaks and carrier-specific demand patterns?

---

## 🎯 Key Findings

### Passenger Volume Projections (2026-2030)
- **Total 5-Year Volume:** 41.59 million passengers
- **2026 Forecast:** 6.73 million passengers
- **2030 Forecast:** 6.55 million passengers
- **Peak Years:** 2028-2029 (highest annual demand)
- **Weekly Peak Capacity:** 232,000 - 236,000 passengers

### Recovery vs. Pre-COVID Baseline
- **2019 Baseline:** 1.28 million passengers
- **2025 Current:** 1.33 million passengers (already exceeded 2019 levels)
- **Recovery Status:** Full recovery achieved; all forecast years remain above pre-COVID volumes

### Seasonal Patterns
- **Peak Months:** June - July (>1M passengers/month), September - October
- **Low Season:** January - February
- **Peak Weeks:** Specific high-demand weeks identified in February, April, and July

### Carrier Market Share
- **Dominant Carrier:** NJ Transit (largest market share through 2030)
- **Secondary Carriers:** Coach USA, Peter Pan/Bonanza, HCEE - Community
- **Growth Leaders:** Smaller carriers showing higher CAGR but modest absolute volumes

---

## 🛠️ Technologies Used

| Category | Tools |
|----------|-------|
| **Data Consolidation** | Excel, Python (Pandas) |
| **Data Warehousing** | SQL Server 2019, SSMS |
| **ETL Development** | SQL Server Integration Services (SSIS), Visual Studio |
| **Forecasting & Modeling** | R (SARIMAX, ETS), Python (Time Series Analysis) |
| **Business Intelligence** | Power BI, DAX |
| **Statistical Analysis** | R (correlation analysis, regression, ACF/PACF diagnostics) |
| **Version Control** | Git, GitHub |

---


---

## 🗄️ Data Warehouse Architecture

### Star Schema Design

**Fact Table:**
- `Fact_Passenger_Departures` (Grain: Weekly observations per carrier)
  - Passenger_Departures, Bus_Departures, Passengers_Per_Bus
  - Recovery metrics, moving averages
  - Foreign keys to all dimensions

**Dimension Tables:**
- `Dim_Date` - Week, Month, Quarter, Year, Season, Fiscal Year
- `Dim_Carrier` - Carrier name, full name, service type
- `Dim_Service_Type` - Service classification
- `Dim_Weather` - Temperature, precipitation, snow, severe weather flags
- `Dim_Event` - Holidays, NYC events, tourism peaks
- `Dim_COVID_Status` - Pandemic phases (Pre/During/Post/Recovery)

**Aggregate Tables (for Power BI performance):**
- `tbl_Monthly_Carrier_Summary` - Monthly performance by carrier
- `tbl_Quarterly_Summary` - Quarterly trends
- `tbl_COVID_Impact_Summary` - Period-over-period COVID impact
- `tbl_Carrier_Performance_KPIs` - Efficiency metrics & rankings

![Data Warehouse Schema](docs/DataWarehouse_Schema.png)

---

## 🔄 ETL Pipeline

### Package 1: LoadDataWarehouse
**Purpose:** Load cleaned data into star schema  
**Process:**
1. Truncate staging tables
2. Load dimension tables (SCD Type 1)
3. Generate surrogate keys
4. Load fact table with referential integrity checks
5. Data quality validation & error logging

### Package 2: Load_Analytical_Aggregates
**Purpose:** Create pre-aggregated summary tables for dashboards  
**Process:**
1. Read from Fact_Passenger_Departures
2. Aggregate by month, quarter, carrier, and COVID period
3. Calculate KPIs (recovery %, efficiency, growth rates)
4. Load summary tables for Power BI DirectQuery

**Execution Frequency:** Weekly (automated via SQL Server Agent)

---

## 📈 Forecasting Methodology: SARIMAX Model

### Why SARIMA?
**SARIMA (Seasonal AutoRegressive Integrated Moving Average)** was selected as the primary forecasting model because it explicitly captures both **trend and seasonality** in passenger volume data, which are critical drivers of bus terminal demand [file:3].

### SARIMAX Model Components

| Component | Description | Our Model |
|-----------|-------------|-----------|
| **AR (p)** | Autoregressive order - past values predicting future | Optimized via ACF/PACF |
| **I (d)** | Differencing order - makes data stationary | d=1 (first-order difference) |
| **MA (q)** | Moving average order - past forecast errors | Optimized via ACF/PACF |
| **Seasonal AR (P)** | Seasonal autoregressive component | Captures yearly patterns |
| **Seasonal I (D)** | Seasonal differencing | D=1 (removes yearly trend) |
| **Seasonal MA (Q)** | Seasonal moving average | Captures seasonal shocks |
| **s** | Seasonal period | s=52 (weekly data, 52 weeks/year) |
| **Exogenous (X)** | External predictors | Weather, events, COVID period |

### Model Development Process

**1. Data Preparation & Stationarity Testing**
Time series preparation
ts_passengers <- ts(data$Passenger_Departures, frequency = 52)

ADF test for stationarity
adf.test(ts_passengers) # Check if differencing needed

ACF/PACF plots for order selection
acf(diff(ts_passengers))
pacf(diff(ts_passengers))

**2. SARIMAX Model Specification**
Fit SARIMAX model with exogenous variables
sarima_model <- auto.arima(
ts_passengers,
xreg = cbind(Temperature, Holidays, COVID_Period),
seasonal = TRUE,
stepwise = FALSE,
approximation = FALSE
)

**3. Residual Diagnostics**
- **Ljung-Box Test:** Confirms no autocorrelation in residuals
- **Normality Test:** Q-Q plot validates normal distribution assumption
- **ACF of Residuals:** Ensures white noise (no remaining patterns)

**4. Forecast Generation (2026-2030)**
Generate 260-week forecast (5 years × 52 weeks)
forecast_sarima <- forecast(
sarima_model,
xreg = future_exogenous_variables,
h = 260,
level = c(80, 95) # Confidence intervals
)


### Model Strengths
✅ **Captures Seasonality:** Weekly and yearly seasonal patterns explicitly modeled  
✅ **Incorporates Exogenous Factors:** Weather, holidays, and COVID phases improve accuracy  
✅ **Statistical Rigor:** ACF/PACF diagnostics ensure proper model specification  
✅ **Confidence Intervals:** Quantifies forecast uncertainty for risk management  
✅ **Handles Trend:** Differencing removes non-stationary trends in passenger growth  

### Model Limitations
⚠️ **Expanding Confidence Intervals:** Uncertainty increases for 2029-2030 forecasts  
⚠️ **Assumes Linear Patterns:** May underestimate sudden structural changes  
⚠️ **Requires Stationarity:** Data transformations needed for proper fitting  

### Validation Results
- **In-Sample Fit:** RMSE = 8,240 passengers/week
- **Out-of-Sample Accuracy (2024-2025):** MAPE = 6.8%
- **Residual Autocorrelation:** None detected (Ljung-Box p > 0.05)

---

## 📊 Power BI Dashboards

### Dashboard 1: Passenger Volume Forecast 2026-2030
**Answers:** How many passengers will use the terminal?  
**Key Visuals:**
- Annual passenger totals (bar chart)
- Weekly forecast trend (area chart)
- 5-year cumulative total KPI (41.59M)
- Max weekly capacity gauge (232K-236K)

### Dashboard 2: Predictive Factors & Demand Drivers
**Answers:** What drives passenger demand?  
**Key Visuals:**
- Top 10 predictive factors (bar chart)
- Factor category treemap (Historical, Calendar, Weather, Carrier)
- Statistical significance scatter plot (p-values)
- Correlation matrix

**Top Drivers:**
1. Historical demand (lagged passengers, moving averages)
2. Service supply (bus departures, capacity)
3. Calendar/Seasonal (holidays, weekends, summer)

### Dashboard 3: Carrier-Level Projections & Market Share
**Answers:** What are individual carrier forecasts?  
**Key Visuals:**
- Carrier trend lines (2026-2030)
- 2030 market share donut chart
- CAGR comparison waterfall
- Carrier growth table (2026 vs. 2030)

### Dashboard 4: Peak Demand Periods
**Answers:** When are the busiest times?  
**Key Visuals:**
- Monthly demand matrix (by year)
- Busiest months bar chart (June-July, September-October peaks)
- Busiest weeks table (specific dates > 230K passengers)
- Annual/Monthly/Weekly peak KPIs

### Dashboard 5: Recovery Analysis (2019 vs. Current)
**Answers:** How does usage compare to pre-COVID 2019?  
**Key Visuals:**
- 2019 baseline vs. 2025 current KPI cards
- Recovery % trend (area chart)
- Waterfall change by year
- Yearly comparison table (status flags: Above 2019 ✓)

---

## 🚀 Installation & Setup

### Prerequisites
- SQL Server 2019+ with SSIS integration
- Visual Studio 2019+ with SSIS extensions
- SQL Server Management Studio (SSMS)
- R 4.0+ with packages: `forecast`, `tseries`, `lmtest`, `tidyverse`
- Power BI Desktop
- Python 3.8+ (optional, for data prep)

### Step 2: ETL Execution
Open ETL/PortAuthority_ETL.sln in Visual Studio

Update connection managers with your SQL Server instance

Run 01_LoadDataWarehouse.dtsx

Run 02_Load_Analytical_Aggregates.dtsx

Verify data in SSMS (check row counts in fact/dim tables)


Step 4: Open Power BI Dashboard
Open PowerBI/PortAuthority_Dashboard.pbix

Refresh data connection to your SQL Server

Explore 5 dashboard pages


---

## 📌 Key Business Recommendations

Based on the SARIMA forecast analysis, we recommend the Port Authority:

1. **Design for Sustained Peak Capacity**
   - Size temporary staging facilities for **weekly peaks of 232K-236K passengers**
   - Plan infrastructure around **2028-2029 peak years**, not 2026 baseline

2. **Prioritize Commuter Service & NJ Transit Coordination**
   - NJ Transit dominates market share; coordinate scheduling & bay assignments
   - Peak demand: Sundays, Mondays, and weekday mornings

3. **Align Staffing with Seasonal Demand**
   - Increase capacity **May-October** (especially June-July, September-October)
   - Schedule maintenance during **low-demand winter months** (January-February)

4. **Maintain Year-Round Operational Readiness**
   - Weekly baseline remains consistently high; avoid scaling back off-season operations

5. **Monitor Recovery Metrics**
   - Terminal has exceeded 2019 pre-COVID levels; update capacity models quarterly

6. **Enhance Forecasting with Additional Data**
   - Incorporate regional employment trends, event calendars, tourism data
   - Integrate real-time carrier data for dynamic SARIMAX model updates

7. **Plan for Carrier-Specific Growth**
   - Allocate flexible staging/boarding capacity for carrier mix shifts

---

## 📊 Sample Results

### SARIMA Model Parameters (Final Specification)
### Forecast Accuracy Metrics
| Metric | Training Set | Test Set (2024-2025) |
|--------|-------------|----------------------|
| **RMSE** | 8,240 | 9,150 |
| **MAE** | 6,540 | 7,210 |
| **MAPE** | 5.8% | 6.8% |

### Top Carriers by 2030 Market Share
1. **NJ Transit** - 86.95%
2. **Coach USA** - 4.87%
3. **Peter Pan/Bonanza** - 2.06%
4. **Greyhound** - 1.03%
5. **Others** - 5.09%

---
This project is developed for academic and portfolio purposes. Data sources are anonymized where applicable.

---

## 🙏 Acknowledgments

- Port Authority of New York & New Jersey (data provider)
- University of New Haven
- Professor Dr. Pindaro Demertzoglou  for project guidance

---

**⭐ If you found this project useful, please consider starring this repository!**
