from dataset import RegionsDataset, MembersDatasetExtended
from dash import Dash
from callbacks import register_callbacks
from layout import get_layout


def main() -> None:
    df = MembersDatasetExtended().read_preprocessed()

    geo_json = RegionsDataset().read_preprocessed()

    app = Dash(__name__)

    ageGroups = ["0To15", "15To26", "From26"]
    app.layout = get_layout(df["Location"].unique(), ageGroups)

    register_callbacks(app, df, geo_json, ageGroups)

    app.run_server()


if __name__ == "__main__":
    main()
