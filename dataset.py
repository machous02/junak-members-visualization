from urllib.request import urlretrieve
from pathlib import Path
import pandas as pd
from abc import ABC, abstractmethod
from unidecode import unidecode
import json


DATA_DIR = Path("data")

type JsonType = None | int | str | bool | list[JsonType] | dict[str, JsonType]


class Dataset[T](ABC):
    url: str

    @property
    def path(self) -> Path:
        return DATA_DIR / self.url.split("/")[-1]

    def _download(self) -> None:
        urlretrieve(self.url, filename=self.path)

    @abstractmethod
    def _load(self) -> T:
        pass

    def read(self) -> T:
        if not self.path.exists():
            self._download()

        return self._load()

    @abstractmethod
    def preprocess(self, ds: T) -> T:
        pass

    def read_preprocessed(self) -> T:
        return self.preprocess(self.read())


class MembersDataset(Dataset[pd.DataFrame]):
    url = "https://opendata.skaut.cz/data/opendata/V1_clenove_okres_kraj.csv"

    def _load(self) -> pd.DataFrame:
        return pd.read_csv(self.path, sep=";")

    def preprocess(self, ds: pd.DataFrame) -> pd.DataFrame:
        ds.loc[ds["UnitName"] == "Ústecký kraj", "Location"] = "Ústecký kraj"
        ds = ds[ds["ID_UnitType"].isin(["kraj", "ustredi"])]

        ds["Location"] = ds["Location"].map(
            lambda s: unidecode(s.casefold()) if isinstance(s, str) else s
        )
        ds["RegularMembers0To15"] = ds["RegularMembersTo6"] + ds["RegularMembersTo15"]
        ds["RegularMembers15To26"] = ds["RegularMembersTo18"] + ds["RegularMembersTo26"]

        return ds


class RegionsDataset(Dataset[JsonType]):
    url = "https://simplemaps.com/static/svg/country/cz/admin1/cz.json"

    def _load(self) -> JsonType:
        with open(self.path, "r") as f:
            return json.load(f)

    def preprocess(self, ds: JsonType) -> JsonType:
        for feature in ds["features"]:
            feature["properties"]["name"] = unidecode(
                feature["properties"]["name"].strip().casefold()
            )

            if feature["properties"]["name"] == "praha":
                feature["properties"]["name"] = "hlavni mesto praha"

        return ds


class PopulationDataset(Dataset[pd.DataFrame]):
    url = "data/UD-1735819179198.xlsx"

    def _load(self) -> pd.DataFrame:
        return pd.read_excel(
            "data/UD-1735819179198.xlsx",
            engine="openpyxl",
            header=5,
            names=["region", "date", "population"],
            usecols="B:D",
        )

    def preprocess(self, ds: pd.DataFrame) -> pd.DataFrame:
        ds["region"] = ds["region"].ffill()
        ds.dropna(inplace=True)
        ds = ds[ds["date"].str.contains("leden")]
        ds["year"] = ds["date"].str.split().str[-1]
        ds.drop("date", inplace=True, axis="columns")
        ds.reset_index(inplace=True, drop=True)
        ds["region"] = ds["region"].map(lambda s: unidecode(s.casefold()))
        ds = ds.astype({"region": "category", "year": "uint32", "population": "uint64"})
        xx = ds.groupby("year").sum(numeric_only=True).reset_index()
        xx["region"] = "ceska republika"

        ds = pd.concat((ds, xx))
        ds.rename(
            {"region": "Location", "year": "Year", "population": "Population"},
            axis="columns",
            inplace=True,
        )
        return ds


class MembersDatasetExtended(Dataset[pd.DataFrame]):
    url = "https://opendata.skaut.cz/data/opendata/V1_clenove_okres_kraj.csv"

    def _load(self) -> pd.DataFrame:
        members_ds = MembersDataset().read_preprocessed()
        pop_ds = PopulationDataset().read_preprocessed()
        return pd.merge(members_ds, pop_ds, how="left", on=["Location", "Year"])

    def preprocess(self, ds: pd.DataFrame) -> pd.DataFrame:
        member_cols = [
            "RegularMembers",
            "RegularMembers0To15",
            "RegularMembers15To26",
            "RegularMembersFrom26",
        ]

        for s in member_cols:
            ds[s + "Percent"] = 100 * ds[s] / ds["Population"]

        return ds
