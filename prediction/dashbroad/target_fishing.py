import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from django_plotly_dash import DjangoDash
import os
from deep_engine_client.settings.base import BASE_DIR

df = pd.read_csv(os.path.join(BASE_DIR, "prediction", "db", "LBVS_performance_table.csv"))

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


avaliable_diseases = df['disease_class_name'].unique()
avaliable_protein_class = df['protein_class_name'].unique()
# avaliable_score_type = ['maximum', 'minimum', 'average', 'ratio']

app = DjangoDash("target_fishing")

app.layout = html.Div(children=[
    html.H2("Results:"),
    html.Label("Disease category:"),
    dcc.Dropdown(
        id='disease-dropdown',
        options=[{"label": x, "value": x} for x in avaliable_diseases],
        placeholder="select disease",
        value="Behavior and Behavior Mechanisms"
    ),
    html.Label("Protein class:"),
    dcc.Dropdown(
        id='protein-type-checklist',
        options=[{"label": x, "value": x} for x in avaliable_protein_class],
        value=['Kinase', 'Enzyme'],
        multi=True
    ),
    # html.Label("DisGeNET association score type:"),
    # dcc.RadioItems(
    #     id='score-type-dropdown',
    #     options=[{"label": x, "value": x} for x in avaliable_score_type],
    #     value="average"
    # ),

    dcc.Graph(id='auroc-with-dropdown'),
    dcc.Graph(id='auroc-boxplot'),
    html.H2("About DisGeNET associoation score"),
    html.P("The DisGeNET score for GDAs takes into account the number and type of sources and the number of publications supporting the association, while the score for the VDAs takes into account sources, and number of papers. The scores range from 0 to 1."),
    dcc.Markdown("For more information, please check out official [document](https://www.disgenet.org/dbinfo#score).")
]
)


@app.callback(
    Output('auroc-with-dropdown', 'figure'),
    [Input('disease-dropdown', 'value'),
     Input('protein-type-checklist', 'value'),
     #Input('score-type-dropdown', 'value')
     ])
def update_figure(selected_disease, protein_class):
#def update_figure(selected_disease, protein_class, selected_type):

    filtered_df = df[(df.disease_class_name == selected_disease) & (df.type == "maximum") & (df['protein_class_name'].isin(protein_class))]
    # print(filtered_df['protein_class_name'].unique())
    fig = px.scatter(filtered_df,
                     x="score", y="AUROC", size="sample_size",
                     color='protein_class_name', hover_name="gene_symbol",
                     labels={"score": "DisGeNET association score",
                             "AUROC": "AuROC",
                             "protein_class_name": "Protein class"}
                     )
    fig.update_layout(transition_duration=500, font_size=14)
    return fig


@app.callback(
    Output('auroc-boxplot', 'figure'),
    [Input('disease-dropdown', 'value'),
     Input('protein-type-checklist', 'value')])
def update_boxplot(selected_disease, protein_class):
    subset_df = df[(df.disease_class_name == selected_disease) & (df['protein_class_name'].isin(protein_class))][['AUROC', 'gene_symbol', 'protein_class_name']].drop_duplicates()
    # print(subset_df)
    fig = px.violin(subset_df, y="AUROC", x="protein_class_name",
                    box=True, hover_data=subset_df.columns, points="all",
                    labels={
                        "AUROC": "AuROC",
                        "protein_class_name": "Protein class"}
                    )
    fig.update_layout(font_size=14)
    return fig
