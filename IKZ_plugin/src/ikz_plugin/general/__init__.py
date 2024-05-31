from nomad.config.models.plugins import SchemaPackageEntryPoint
from pydantic import Field


class GeneralEntryPoint(SchemaPackageEntryPoint):
    parameter: int = Field(0, description='Custom configuration parameter')

    def load(self):
        from ikz_plugin.general.schema import m_package

        return m_package


general_schema = GeneralEntryPoint(
    name='GeneralSchema',
    description='Schema package defined using the new plugin mechanism.',
)
