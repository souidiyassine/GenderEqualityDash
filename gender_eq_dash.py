import plotly.express as px
import pandas as pd
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
from plotly.validator_cache import ValidatorCache
from plotly.graph_objects import Layout
from apriori import ar as ap
from settings import dataset_path

darkblue_color_palette = ["#00183d", "#002a69", "#003f9a", "#005ccf", "#007eff", "#49b3ff", "#75c8ff", "#8fd8ff"]
skyblue_color_palette = ["#005ccf", "#007eff", "#49b3ff", "#75c8ff", "#8fd8ff", "#b5e6ff", "#dcf0fa", "#f2fbff"]

codebook = pd.read_excel(dataset_path, sheet_name="Codebook")
df = pd.read_excel(dataset_path, sheet_name="Data")

# ap = ap[pd.DataFrame(np.sort(ap[['antecedents','consequents']].values, 1)).duplicated()]
ap = ap[~ap[['antecedents', 'consequents']].apply(frozenset, axis=1).duplicated()]
ap = ap.sort_values("lift", ascending=False)
ap = ap.round(2)

codebook = codebook.dropna(axis=0, how="all", subset=codebook.iloc[:0,4:5].columns.tolist())

df = df[df.Gender != "Combined"]
df = df.dropna(axis=1, how="all")
df = df.dropna(axis=0, how="all", subset=df.iloc[:0,4:].columns.tolist())

for index in df.index:
    if df.loc[index, 'Region'] == "Middle East & North Africa":
        df.loc[index, 'Region'] = "Middle East and North Africa"
    if df.loc[index, 'Region'] == "Europe & Central Asia":
        df.loc[index, 'Region'] = "Europe and Central Asia"

app = dash.Dash(__name__)
server = app.server

app.title="Gender Equality Analytics"
app._favicon = "favicon.png"

