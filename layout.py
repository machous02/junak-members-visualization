from dash import html, dcc

info = """
This visualization presents the number of regular members of Junák – český skaut, z. s.
across different years and regions of Czechia.
Users can compare data regionally and observe trends over time.
Additionally, a relative mode highlights the percentage of each region's population who are members.
Filters are available to focus on three main age categories: 0–15, 15–26, and 26+.
"""


def get_layout(regions: list[str], ageGroups: list[str]) -> html.Div:
    return html.Div(
        style={
            "backgroundColor": "#F6EBD8",
            "height": "100%",
            "color": "#657F6F",
            "margin": 0,
            "padding": "15px",
        },
        children=[
            html.H1(
                children="Members of Junák",
                style={
                    "marginTop": "0px",
                    "marginBottom": "0px",
                },
            ),
            info,
            html.P(id="here"),
            html.Hr(),
            html.Div(
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "stretch",
                    "margin-bottom": "15px",
                },
                children=[
                    html.Div(
                        children=[
                            html.H2(
                                "Controls",
                                style={"margin-top": "5px", "margin-bottom": "5px"},
                            ),
                            html.B("Selected region: "),
                            dcc.Dropdown(
                                regions,
                                "ceska republika",
                                id="selected-region",
                                clearable=False,
                                optionHeight=50,
                                style={"width": "110%"},
                            ),
                            html.Div(
                                style={
                                    "display": "flex",
                                    "justifyContent": "space-between",
                                    "alignItems": "stretch",
                                    "margin-bottom": "15px",
                                },
                                children=[
                                    html.Div(
                                        children=[
                                            html.B("Layout: "),
                                            dcc.RadioItems(
                                                ["Absolute", "Relative"],
                                                "Absolute",
                                                id="mode",
                                                labelStyle={
                                                    "margin-top": "3px",
                                                    "margin-bottom": "5px",
                                                },
                                            ),
                                            html.B("Age group: "),
                                            dcc.Checklist(
                                                ageGroups,
                                                ageGroups,
                                                id="age",
                                                labelStyle={
                                                    "margin-top": "3px",
                                                    "margin-bottom": "5px",
                                                },
                                            ),
                                        ],
                                        style={
                                            "width": "60%",
                                            "display": "inline-block",
                                        },
                                    ),
                                    html.Div(
                                        children=[
                                            dcc.Slider(
                                                2003,
                                                2024,
                                                step=1,
                                                value=2024,
                                                id="slider",
                                                marks={
                                                    i: "{}".format(i)
                                                    for i in range(2003, 2024, 5)
                                                },
                                                tooltip={
                                                    "placement": "left",
                                                    "always_visible": True,
                                                },
                                                vertical=True,
                                                verticalHeight=300,
                                            ),
                                        ],
                                        style={
                                            "width": "30%",
                                            "display": "inline-block",
                                        },
                                    ),
                                ],
                            ),
                        ],
                        style={
                            "width": "10%",
                        },
                    ),
                    html.Div(
                        children=[
                            html.H2(
                                "Distribution among regions",
                                style={
                                    "textAlign": "center",
                                    "color": "#657F6F",
                                    "margin-top": "5px",
                                    "margin-bottom": "5px",
                                },
                            ),
                            dcc.Graph(id="map"),
                        ],
                        style={"width": "40%", "display": "inline-block"},
                    ),
                    html.Div(
                        children=[
                            html.H2(
                                "Timeline",
                                style={
                                    "textAlign": "center",
                                    "color": "#657F6F",
                                    "margin-top": "5px",
                                    "margin-bottom": "5px",
                                },
                            ),
                            dcc.Graph(id="timeline"),
                        ],
                        style={"width": "40%", "display": "inline-block"},
                    ),
                ],
            ),
            html.Div(children=[], id="table_container"),
        ],
    )
