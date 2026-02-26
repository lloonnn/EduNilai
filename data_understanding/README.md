# EduNilai — Data Understanding

---

## 1. Overview

This document describes the datasets collected and used in the **EduNilai** project, which investigates the financial return on investment (ROI) of a Malaysian university degree. The study spans **2010–2025** and covers graduate employment outcomes, household income, labour force statistics, tuition fees, inflation, and ASEAN regional benchmarks.

---

## 2. Datasets Summary

| # | Dataset | File | Source | Coverage |
|---|---------|------|--------|----------|
| 1 | Consumer Price Index (CPI) | `cpi_2010_onwards.csv` | DOSM OpenDOSM | Annual, 2010–2025 |
| 2 | Graduate SRU by Sex | `graduate_underemployment_sex.csv` | DOSM LFS (quarterly) | 2016 Q1 – 2023 Q3 |
| 3 | Graduate SRU by Age | `graduate_underemployment_age.csv` | DOSM LFS (quarterly) | 2017 Q1 – 2025 Q3 |
| 4 | Youth Unemployment (Monthly) | `youth_unemployment_monthly.csv` | DOSM LFS (monthly) | 2016–2025 |
| 5 | Annual Labour Force Statistics by Sex | `lfs_annual_sex.csv` | DOSM LFS (annual) | 2010–2023 |
| 6 | Household Income — National | `hh_income_national.csv` | DOSM HIES | 2012–2022 |
| 7 | Household Income — State | `hh_income_state.csv` | DOSM HIES | 2012–2022 |
| 8 | Household Income — Percentiles | `hh_income_percentiles.csv` | DOSM HIES | 2019–2024 |
| 9 | Income Inequality (Gini) | `income_inequality_gini.csv` | DOSM HIES | 2012–2022 |
| 10 | University Tuition Fees (Raw) | `edunilai_raw_fees.csv` | UTM, UM, APU, Taylor's (scraped) | 2024–2025 |
| 11 | University Tuition Fees (Mean by Field) | `edunilai_mean_fees.csv` | UTM, UM, APU, Taylor's (scraped) | 2024–2025 |
| 12 | ASEAN Education & Labour Indicators | `asean_comparison.csv` | World Bank Open Data API | 2010–2023 |

All DOSM datasets are licensed under **CC BY 4.0**. World Bank data is licensed under **CC BY 4.0**.

---

## 3. Dataset Descriptions

