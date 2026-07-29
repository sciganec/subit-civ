# Hypothesis Testing: Caral‑Supe Formation and Decline
Using the SUBIT heuristic framework and the fact database.


```python
import sys, os, sqlite3, pandas as pd

# Absolute path to the database – adjust if your project folder is different
DB_PATH = r'C:\Users\sciga\subit-civ\caral_facts.sqlite'
if not os.path.exists(DB_PATH):
    # Fallback: try relative path (notebook run from inside notebooks/)
    DB_PATH = '../caral_facts.sqlite'

print('Using database:', os.path.abspath(DB_PATH))
conn = sqlite3.connect(DB_PATH)
print('Connected.')
```

    Using database: C:\Users\sciga\subit-civ\caral_facts.sqlite
    Connected.
    


```python
# Load experiments
exp_df = pd.read_sql("SELECT * FROM experiments", conn)
exp_df
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>experiment_uuid</th>
      <th>title</th>
      <th>research_question</th>
      <th>null_hypothesis_rule_id</th>
      <th>alternative_hypothesis_rule_id</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>d64bea1b-ae6a-4182-851a-4963397f089c</td>
      <td>Testing Formative Phase Hypotheses</td>
      <td>Which subsystem drove monumentality first?</td>
      <td>7</td>
      <td>7</td>
    </tr>
    <tr>
      <th>1</th>
      <td>297657d3-ec05-4e8b-ac45-f99f7cf11395</td>
      <td>Testing Decline Phase Hypotheses</td>
      <td>Sudden collapse or managed adaptation?</td>
      <td>8</td>
      <td>10</td>
    </tr>
  </tbody>
</table>
</div>




```python
# For each experiment, show discriminating tests
for _, row in exp_df.iterrows():
    exp_uuid = row['experiment_uuid']
    title = row['title']
    tests = pd.read_sql(f"SELECT * FROM discriminating_tests WHERE experiment_uuid = '{exp_uuid}'", conn)
    print(f"Experiment: {title}")
    display(tests)
    print()
