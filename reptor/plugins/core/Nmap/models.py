from reptor.lib.plugins.ModelBase import ModelBase


class Service(ModelBase):
    ip: str
    port: int
    protocol: str
    service: str
    version: str

    def parse(self, data):
        self.ip = data.get("ip", "")
        self.hostname = data.get("hostname", "")
        self.port = data.get("port")
        self.protocol = data.get("protocol")
        self.service = data.get("service", "")
        self.version = data.get("version", "")
