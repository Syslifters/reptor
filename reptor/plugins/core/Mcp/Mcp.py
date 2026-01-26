from reptor.lib.plugins.Base import Base
from reptor.plugins.core.Mcp.Server import MCPServer
from reptor.plugins.core.Mcp.FieldExcluder import FieldExcluder


class Mcp(Base):
    meta = {
        "name": "Mcp",
        "summary": "Starts the Model Context Protocol (MCP) server",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.remove_fields = self._parse_remove_fields(kwargs.get("remove_fields"))
        self.transport = kwargs.get("transport", "stdio")
        self.mcp_debug = kwargs.get("mcp_debug")

    def _parse_remove_fields(self, fields_string):
        """Parse comma-separated field names into a list with validation."""
        if not fields_string:
            return []

        # Split by comma and strip whitespace
        fields = [f.strip() for f in fields_string.split(",")]

        # Validate that we have non-empty field names
        valid_fields = [f for f in fields if f]
        invalid_fields = [f for f in fields if not f]

        if invalid_fields:
            self.warning(f"Ignoring {len(invalid_fields)} empty field name(s)")

        return valid_fields

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath=plugin_filepath)
        parser.add_argument(
            "--remove-fields",
            dest="remove_fields",
            help="Comma-separated list of field names to remove from findings before sending to LLM (e.g., 'affected_components,internal_notes')",
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

            try:
                logger = logging.getLogger("[MCP - Reptor]")
                logger.setLevel(logging.DEBUG)
                fh = logging.FileHandler(self.mcp_debug)
                formatter = logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
                fh.setFormatter(formatter)
                logger.addHandler(fh)
                logger.propagate = False
            except Exception as e:
                self.error(f"Failed to initialize MCP debug logger at '{self.mcp_debug}': {e}")
                logger = None

        return logger

    def run(self):
        self.info("Starting MCP Server...")
        if self.remove_fields:
            self.info(f"Field exclusion enabled: {', '.join(self.remove_fields)}")

        try:
            logger = self._file_logger()
            field_excluder = (
                FieldExcluder(exclude_fields=self.remove_fields)
                if self.remove_fields
                else None
            )
            server = MCPServer(
                reptor_instance=self.reptor,
                field_excluder=field_excluder,
                logger=logger,
            )

            server.run(transport=self.transport)
        except ImportError as e:
            self.error(str(e))
        except Exception as e:
            self.error(f"Failed to start MCP server: {e}")


loader = Mcp
