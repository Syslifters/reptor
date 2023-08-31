import typing

from reptor.lib.plugins.ModelBase import ModelBase


class Instance(ModelBase):
    uri: str
    method: str
    param: str
    attack: str
    evidence: str
    otherinfo: str
    requestheader: str
    requestbody: str
    responseheader: str
    # responsebody: str # Careful with this!

    def parse(self, data):
        self.uri = data.find("uri").text
        self.method = data.find("method").text
        self.param = data.find("param").text
        self.attack = data.find("attack").text
        self.evidence = data.find("evidence").text
        self.otherinfo = data.find("otherinfo").text
        if data.find("requestheader"):
            self.requestheader = data.find("requestheader").text
        if data.find("requestbody"):
            self.requestbody = data.find("requestbody").text
        if data.find("responseheader"):
            self.responseheader = data.find("responseheader").text


class Alert(ModelBase):
    pluginid: str
    alertRef: str
    name: str
    riskcode: int
    confidence: int
    riskdesc: str
    confidencedesc: str
    desc: str
    count: int
    solution: str
    otherinfo: str
    reference: str
    cweid: int
    wascid: int
    sourceid: int

    instances: typing.List[Instance] = list()

    def parse(self, data):
        self.pluginid = data.find("pluginid").text
        self.alertRef = data.find("alertRef").text
        self.name = data.find("name").text
        self.riskcode = data.find("riskcode").text
        self.confidence = data.find("confidence").text
        self.riskdesc = data.find("riskdesc").text
        self.confidencedesc = data.find("confidencedesc").text
        self.desc = data.find("desc").text
        self.count = data.find("count").text
        self.solution = data.find("solution").text
        self.reference = data.find("reference").text
        self.cweid = data.find("cweid").text
        self.wascid = data.find("wascid").text
        self.sourceid = data.find("sourceid").text

    @property
    def references_as_list_items(self):
        return self.reference.splitlines()


class Site(ModelBase):
    name: str
    host: str
    port: str
    ssl: bool

    alerts: typing.List[Alert] = list()

    def parse(self, data):
        self.name = data.get("name")
        self.host = data.get("host")
        self.port = data.get("port")
        self.ssl = data.get("ssl")
