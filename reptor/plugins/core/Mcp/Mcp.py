from reptor.lib.plugins.Base import Base
from reptor.plugins.core.Mcp.Server import MCPServer
from reptor.plugins.core.Mcp.Anonymizer import Anonymizer

class Mcp(Base):
    meta = {
        "name": "Mcp",
        "summary": "Starts the Model Context Protocol (MCP) server",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.anonymize = kwargs.get("anonymize", False)
        self.transport = kwargs.get("transport", "stdio")
        self.mcp_debug = kwargs.get("mcp_debug")

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath=plugin_filepath)
        parser.add_argument(
            "--anonymize",
            action="store_true",
            help="Anonymize affected components before sending to MCP client",
        )
        parser.add_argument(
            "--transport",
            default="stdio",
            choices=["stdio", "sse"],
            help="Transport mode for MCP server (default: stdio)",
        )
        parser.add_argument(
            "--mcp-debug",
            dest="mcp_debug",
            help="Path to log file for debugging MCP communication",
        )

    def _file_logger(self):
        """
        Creating file logger because MCP uses stdio and it would break MCP if we were not to use file logger
        """

        logger = None

        if self.mcp_debug:
            import logging
            logger = logging.getLogger("[MCP - Reptor]")
            logger.setLevel(logging.DEBUG)
            fh = logging.FileHandler(self.mcp_debug)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            fh.setFormatter(formatter)
            logger.addHandler(fh)
            logger.propagate = False

        return logger

    def run(self):
        self.info("Starting MCP Server...")
        if self.anonymize:
            self.info("Anonymization enabled.")
        
        try:
            logger = self._file_logger()
            anonymizer = Anonymizer() if self.anonymize else None
            server = MCPServer(reptor_instance=self.reptor, anonymizer=anonymizer, logger=logger)
            
            server.run(transport=self.transport)
        except ImportError as e:
            self.error(str(e))
        except Exception as e:
            self.error(f"Failed to start MCP server: {e}")

loader = Mcp
