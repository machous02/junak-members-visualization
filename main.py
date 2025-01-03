from dash import Dash

from callbacks import register_callbacks
from dataset import MembersDatasetExtended, RegionsDataset
from layout import get_layout

app = Dash(__name__)

df = MembersDatasetExtended().read_preprocessed()
geo_json = RegionsDataset().read_preprocessed()

ageGroups = ["0To15", "15To26", "From26"]

app.layout = get_layout(df["Location"].unique(), ageGroups)
register_callbacks(app, df, geo_json, ageGroups)

server = app.server

if __name__ == "__main__":
    app.run_server()