```

    Experiment: Testing Formative Phase Hypotheses
    


<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>test_uuid</th>
      <th>experiment_uuid</th>
      <th>description</th>
      <th>expected_result_if_null</th>
      <th>expected_result_if_alternative</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>test-form-001</td>
      <td>d64bea1b-ae6a-4182-851a-4963397f089c</td>
      <td>Isotopes: marine protein % at Caral vs Aspero</td>
      <td>similar (&gt;40%)</td>
      <td>Caral &lt; 30%</td>
    </tr>
    <tr>
      <th>1</th>
      <td>test-form-002</td>
      <td>d64bea1b-ae6a-4182-851a-4963397f089c</td>
      <td>Site size: inland vs coastal</td>
      <td>similar sizes</td>
      <td>inland much larger</td>
    </tr>
    <tr>
      <th>2</th>
      <td>test-form-003</td>
      <td>d64bea1b-ae6a-4182-851a-4963397f089c</td>
      <td>Earliest radiocarbon dates</td>
      <td>coastal older or same</td>
      <td>inland older</td>
    </tr>
  </tbody>
</table>
</div>


    
    Experiment: Testing Decline Phase Hypotheses
    


<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>test_uuid</th>
      <th>experiment_uuid</th>
      <th>description</th>
      <th>expected_result_if_null</th>
      <th>expected_result_if_alternative</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>test-decl-001</td>
      <td>297657d3-ec05-4e8b-ac45-f99f7cf11395</td>
      <td>Destruction layer (thin, synchronous)</td>
      <td>present, same time everywhere</td>
      <td>absent or asynchronous</td>
    </tr>
    <tr>
      <th>1</th>
      <td>test-decl-002</td>
      <td>297657d3-ec05-4e8b-ac45-f99f7cf11395</td>
      <td>Abandonment timing (inland vs coastal)</td>
      <td>inland first</td>
      <td>coastal first or simultaneous</td>
    </tr>
    <tr>
      <th>2</th>
      <td>test-decl-003</td>
      <td>297657d3-ec05-4e8b-ac45-f99f7cf11395</td>
      <td>Cultural continuity at Vichama/Peñico</td>
      <td>abrupt change</td>
      <td>continuity in architecture/symbols</td>
    </tr>
  </tbody>
</table>
</div>


    
    


```python
# Hypothesis evaluation: test-form-001 (marine protein %)
# Load marine protein observations
conn_check = sqlite3.connect(DB_PATH)   # fresh connection to be safe
obs_marine = pd.read_sql("SELECT * FROM observations WHERE type='marine_protein_%'", conn_check)
print(f"Found {len(obs_marine)} marine protein observations.")
display(obs_marine)
conn_check.close()
```

    Found 2 marine protein observations.
    


<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>obs_id</th>
      <th>site_id</th>
      <th>source_id</th>
      <th>type</th>
      <th>value</th>
      <th>year_from</th>
      <th>year_to</th>
      <th>method</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>18</td>
      <td>1</td>
      <td>5</td>
      <td>marine_protein_%</td>
      <td>25.0</td>
      <td>-2700</td>
      <td>-2000</td>
      <td>Pezo-Lanfranco2022</td>
    </tr>
    <tr>
      <th>1</th>
      <td>19</td>
      <td>2</td>
      <td>5</td>
      <td>marine_protein_%</td>
      <td>45.0</td>
      <td>-2700</td>
      <td>-2000</td>
      <td>Pezo-Lanfranco2022</td>
    </tr>
  </tbody>
</table>
</div>



```python
# Evaluate the test
conn_eval = sqlite3.connect(DB_PATH)
obs_marine_eval = pd.read_sql("SELECT * FROM observations WHERE type='marine_protein_%'", conn_eval)
caral_marine = obs_marine_eval[obs_marine_eval['site_id'] == 1]['value']
aspero_marine = obs_marine_eval[obs_marine_eval['site_id'] == 2]['value']

if not caral_marine.empty:
    mean_caral = caral_marine.mean()
    print(f"Mean marine protein at Caral: {mean_caral:.1f}%")
    if mean_caral < 30:
        print("Result: Supports alternative hypothesis (agricultural primacy)")
    else:
        print("Result: Supports null hypothesis (complementarity)")
else:
    print("No marine protein data for Caral.")

if not aspero_marine.empty:
    print(f"Mean marine protein at Aspero: {aspero_marine.mean():.1f}%")
conn_eval.close()
```

    Mean marine protein at Caral: 25.0%
    Result: Supports alternative hypothesis (agricultural primacy)
    Mean marine protein at Aspero: 45.0%
    


```python
# Additional test: test-decl-001 (destruction layer) — using abandonment dates as proxy
conn_abandon = sqlite3.connect(DB_PATH)
obs_abandon = pd.read_sql("SELECT * FROM observations WHERE type IN ('abandonment_year','founding_year')", conn_abandon)
print(f"Found {len(obs_abandon)} abandonment/founding records.")
display(obs_abandon)
conn_abandon.close()
```

    Found 3 abandonment/founding records.
    


<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>obs_id</th>
      <th>site_id</th>
      <th>source_id</th>
      <th>type</th>
      <th>value</th>
      <th>year_from</th>
      <th>year_to</th>
      <th>method</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>22</td>
      <td>1</td>
      <td>4</td>
      <td>abandonment_year</td>
      <td>-1850.0</td>
      <td>-1800</td>
      <td>Shady2025_Caral</td>
      <td>None</td>
    </tr>
    <tr>
      <th>1</th>
      <td>23</td>
      <td>2</td>
      <td>3</td>
      <td>abandonment_year</td>
      <td>-1900.0</td>
      <td>-1850</td>
      <td>Sandweiss2009_Aspero</td>
      <td>None</td>
    </tr>
    <tr>
      <th>2</th>
      <td>24</td>
      <td>3</td>
      <td>4</td>
      <td>founding_year</td>
      <td>-1750.0</td>
      <td>-1700</td>
      <td>Shady2025_Vichama</td>
      <td>None</td>
    </tr>
  </tbody>
</table>
</div>



```python
# Simple logic: if all abandonment dates are within a narrow window, supports seismic shock (synchronous)
conn_sync = sqlite3.connect(DB_PATH)
obs_abandon_sync = pd.read_sql("SELECT * FROM observations WHERE type IN ('abandonment_year','founding_year')", conn_sync)
abandon_dates = obs_abandon_sync[obs_abandon_sync['type'] == 'abandonment_year']
if len(abandon_dates) >= 2:
    range_years = abandon_dates['year_from'].max() - abandon_dates['year_from'].min()
    print(f"Abandonment date range: {range_years} years")
    if range_years <= 100:
        print("Interpretation: relatively synchronous → consistent with seismic shock")
    else:
        print("Interpretation: spread over >100 years → more consistent with gradual processes")
