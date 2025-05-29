import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, State, dash_table
from plotly.graph_objects import Figure

from dataset import JsonType


def register_callbacks(
    app: Dash, df: pd.DataFrame, geo_json: JsonType, ageGroups: list[str]
) -> None:
    maximums = {
        col: pd.to_numeric(
            df[df["Location"] != "ceska republika"][col], errors="coerce"
        ).max()
        for col in df.columns
    }
    opts = ageGroups

    def get_map(modeValue: str, ageGroups: list[str], sliderYear: int) -> Figure:
        df_year = df[df["Year"] == sliderYear]

        columns = list(
            map(
                lambda s: "RegularMembers" + s + (modeValue == "Relative") * "Percent",
                ageGroups,
            )
        )

        range_color = (0, sum(map(lambda c: maximums[c], columns)))

        fig = px.choropleth(
            df_year,
            geojson=geo_json,
            featureidkey="properties.name",
            locations="Location",
            color=df_year[columns].sum(axis="columns"),
            color_continuous_scale=px.colors.sequential.Oranges,
            projection="miller",
            fitbounds="locations",
            range_color=range_color,
        )

        fig.update_geos(visible=False, bgcolor="rgba(0,0,0,0)")
        fig.update_layout(margin={"r": 0, "l": 0, "t": 0, "b": 0})
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#657F6F",
        )

        digits = 3 if modeValue == "Relative" else 0

        fig.update_traces(
            hovertemplate="%{location}"
            + "<br>"
            + "<br>".join(
                map(
                    lambda c: c[1][14:]
                    + ": %{customdata["
                    + str(c[0])
                    + "]:."
                    + str(digits)
                    + "f}",
                    enumerate(columns),
                )
            )
            + "<br>"
            + "sum: %{z:."
            + str(digits)
            + "f}",
            hoverlabel=dict(
                bgcolor="#ECDCAF",
                align="left",
            ),
        )
        fig.update_traces(customdata=df_year[columns].values)

        fig.update_layout(
            coloraxis_colorbar=dict(
                orientation="h",
                y=-0.25,
                len=0.9,
            ),
        )

        return fig

    def get_timeline(region: str, hide: list[str] = []) -> Figure:
        df_region = df[df["Location"] == region]

        bars = px.bar(
            df_region,
            x="Year",
            y=["RegularMembers0To15", "RegularMembers15To26", "RegularMembersFrom26"],
            color_discrete_sequence=["#b2df8a", "#a6cee3", "#1f78b4"],
            barmode="stack",
        )

        bars.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#657F6F",
        )

        bars.update_layout(
            legend=dict(
                title="Age group",
                orientation="h",
                y=-0.25,
            ),
            yaxis=dict(title=dict(text="Number of members")),
        )

        for name in hide:
            bars.update_traces(
                selector=dict(name=name),
                visible="legendonly",
            )

        return bars

    def get_table(region: str, ageCategories: list[str]) -> dash_table.DataTable:
        table_df = df[df["Location"] == region]
        table_df = table_df[["Location", "Year"] + ageCategories]
        table_df["SumMembers"] = table_df[ageCategories].sum(axis="columns")
        table_df = table_df.pivot(
            index="Location", columns="Year", values="SumMembers"
        ).reset_index()

        return dash_table.DataTable(
            table_df.to_dict("records"),
            id="table",
            columns=[{"name": str(i), "id": str(i)} for i in table_df.columns],
            style_header={"backgroundColor": "#D3BFA0", "fontWeight": "bold"},
            style_cell={"backgroundColor": "#ECDCAF"},
            cell_selectable=False,
        )

    # buttons / yearSlider -> map
    @app.callback(
        Output("map", "figure"),
        Input("mode", "value"),
        Input("age", "value"),
        Input("slider", "value"),
    )
    def update_map(modeValue: str, ageGroups: list[str], sliderYear: str) -> Figure:
        return get_map(modeValue, ageGroups, sliderYear)

    # ageGroup / regionDropdown -> timeline (barchart)
    @app.callback(
        Output("timeline", "figure"),
        Input("selected-region", "value"),
        Input("age", "value"),
    )
    def update_timeline(region: str | None, ageGroups: list[str]) -> Figure:
        if region is None:
            region = "ceska republika"

        fig = get_timeline(
            region, ["RegularMembers" + opt for opt in opts if opt not in ageGroups]
        )
        return fig

    # timeline (barchart) -> yearSlider
    @app.callback(
        Output("slider", "value"),
        Input("timeline", "clickData"),
    )
    def update_year(clickData: JsonType) -> int:
        year = 2024
        if clickData is not None:
            year = clickData["points"][0]["x"]

        return year

    # timeline (barchart) + ageGroups -> ageGroups
    # (update checkboxes based on hidden legend labels)
    @app.callback(
        Output("age", "value"), Input("timeline", "restyleData"), State("age", "value")
    )
    def update_age_options(restyle_data: JsonType, ageGroups: list[str]) -> list[str]:
        if restyle_data is None:
            return opts

        visibility_changes = restyle_data[0]
        affected_traces: list = restyle_data[1]

        change = {
            opts[s]: not isinstance(v, str)
            for s, v in zip(affected_traces, visibility_changes["visible"])
        }
        for opt in opts:
            if opt not in change:
                change[opt] = opt in ageGroups

        return [key for key, value in change.items() if value]

    # map -> regionDropdown
    @app.callback(
        Output("selected-region", "value"),
        Input("map", "clickData"),
    )
    def update_data(clickData: JsonType) -> str:
        if clickData is None:
            return "ceska republika"

        return clickData["points"][0]["location"]

    # ageGroups / regionDropdown -> table
    @app.callback(
        Output("table_container", "children"),
        Input("selected-region", "value"),
        Input("age", "value"),
    )
    def update_table(
        region: str | None, ageCategories: list[str]
    ) -> dash_table.DataTable:
        if region == None:
            region = "ceska republika"

        return get_table(region, ["RegularMembers" + opt for opt in ageCategories])
