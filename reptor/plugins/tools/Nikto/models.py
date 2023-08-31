import datetime
import typing

from reptor.lib.plugins.ModelBase import ModelBase


class Item(ModelBase):
    method: str = "GET"
    description: str
    uri: str
    namelink: str
    iplink: str
    references: str

    endpoint: str = "/"

    def parse(self, data):
        description = data.find("description").text
        self.description = description
        if ": " in description:
            description_data = description.split(":")
            self.endpoint = description_data[0]
            self.description = description_data[1]

        self.uri = data.find("uri").text
        self.namelink = data.find("namelink").text
        self.iplink = data.find("iplink").text
        self.references = data.find("references").text
        self.method = data.get("method")


class ScanDetails(ModelBase):
    targetip: str
    targethostname: str
    targetport: str
    targetbanner: str
    sitename: str
    siteip: str
    hostheader: str
    errors: str
    checks: str

    items: typing.List[Item] = list()

    def parse(self, data):
        self.targethostname = data.get("targethostname")
        self.targetport = data.get("targetport")
        self.targetbanner = data.get("targetbanner")
        self.sitename = data.get("sitename")
        self.hostheader = data.get("hostheader")
        self.siteip = data.get("siteip")
        self.targetip = data.get("targetip")
        self.starttime = data.get("starttime")
        self.errors = data.get("errors")

    def append_item(self, item: Item):
        if not self.items:
            self.items = list()

        self.items.append(item)

    def set_items(self, items: typing.List[Item]):
        self.items = items


class Statistics(ModelBase):
    elapsed: int
    errors: int
    checks: int
    itemsfound: int
    itemstested: int
    starttime: datetime.datetime
    endtime: datetime.datetime

    def parse(self, data):
        self.elapsed = data.get("elapsed")
        self.itemsfound = data.get("itemsfound")
        self.endtime = data.get("endtime")
        self.itemstested = data.get("itemstested")
        self.checks = data.get("checks")
        self.errors = data.get("errors")


class NiktoScan(ModelBase):
    options: str
    version: str
    scandetails: ScanDetails
    statistics: Statistics

    def parse(self, data):
        self.options = data.get("options")
        self.version = data.get("version")