else:
    print("Not enough abandonment data to test.")
conn_sync.close()
```

    Abandonment date range: 50 years
    Interpretation: relatively synchronous → consistent with seismic shock
    


```python
# Close any remaining connection (if needed)
try:
    conn.close()
except:
    pass
```


```python
# Check radiocarbon dates
conn_radio = sqlite3.connect(DB_PATH)
radio = pd.read_sql("SELECT * FROM observations WHERE type='earliest_radiocarbon_date'", conn_radio)
display(radio)
conn_radio.close()
```


<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>obs_id</th>
      <th>site_id</th>
      <th>source_id</th>
      <th>type</th>
      <th>value</th>
      <th>year_from</th>
      <th>year_to</th>
      <th>method</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>27</td>
      <td>1</td>
      <td>6</td>
      <td>earliest_radiocarbon_date</td>
      <td>-2627.0</td>
      <td>-2700</td>
      <td>-2550</td>
      <td>Shady2001_Caral</td>
    </tr>
    <tr>
      <th>1</th>
      <td>28</td>
      <td>2</td>
      <td>6</td>
      <td>earliest_radiocarbon_date</td>
      <td>-2550.0</td>
      <td>-2700</td>
      <td>-2400</td>
      <td>Shady2001_Aspero</td>
    </tr>
  </tbody>
</table>
</div>



```python
# Compare inland vs coastal abandonment
conn_ab2 = sqlite3.connect(DB_PATH)
ab2 = pd.read_sql("SELECT sites.name, observations.* FROM observations JOIN sites ON observations.site_id = sites.site_id WHERE observations.type='abandonment_year'", conn_ab2)
display(ab2)
conn_ab2.close()
```


<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>name</th>
      <th>obs_id</th>
      <th>site_id</th>
      <th>source_id</th>
      <th>type</th>
      <th>value</th>
      <th>year_from</th>
      <th>year_to</th>
      <th>method</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Caral</td>
      <td>22</td>
      <td>1</td>
      <td>4</td>
      <td>abandonment_year</td>
      <td>-1850.0</td>
      <td>-1800</td>
      <td>Shady2025_Caral</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Aspero</td>
      <td>23</td>
      <td>2</td>
      <td>3</td>
      <td>abandonment_year</td>
      <td>-1900.0</td>
      <td>-1850</td>
      <td>Sandweiss2009_Aspero</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Huaricanga</td>
      <td>25</td>
      <td>5</td>
      <td>6</td>
      <td>abandonment_year</td>
      <td>-2000.0</td>
      <td>-2100</td>
      <td>-1900</td>
      <td>Haas2004_Huaricanga</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Bandurria</td>
      <td>26</td>
      <td>6</td>
      <td>3</td>
      <td>abandonment_year</td>
      <td>-1900.0</td>
      <td>-2000</td>
      <td>-1800</td>
      <td>Sandweiss2009_Bandurria</td>
    </tr>
  </tbody>
</table>
</div>



```python

```