### 3.1 Consumer Price Index (CPI)
**File:** `inflation/cpi_2010_onwards.csv`  
**Source:** [https://open.dosm.gov.my/data-catalogue/cpi_annual](https://open.dosm.gov.my/data-catalogue/cpi_annual)

Annual CPI for Malaysia, broken down into **13 COICOP divisions** (e.g. Food, Housing, Education, Transport). Base year = 2010. Covers 2010–2025 (224 rows).

| Column | Type | Description |
|--------|------|-------------|
| `date` | date | Year of observation (YYYY-01-01) |
| `division` | string | CPI category (e.g. `overall`, `education`, `housing`) |
| `index` | float | CPI value — base year 2010 = 100 |

**Use:** Adjusting tuition fees and graduate salaries for inflation to compute real ROI over time. The `education` division specifically tracks how education costs have changed relative to the general price level.

---

### 3.2 Graduate Skills-Related Underemployment by Sex (SRU)
**File:** `salary/graduate_underemployment_sex.csv`  
**Source:** [https://open.dosm.gov.my/data-catalogue/lfs_qtr_sru_sex](https://open.dosm.gov.my/data-catalogue/lfs_qtr_sru_sex)

Quarterly count and rate of **tertiary-educated workers employed in semi-skilled or low-skilled jobs**, disaggregated by sex. Covers 2017 Q1 – 2025 Q3 (105 rows).

| Column | Type | Description |
|--------|------|-------------|
| `date` | date | Quarter start date (YYYY-MM-DD) |
| `sex` | string | `male` or `female` |
| `sru_person` | float | Underemployed graduates ('000 persons) |
| `sru_rate` | float | Proportion of graduates that are underemployed (%) |

**Use:** Directly measures the degree mismatch problem. The gender split reveals whether female graduates face higher underemployment, which impacts their measured ROI.

---

### 3.3 Graduate Skills-Related Underemployment by Age (SRU)
**File:** `salary/graduate_underemployment_age.csv`  
**Source:** [https://open.dosm.gov.my/data-catalogue/lfs_qtr_sru_age](https://open.dosm.gov.my/data-catalogue/lfs_qtr_sru_age)

Same concept as 3.2 but broken down by **age group** (15–24, 25–34, 35–44, 45–54, 55–64). Covers 2017 Q1 – 2025 Q3 (175 rows).

| Column | Type | Description |
|--------|------|-------------|
| `date` | date | Quarter start date (YYYY-MM-DD) |
| `age` | string | Age group (e.g. `15-24`, `25-34`) |
| `sru_persons` | float | Underemployed graduates in this age group ('000) |
| `sru_rate` | float | Underemployment rate for this age group (%) |

**Use:** Determines whether young fresh graduates (15–34) face disproportionately high underemployment in early career years — a critical input for payback period calculations.

---

### 3.4 Youth Unemployment (Monthly)
**File:** `salary/youth_unemployment_monthly.csv`  
**Source:** [https://open.dosm.gov.my/data-catalogue/lfs_month_youth](https://open.dosm.gov.my/data-catalogue/lfs_month_youth)

Monthly unemployment statistics for youth aged **15–24** and **15–30**. Covers January 2016 – December 2025 (120 rows).

| Column | Type | Description |
|--------|------|-------------|
| `date` | date | Month (YYYY-MM-DD) |
| `unemployed_15_24` | float | Unemployed persons aged 15–24 ('000) |
| `u_rate_15_24` | float | Unemployment rate, ages 15–24 (%) |
| `unemployed_15_30` | float | Unemployed persons aged 15–30 ('000) |
| `u_rate_15_30` | float | Unemployment rate, ages 15–30 (%) |

**Use:** An unemployed fresh graduate earns nothing — capturing the post-graduation unemployment period is essential for accurate ROI. The 15–30 band covers the extended early-career transition period. The monthly series clearly shows the COVID-19 shock (2020–2021) and recovery.

---

### 3.5 Annual Labour Force Statistics by Sex
**File:** `salary/lfs_annual_sex.csv`  
**Source:** [https://open.dosm.gov.my/data-catalogue/lfs_year_sex](https://open.dosm.gov.my/data-catalogue/lfs_year_sex)

Annual national labour force statistics broken down by sex. Covers 2010–2023 (42 rows).

| Column | Type | Description |
|--------|------|-------------|
| `sex` | string | `both`, `male`, or `female` |
| `date` | date | Year of survey (YYYY-01-01) |
| `lf` | float | Labour force size ('000) |
| `lf_employed` | float | Number employed ('000) |
| `lf_unemployed` | float | Number unemployed ('000) |
| `lf_outside` | float | Population outside the labour force ('000) |
| `p_rate` | float | Labour force participation rate (%) |
| `u_rate` | float | Unemployment rate (%) |
| `ep_ratio` | float | Employment-to-population ratio (%) |

**Use:** Provides the baseline unemployment rate for the ROI model and reveals the gender gap in labour participation. `ep_ratio` and `lf_outside` are particularly useful for understanding the share of graduates who exit the workforce entirely.

---

### 3.6 Household Income — National
**File:** `demographic/hh_income_national.csv`  
**Source:** [https://open.dosm.gov.my/data-catalogue/hh_income](https://open.dosm.gov.my/data-catalogue/hh_income)

National-level mean and median gross monthly household income from DOSM's **Household Income and Expenditure Survey (HIES)**, conducted every 2–3 years. Covers 2012–2022 (6 rows).

| Column | Type | Description |
|--------|------|-------------|
| `date` | date | Survey year (YYYY-01-01) |
| `income_mean` | float | Mean gross monthly household income (RM) |
| `income_median` | float | Median gross monthly household income (RM) |

**Use:** Provides the non-graduate income baseline for ROI comparison. The widening gap between mean and median signals rising income inequality over time.

---

### 3.7 Household Income — State Level
**File:** `demographic/hh_income_state.csv`  
**Source:** [https://open.dosm.gov.my/data-catalogue/hh_income_state](https://open.dosm.gov.my/data-catalogue/hh_income_state)

State-level household income from HIES across 16 states. Covers 2012–2022 (96 rows).

| Column | Type | Description |
|--------|------|-------------|
| `state` | string | Malaysian state name |
| `date` | date | Survey year (YYYY-01-01) |
| `income_mean` | float | Mean gross monthly household income (RM) |
| `income_median` | float | Median gross monthly household income (RM) |

**Use:** Supports geographic inequality analysis — whether higher education yields consistent financial returns across regions, or whether returns are concentrated in high-income states like Selangor and KL.

---

### 3.8 Household Income — Percentile Distribution
**File:** `demographic/hh_income_percentiles.csv`  
**Source:** [https://open.dosm.gov.my/data-catalogue/hies_malaysia_percentile](https://open.dosm.gov.my/data-catalogue/hies_malaysia_percentile)

Income distribution across all 100 population percentiles with four statistical measures per percentile. Covers 2019–2024 (1,200 rows).

| Column | Type | Description |
|--------|------|-------------|
| `date` | date | Survey year (YYYY-01-01) |
| `percentile` | integer | Income percentile group (1–100) |
| `variable` | string | Statistic type: `mean`, `median`, `minimum`, or `maximum` |
| `income` | float | Monthly household income (RM) for this percentile and statistic |

**Use:** Enables distributional analysis beyond mean/median values. Helps assess whether graduates move into higher income brackets over time, and whether degree attainment correlates with upward income mobility.

---

### 3.9 Income Inequality — Gini Coefficient
**File:** `demographic/income_inequality_gini.csv`  
**Source:** [https://open.dosm.gov.my/data-catalogue/hh_inequality](https://open.dosm.gov.my/data-catalogue/hh_inequality)

National Gini coefficient from HIES. Covers 2012–2022 (5 rows).

| Column | Type | Description |
|--------|------|-------------|
| `date` | date | Survey year (YYYY-01-01) |
| `gini` | float | Gini coefficient (0 = perfect equality, 1 = perfect inequality) |

**Use:** Tracks whether the expansion of higher education in Malaysia has actually reduced income inequality over time, or whether graduate earnings growth has widened the gap.

---

### 3.10 University Tuition Fees — Raw Programme Data
**File:** `cost/edunilai_raw_fees.csv`  
**Source:** UTM (`admission.utm.my`), UM (official PDF), APU & Taylor's (`articles.unienrol.com`) — web-scraped

Individual programme-level tuition fees for Malaysian students across 4 universities (2 public, 2 private).

| Column | Type | Description |
|--------|------|-------------|
| `university` | string | University name (UTM, UM, APU, Taylor's) |
| `type` | string | Institution type: `Public` or `Private` |
| `field_category` | string | Standardised field (e.g. Engineering, Medicine & Health) |
| `programme` | string | Full programme name |
| `fee` | float | Total undergraduate tuition fee (RM) |

**Use:** Granular cost data for ROI calculations at the programme level. The public vs. private fee gap is a key analytical dimension.

---

### 3.11 University Tuition Fees — Mean by Field
**File:** `cost/edunilai_mean_fees.csv`  
**Source:** Derived from `edunilai_raw_fees.csv`

Aggregated mean tuition fees per field of study broken down by university, for direct use in ROI modelling.

| Column | Type | Description |
|--------|------|-------------|
| `field_category` | string | Standardised field of study |
| `UTM` | float | Mean fee at UTM (RM) |
| `UM` | float | Mean fee at UM (RM) |
| `APU` | float | Mean fee at APU (RM) |
| `Taylor's` | float | Mean fee at Taylor's (RM) |
| `Overall_Mean_RM` | float | Mean fee across all 4 universities (RM) |
| `Uni_Count` | integer | Number of universities offering this field |

**Use:** Primary cost input for the ROI and NPV calculations by field of study.

---

### 3.12 ASEAN Education & Labour Indicators
**File:** `asean/asean_comparison.csv`  
**Source:** [https://data.worldbank.org](https://data.worldbank.org) — World Bank Open Data API

Education and labour market indicators for **10 ASEAN countries** (Malaysia, Singapore, Thailand, Indonesia, Philippines, Vietnam, Myanmar, Cambodia, Brunei, Laos) collected via the World Bank API. Covers 2010–2023 (140 rows).

| Column | Type | Description |
|--------|------|-------------|
| `country_code` | string | ISO 3-letter country code |
| `country` | string | Country name |
| `year` | integer | Year of observation |
| `unemployment_advanced_edu_pct` | float | Unemployment rate, population with advanced education (%) |
| `gdp_per_capita_usd` | float | GDP per capita (current USD) |
| `education_expenditure_pct_gdp` | float | Government education spending as % of GDP |
| `labour_force_participation_rate` | float | Labour force participation rate (%) |
| `tertiary_gross_enrolment_ratio` | float | Tertiary gross enrolment ratio (%) |
| `human_capital_index` | float | World Bank Human Capital Index (0–1) |

**Use:** Benchmarks Malaysia's graduate ROI problem against regional peers — whether Malaysia spends more on education than ASEAN peers, whether graduate unemployment is uniquely high, and whether Malaysia's tertiary enrolment growth is outpacing its labour market's absorption capacity.

---

## 4. Key Findings from Data Exploration

- **Graduate underemployment is concentrated in younger age groups.** SRU rates for the 15–24 cohort are consistently and substantially higher than for older workers, meaning fresh graduates face a prolonged period of sub-optimal earnings before reaching degree-level employment.
- **Youth unemployment spiked sharply during COVID-19 (2020–2021)** and has since partially recovered, but remains elevated relative to pre-pandemic levels — disproportionately affecting the ROI of graduates from that cohort.
- **Female graduates show higher SRU rates than male graduates**, despite similar qualification levels. Combined with lower labour force participation rates, this creates a measurable gender gap in degree ROI.
- **Education CPI has risen faster than overall CPI** in several years, meaning the real cost of education is increasing faster than general living costs — compressing the financial return of a degree over time.
- **The gap between mean and median national household income has widened**, suggesting income growth is skewed toward higher earners, consistent with a degree premium that benefits some graduates significantly while leaving others behind.
- **Malaysia's tertiary gross enrolment ratio has grown significantly** relative to most ASEAN peers, but this growth is not matched by proportional improvement in employment outcomes — suggesting potential over-supply of graduates relative to graduate-level job creation.

---

## 5. Data Limitations

- HIES data is collected every 2–3 years, meaning intra-survey years require interpolation or are unavailable.
- Household income percentile data is only available from 2019 onwards, limiting longitudinal distributional analysis.
- SRU datasets begin from 2017 Q1 only, restricting historical underemployment comparison for the full 2010–2025 study period.
- Tuition fee data covers only 4 institutions; broader coverage uses PTPTN average loan amounts as a proxy where needed.
- The DOSM Salaries & Wages Survey by industry is inaccessible on current hosting infrastructure and has been replaced by the SRU dataset as the primary graduate outcomes measure.
- `asean_comparison.csv` has uneven country coverage — indicators for Myanmar, Cambodia, and Laos contain significant missing values.