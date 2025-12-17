import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# STEP 1: LOAD AND PREPARE DATA WITH EXOGENOUS VARIABLES
# =============================================================================
print("=" * 80)
print("SARIMAX FORECASTING WITH EXOGENOUS VARIABLES")
print("Bus Terminal Passenger Projection 2026–2030")
print("=" * 80)

# Load data
df = pd.read_csv('FinalDataset.csv')
df['Week_Date'] = pd.to_datetime(df['Week_Date'])

# Aggregate weekly
weekly_data = df.groupby('Week_Date').agg({
    'Passenger_Departures': 'sum',
    'Is_Holiday': 'max',
    'Is_Tourism_Peak': 'max',
    'Is_Severe_Weather': 'max',
    'Is_High_Inflation': 'max',
    'Year': 'first',
    'Month': 'first'
}).reset_index()

# Set index
weekly_data.set_index('Week_Date', inplace=True)
weekly_data = weekly_data.asfreq('W')

# =======================
# DEPENDENT VARIABLE
# =======================
ts_data = weekly_data['Passenger_Departures'].astype(float)

# =======================
# EXOGENOUS VARIABLES (FIXED)
# =======================
exog_vars = weekly_data[
    ['Is_Holiday', 'Is_Tourism_Peak', 'Is_Severe_Weather', 'Is_High_Inflation']
].fillna(0).astype(int)

print(f"\nData Summary:")
print(f"  Total weeks: {len(ts_data)}")
print(f"  Average weekly passengers: {ts_data.mean():,.0f}")

# =============================================================================
# STEP 2: STATIONARITY TEST
# =============================================================================
print("\n" + "=" * 80)
print("STEP 1: Stationarity Test (ADF)")
print("=" * 80)

if ts_data.nunique() <= 1:
    print("⚠ ADF test skipped: time series is constant or nearly constant")
    print("  Proceeding directly to SARIMAX modeling")
else:
    adf_stat, p_value, *_ = adfuller(ts_data.dropna())
    print(f"ADF Statistic: {adf_stat:.4f}")
    print(f"P-value: {p_value:.4f}")

# =============================================================================
# STEP 3: FIT SARIMAX MODEL
# =============================================================================
print("\n" + "=" * 80)
print("STEP 2: FITTING SARIMAX MODEL")
print("=" * 80)

p, d, q = 1, 1, 1
P, D, Q, s = 1, 1, 1, 52

model = SARIMAX(
    ts_data,
    exog=exog_vars,
    order=(p, d, q),
    seasonal_order=(P, D, Q, s),
    enforce_stationarity=False,
    enforce_invertibility=False
)

results = model.fit(disp=False)
print("✓ Model trained successfully")

print("\nMODEL DIAGNOSTICS")
print(f"AIC: {results.aic:.2f}")
print(f"BIC: {results.bic:.2f}")

# =============================================================================
# STEP 4: FUTURE EXOGENOUS VARIABLES (2026–2030)
# =============================================================================
print("\n" + "=" * 80)
print("STEP 3: PREPARING FUTURE EXOGENOUS VARIABLES")
print("=" * 80)

forecast_steps = 260
last_date = ts_data.index[-1]
forecast_dates = pd.date_range(
    start=last_date + pd.Timedelta(weeks=1),
    periods=forecast_steps,
    freq='W'
)

np.random.seed(42)

future_exog = pd.DataFrame({
    'Is_Holiday': np.random.binomial(1, exog_vars['Is_Holiday'].mean(), forecast_steps),
    'Is_Tourism_Peak': np.random.binomial(1, exog_vars['Is_Tourism_Peak'].mean(), forecast_steps),
    'Is_Severe_Weather': np.random.binomial(1, exog_vars['Is_Severe_Weather'].mean(), forecast_steps),
    'Is_High_Inflation': 0
}, index=forecast_dates)

# Seasonal tourism
future_exog['Month'] = future_exog.index.month
future_exog.loc[future_exog['Month'].isin([6,7,8,9,10]), 'Is_Tourism_Peak'] = 1

# Holiday weeks
future_exog['Week'] = future_exog.index.isocalendar().week
future_exog.loc[future_exog['Week'].isin([1, 47, 51, 52]), 'Is_Holiday'] = 1

future_exog = future_exog[
    ['Is_Holiday', 'Is_Tourism_Peak', 'Is_Severe_Weather', 'Is_High_Inflation']
].astype(int)

# =============================================================================
# STEP 5: FORECAST
# =============================================================================
print("\n" + "=" * 80)
print("STEP 4: GENERATING FORECAST")
print("=" * 80)

forecast = results.get_forecast(steps=forecast_steps, exog=future_exog)
forecast_mean = forecast.predicted_mean
forecast_ci = forecast.conf_int()

forecast_df = pd.DataFrame({
    'Week_Date': forecast_dates,
    'Forecasted_Passengers': forecast_mean,
    'Lower_Bound_95': forecast_ci.iloc[:, 0],
    'Upper_Bound_95': forecast_ci.iloc[:, 1]
})

forecast_df['Year'] = forecast_df['Week_Date'].dt.year
forecast_df['Month'] = forecast_df['Week_Date'].dt.month

forecast_2026_2030 = forecast_df[forecast_df['Year'] >= 2026]

# =============================================================================
# STEP 6: ANNUAL PROJECTIONS
# =============================================================================
annual_forecast = forecast_2026_2030.groupby('Year').agg({
    'Forecasted_Passengers': 'sum',
    'Lower_Bound_95': 'sum',
    'Upper_Bound_95': 'sum'
}).reset_index()

annual_forecast.columns = [
    'Year', 'Projected_Passengers',
    'Conservative_Estimate', 'Optimistic_Estimate'
]

baseline_2019 = 125398 * 52

annual_forecast['Recovery_%'] = (
    annual_forecast['Projected_Passengers'] / baseline_2019 * 100
).round(1)

print("\nANNUAL FORECAST (2026–2030)")
print(annual_forecast.to_string(index=False))

# =============================================================================
# STEP 7: SAVE OUTPUTS
# =============================================================================
annual_forecast.to_csv(
    'SARIMAX_Annual_Forecast_2026_2030_With_Exog.csv',
    index=False
)

forecast_2026_2030.to_csv(
    'SARIMAX_Weekly_Forecast_2026_2030_With_Exog.csv',
    index=False
)

print("\nFILES SAVED SUCCESSFULLY")
print("=" * 80)
