#!/usr/bin/env python
# %% imports
import json
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, dash_table

# %% setup
URL = "https://w3c-ccg.github.io/traceability-interop/reports/"
url = requests.get(URL)

# %% process initial json
data = json.loads(url.text)

# %% loop and get each report and assign to provider from url
items = data['items']
report_sources = []
for item in items:
    if '.json' in item:
        report_sources.append(item) 

reports = []
for report_source in report_sources:
    provider = report_source.rsplit('-', 1)[1].replace('.json', '')
    print(provider)
    report = json.loads(requests.get(report_source).text)
    reports.append({
        'provider': provider,
        'report': report
    })

# %% debug check
# print(json.dumps(reports[0], indent=2))
# print(
#     reports[0]['provider'],
#     reports[0]['report']['collection']['info']['name'].replace(' Tutorial',''),
# )

# %% set up dataframe(s)
df = pd.DataFrame(pd.json_normalize(reports))
df['report.collection.info.name'] = df['report.collection.info.name'].str.replace(' Tutorial', '')
df_results = df[[
    'provider',
    'report.collection.info.name',
    'report.run.stats.iterations.failed',
    'report.run.stats.items.total'
]].copy()
df_results.columns = ['Provider', 'Test', 'Failed', 'Total']
df_results['Percentage'] = (df_results['Total']-df_results['Failed']) / df_results['Total']

# %% setup dash
app = Dash(
    title="Traceability Interop Test Results",
    external_stylesheets=[dbc.themes.SLATE]
)

fig = dash_table.DataTable(
    id='results_able',
    columns=[{"name": i, "id": i} 
        for i in df_results.columns],
    data=df_results.to_dict('records'),
    style_cell=dict(textAlign='center'),
    editable=False,
    row_selectable=False,
    column_selectable=False,
    cell_selectable=False,
    filter_action="native",
    sort_action="native",
)


# %%


# %% main it up
if __name__ == "__main__":
    app.run_server()