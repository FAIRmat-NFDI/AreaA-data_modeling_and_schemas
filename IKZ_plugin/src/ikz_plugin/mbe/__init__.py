from nomad.config.models.plugins import SchemaPackageEntryPoint
from pydantic import Field


class MbeSchemaPackageEntryPoint(SchemaPackageEntryPoint):
    parameter: int = Field(0, description='Custom configuration parameter')

    def load(self):
        from ikz_plugin.mbe.schema import m_package

        return m_package


mbe_schema = MbeSchemaPackageEntryPoint(
    name='MbeSchema',
    description='Schema package defined using the new plugin mechanism.',
)