app.layout = html.Div(
    className="container_div",
    children=[
        html.Div(
            className="header_div",
            children=[
                html.Img(src="https://dash.gallery/dash-clinical-analytics/assets/plotly_logo.png")
            ]
        ),
        html.Div(
            className="main_div",
            children=[
                html.Div(
                    className="left_fixed_div",
                    children=[
                        html.H2("Gender Equality Analytics"),
                        html.H1("Welcome to the Gender Equality Analytics Dashboard"),
                        html.P("The Gender Equality at Home survey covers topics about gender norms, unpaid and household care, access and agency, and COVID-19's impact on these areas. It has been fielded in over 200 countries and territories."),
                        html.Div(
                            id="data_source",
                            children=[
                                html.Label("Data Source: "),
                                dcc.Link(
                                    children=[
                                        html.A("Data for Good | Facebook")
                                    ],
                                    title="Data for Good | Facebook",
                                    href="https://dataforgood.facebook.com/dfg/tools/survey-on-gender-equality-at-home#accessdata",
                                    refresh=True,
                                    target="_blank"
                                ),
                            ]
                        ),
                        html.Label("Select Category Theme:"),
                        dcc.Dropdown(
                            id="theme_dropdown",
                            options = [{'label': t.capitalize(), 'value': t.capitalize()} for t in sorted(codebook.iloc[4:, 1].unique())],
                            value=codebook.iloc[4, 1],
                            clearable=False,
                            persistence=True
                        ),
                        html.Label("Select Question:"),
                        dcc.Dropdown(
                            id="question_dropdown",
                            optionHeight=75,
                            clearable=False,
                            persistence=True
                        ),
                        html.Label("Select Answer:"),
                        dcc.Dropdown(id="answer_dropdown", clearable=False, optionHeight=40,),
                        html.Label("Select Year:"),
                        dcc.Dropdown(
                            id="year_dropdown",
                            clearable=False,
                            persistence=True
                        ),
                        html.Div(
                            id="answer_gender_proportion_div",
                            children=[
                                html.Div(
                                    children=[
                                        html.Label("Group results by:"),
                                        dcc.RadioItems(
                                            id="filter_answer_gender_radio",
                                            options=[
                                                {'label': 'Answer', 'value': 'Answer'},
                                                {'label': 'Gender', 'value': 'Gender'},
                                            ],
                                            value='Answer',
                                            persistence=True,
                                            labelStyle={'display': 'flex'}
                                        ),
                                    ]
                                ),
                                html.Div(
                                    children=[
                                        html.Label("Select Result type:"),
                                        dcc.RadioItems(
                                            id="res_type",
                                            options=[
                                                {'label': 'Number', 'value': 'Number'},
                                                {'label': 'Percentage', 'value': 'Percentage'},
                                            ],
                                            value='Number',
                                            persistence=True,
                                            labelStyle={'display': 'flex'}
                                        ),
                                    ]
                                ),
                            ]
                        )
                    ]
                ),
                html.Div(
                    className="right_div",
                    children=[
                        html.Div(
                            children=[
                                html.H4("Number of chosen Answers of Regions and Countries"),
                                html.Div(
                                    className="radio_filter_div",
                                    children=[
                                        dcc.RadioItems(
                                            id="country_region_radio",
                                            options=[
                                                {'label': 'Region', 'value': 'Region'},
                                                {'label': 'Country', 'value': 'Subregion'},
                                            ],
                                            value='Region',
                                            persistence=True,
                                            labelStyle={'display': 'flex'}
                                        ),
                                        html.Div(
                                            id="regions_filter_div",
                                            children=[
                                                html.Label("Filter countries by region:"),
                                                dcc.Dropdown(
                                                    id="regions_filter_dropdown",
                                                    options = [{'label': v, 'value': v } for v in df["Region"].unique()],
                                                    placeholder="Select regions to filter by...",
                                                    multi=True,
                                                    persistence=True
                                                ),
                                            ]
                                        ),
                                        html.Div(
                                            id="graph_type_div",
                                            children=[
                                                html.Label("Select Graph type:"),
                                                dcc.Dropdown(
                                                    id="graph_type2",
                                                    options=[
                                                        {'label': 'Bar Plot', 'value': 'Bar Plot'},
                                                        {'label': 'Box Plot', 'value': 'Box Plot'},
                                                    ],
                                                    value="Bar Plot",
                                                    clearable=False,
                                                    persistence=True
                                                ),
                                            ]
                                        ),
                                    ]
                                ),
                                dcc.Graph(id='countries_regions_graph'),
                            ]
                        ),
                        html.Div([
                            html.H4("Compare Answers across different Countries"),
                            html.Div(
                                className="countries_dropdowns",
                                children=[
                                    html.Div(
                                        [
                                            html.Label("Select Countries to compare:"),
                                            dcc.Dropdown(
                                                id="countries_dropdown",
                                                options = [{'label': v, 'value': v } for v in df["Subregion"].unique()],
                                                value=[df["Subregion"].unique()[0], df["Subregion"].unique()[1]],
                                                multi=True,
                                                persistence=True
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.Label("Select Graph type:"),
                                            dcc.Dropdown(
                                                id="graph_type",
                                                options=[
                                                    {'label': 'Bar Plot', 'value': 'Bar Plot'},
                                                    {'label': 'Sunburst Plot', 'value': 'Sunburst Plot'},
                                                ],
                                                value="Bar Plot",
                                                persistence=True
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                            dcc.Graph(id='compare_countries_graph'),
                        ]),
                        html.Div(
                            id="years_div",
                            children=[
                                html.H4("Evolution of Answers over the Years"),
                                html.Label("Select Country:"),
                                dcc.Dropdown(
                                    id="country_dropdown",
                                    options = [{'label': v, 'value': v } for v in df["Subregion"].unique()],
                                    value=df["Subregion"].unique()[0],
                                    persistence=True
                                ),
                                dcc.Graph(id='years_countries_graph'),
                            ]
                        ),
                        html.Div([
                            html.H4("Distibution of the number of the chosen Answer over the World"),
                            html.Div(
                                className="map_radios_div", 
                                children=[
                                    html.Div(
                                        children=[
                                            html.Label("Group countries by:"),
                                            dcc.RadioItems(
                                                id="group_by_radio",
                                                options=[
                                                    {'label': 'Number of Answers', 'value': 'Answer'},
                                                    {'label': 'Region', 'value': 'Region'},
                                                ],
                                                value='Answer',
                                                persistence=True,
                                                labelStyle={'display': 'flex'}
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        children=[
                                            html.Label("Map Graph type:"),
                                            dcc.RadioItems(
                                                id="map_res_type_radio",
                                                options=[
                                                    {'label': 'Scatter Map', 'value': 'Scatter Map'},
                                                    {'label': 'Choropleth Map', 'value': 'Choropleth Map'},
                                                ],
                                                value='Scatter Map',
                                                persistence=True,
                                                labelStyle={'display': 'flex'}
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                            dcc.Graph(id='map_graph'),
                        ]),
                        html.Div([
                            html.H4(f"Modalities that tend to appear together ({len(ap)} Modalities found!)"),
                            html.Div(
                                className="apriori_select_div",
                                children=[
                                    html.Div([
                                        html.Label("Choose a modality to view:"),
                                        dcc.Dropdown(
                                            id="modalities",
                                            options=[
                                                {"label": f"#{i+1} ({row[0]}) and ({row[1]})", "value": i} for i, row in enumerate(ap.values)
                                            ],
                                            value=0,
                                            persistence=True,
                                            clearable=False,
                                        ),
                                    ]),
                                    html.Div([
                                        html.Label("Group by:"),
                                        dcc.Checklist(
                                            id="apriori_group_by",
                                            options=[
                                                {"label": "Gender", "value": "Gender"},
                                                {"label": "Year", "value": "Year"},
                                                {"label": "Region", "value": "Region"},
                                            ],
                                            value=[],
                                            persistence=True,
                                            labelStyle={'display': 'flex'}
                                        ),
                                    ]),
                                ]
                            ),
                            dash_table.DataTable(
                                id='apriori_table',
                                style_data={
                                    'whiteSpace': 'normal',
                                    'height': 'auto',
                                },
                                style_cell={
                                    'textAlign': 'center',
                                    'padding': '5px'
                                },
                                style_header={
                                    'fontWeight': 'bold'
                                },
                                style_cell_conditional=[
                                    {
                                        'if': {'column_id': 'Question'},
                                        'textAlign': 'left'
                                    }
                                ]
                            ),
                            dcc.Graph(id='apriori_graph'),
                        ]),
                    ]
                ),
            ]
        ),
    ]
)

def get_qst_from_answer(answer_value):
    for row in codebook.values:
        if row[0] == answer_value:
            return row[2]

def get_answer_label_from_value(answer_value):
    for row in codebook.values:
        if row[0] == answer_value:
            return row[4]

def get_answer_labels_and_values(answers):
    answer_labels, answer_values = [], []
    for a in answers:
        answer_values.append(a["value"])
        answer_labels.append(a["label"])
    return answer_labels, answer_values

@app.callback([Output('question_dropdown', 'options'),
               Output('question_dropdown', 'value')],
               Input('theme_dropdown', 'value'))
def qsts_dropdown_update(theme):
    qsts = []
    for row in codebook.values:
        if row[1] == theme.lower() and not row[2] in qsts:
            qsts.append(row[2])
    return [{'label': q, 'value': q} for q in qsts], qsts[0]

@app.callback([Output('answer_dropdown', 'options'),
               Output('answer_dropdown', 'value')],
               Input('question_dropdown', 'value'))
def resp_dropdown_update(question):
    resps_labels, resps_values = [], []
    for row in codebook.values:
        if row[2] == question:
            resps_values.append(row[0])
            resps_labels.append(row[4])
    return [{'label': r1, 'value': r2} for r1, r2 in zip(resps_labels, resps_values)], resps_values[0]

@app.callback([Output('year_dropdown', 'options'),
               Output('year_dropdown', 'value')],
               Input('answer_dropdown', 'value'))
def years_dropdown_update(answer):
    years = []
    for year in df["Year"].unique():
        if not df[df.Year == year][answer].isnull().all():
            years.append(year)
    years = sorted(years)
    return [{'label': y, 'value': y} for y in years], years[len(years)-1]

@app.callback([Output('regions_filter_div', 'style'),
               Output('graph_type_div', 'style')],
               Input('country_region_radio', 'value'))
def regions_dropdown_update(country_or_region):
    if country_or_region == "Region":
        return {'display': 'none'}, None
    elif country_or_region == "Subregion":
        return None, {'display': 'none'}

@app.callback(Output('countries_regions_graph', 'figure'),
              [Input('answer_dropdown', 'value'),
               Input('answer_dropdown', 'options'),
               Input('year_dropdown', 'value'),
               Input('country_region_radio', 'value'),
               Input('filter_answer_gender_radio', 'value'),
               Input('res_type', 'value'),
               Input('regions_filter_dropdown', 'value'),
               Input('graph_type2', 'value')])
def countries_regions_graph_update(answer, answers, year, country_or_region, answer_or_gender, res_type, regions_filter, graph_type):
    answer_label = get_answer_label_from_value(answer)
    answer_labels, answer_values = get_answer_labels_and_values(answers)

    if regions_filter is not None and regions_filter and country_or_region == "Subregion":
        dd = df.loc[df['Region'].isin(regions_filter)]
    else: 
        dd = df

    dd = dd[dd.Year == year]
    dd = dd[["Region"] + ["Subregion"] + ["Gender"] + answer_values]
    dd = dd.rename(columns={x: y for x, y in zip(answer_values, answer_labels)})

    if answer_or_gender == "Answer":
        dd = dd.melt(id_vars=['Region', 'Subregion', 'Gender'], var_name="Answer", value_name="Count")
        y="Count"
        color="Answer"
    elif answer_or_gender == "Gender":
        y=answer_label
        color="Gender"

    if graph_type == "Box Plot" and country_or_region == "Region":
        fig = px.box(
            data_frame=dd,
            x=country_or_region, 
            y=y,
            color=color,
            labels={
                answer: f'people who selected "{answer_label}"',
                "Subregion": "Country",
            },
            category_orders={"Gender": ["Male", "Female"]},
            color_discrete_sequence=skyblue_color_palette,
        )
        fig.update_layout(yaxis={'title': 'Number of answers',}, xaxis_title=None, margin=dict(t=35))

    else:
        fig = px.histogram(
            data_frame=dd,
            x=country_or_region, 
            y=y,
            color=color,
            labels={
                answer: f'people who selected "{answer_label}"',
                "Subregion": "Country",
            },
            category_orders={"Gender": ["Male", "Female"]},
            color_discrete_sequence=skyblue_color_palette,
        )
        fig.update_layout(yaxis={'title': 'Number of answers',}, xaxis_title=None, margin=dict(t=35, l=0))
        if res_type == "Percentage":
            fig.update_layout(barnorm="percent")

    return fig

@app.callback(Output('compare_countries_graph', 'figure'),
              [Input('countries_dropdown', 'value'),
               Input('answer_dropdown', 'options'),
               Input('answer_dropdown', 'value'),
               Input('year_dropdown', 'value'),
               Input('res_type', 'value'),
               Input('filter_answer_gender_radio', 'value'),
               Input('graph_type', 'value')])
def compare_countries_graph_update(countries_dropdown, answers, answer, year, res_type, answer_or_gender, graph_type):
    answer_label = get_answer_label_from_value(answer)
    answer_labels, answer_values = get_answer_labels_and_values(answers)

    dd = df.loc[df['Subregion'].isin(countries_dropdown)]
    dd = dd[dd.Year == year]
    dd = dd[["Subregion"] + ["Gender"] + answer_values]
    dd = dd.rename(columns={x: y for x, y in zip(answer_values, answer_labels)})

    if graph_type == "Bar Plot":
        if answer_or_gender == "Answer":
            dd = dd.melt(id_vars=['Subregion', 'Gender'], var_name="Answer", value_name="Count")
            y="Count"
            color="Answer"
        elif answer_or_gender == "Gender":
            y=answer_label
            color="Gender"

        fig = px.histogram(
            data_frame=dd,
            x="Subregion",
            y=y,
            color=color,
            labels={
                "variable": "Answer",
                "value": "answers",
                "Subregion": "Country",
            },
            category_orders={
                "Subregion": countries_dropdown,
                "Gender": ["Male", "Female"]
            },
            color_discrete_sequence=skyblue_color_palette,
            height=500
        )
        fig.update_layout(yaxis={'title' : 'Number of answers'}, xaxis_title=None)
        if res_type == "Percentage":
            fig.update_layout(barnorm="percent")

    elif graph_type == "Sunburst Plot":
        dd = dd.melt(id_vars=['Subregion', 'Gender'], var_name="Answer", value_name="Count")
        fig = px.sunburst(
            data_frame=dd, 
            path=['Subregion', 'Gender', 'Answer'], 
            values='Count',
            color_discrete_sequence=skyblue_color_palette,
            height=600
        )

    fig.update_layout(margin=dict(t=35))
    return fig

@app.callback([Output('years_countries_graph', 'figure'),
               Output('years_div', 'style')],
              [Input('country_dropdown', 'value'),
               Input('year_dropdown', 'options'),
               Input('answer_dropdown', 'options')])
def years_countries_graph_update(country_dropdown, years, answers):
    answer_labels, answer_values = get_answer_labels_and_values(answers)

    dd = df[df.Subregion == country_dropdown]
    dd = dd.groupby(['Year']).agg({a: sum for a in answer_values}).reset_index()
    dd = dd[["Year"] + answer_values]
    dd = dd.rename(columns={x: y for x, y in zip(answer_values, answer_labels)})

    fig = px.line(
        data_frame=dd,
        x="Year",
        y=answer_labels,
        labels={
            "variable": "Answer",
            "Subregion": "Country",
        },
        color_discrete_sequence=skyblue_color_palette,
        markers=True
    )

    fig.update_layout(xaxis={'dtick': 1}, yaxis={'title' : 'Number of answers'}, margin=dict(t=35))
    fig.update_traces(mode="markers+lines")
    fig.update_yaxes(showspikes=True)

    if len(years) <= 1: style = {'display': 'none'}
    else: style = None

    return fig, style

@app.callback(Output('map_graph', 'figure'),
              [Input('answer_dropdown', 'value'),
               Input("year_dropdown", "value"),
               Input("group_by_radio", "value"),
               Input("map_res_type_radio", "value")])
def map_graph_update(answer, year, group_by, map_res_type):
    mapdf = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2014_world_gdp_with_codes.csv')

    for index in mapdf.index:
        if mapdf.loc[index, 'COUNTRY'] == "United States":
            mapdf.loc[index, 'COUNTRY'] = "United States of America"
    
    mapdf = mapdf[["COUNTRY"] + ["CODE"]]
    mapdf = mapdf.drop_duplicates()
    mapdf = mapdf.rename(columns={'COUNTRY': 'Subregion'})
    mapdf = pd.merge(df[df.Year == year], mapdf)
    mapdf = mapdf[["Region"] + ["Subregion"] + ["CODE"] + [answer]]
    mapdf = mapdf.dropna()
    mapdf = mapdf.groupby(['CODE', 'Subregion', 'Region']).agg({answer: sum}).reset_index()

    color = answer if group_by == "Answer" else "Region"

    if map_res_type == "Scatter Map":
        fig = px.scatter_geo(
            data_frame=mapdf,
            locations="CODE",
            hover_name="Subregion",
            color=color,
            size=answer,
            color_continuous_scale=darkblue_color_palette[::-1],
            labels={answer: "N# of chosen answer"},
            hover_data={'Region': True, 'CODE': False},
        )
    elif map_res_type == "Choropleth Map":
        fig = px.choropleth(
            data_frame=mapdf,
            locations="CODE",
            hover_name="Subregion",
            color=color,
            color_continuous_scale=darkblue_color_palette[::-1],
            labels={answer: "N# of chosen answer"},
            hover_data={'Region': True, 'CODE': False},
        )

    fig.update_layout(margin=dict(t=30, b=30, l=0, r=0))
    return fig

@app.callback([Output('apriori_table', 'columns'),
               Output('apriori_table', 'data')],
               Input('modalities', 'value'))
def apriori_table_update(modality_index):
    i = modality_index
    columns = [
        {"name": "Axis", "id": "Axis"},
        {"name": "Question", "id": "Question"},
        {"name": "Answer", "id": "Answer"},
        {"name": "Support", "id": "Support"},
        {"name": "Confidence", "id": "Confidence"},
        {"name": "Lift", "id": "Lift"},
    ]
    data = [
        {"Axis": "x", "Question": get_qst_from_answer(ap.values[i][0]), "Answer": get_answer_label_from_value(ap.values[i][0]), "Support": ap.values[i][4], "Confidence": ap.values[i][5], "Lift": ap.values[i][6]},
        {"Axis": "y", "Question": get_qst_from_answer(ap.values[i][1]), "Answer": get_answer_label_from_value(ap.values[i][1]), "Support": ap.values[i][4], "Confidence": ap.values[i][5], "Lift": ap.values[i][6]},
    ]
    
    return columns, data

@app.callback(Output('apriori_graph', 'figure'),
             [Input('apriori_group_by', "value"),
              Input('modalities', 'value')])
def apriori_graph_update(group_by_values, modality_index):
    i = modality_index
    fig = px.scatter(
        data_frame=df,
        x=ap.values[i][0],
        y=ap.values[i][1],
        labels={
            ap.values[i][0]: "x",
            ap.values[i][1]: "y",
        },
        facet_col="Year" if "Year" in group_by_values else None,
        facet_row="Gender" if "Gender" in group_by_values else None,
        color="Region" if "Region" in group_by_values else None,
        trendline="ols",
        hover_data=["Subregion"],
    )
    fig.update_layout(margin=dict(t=30, b=30, l=0, r=0))
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)