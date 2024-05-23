from nomad.config.models.plugins import SchemaPackageEntryPoint
from pydantic import Field


class GeneralPackageEntryPoint(SchemaPackageEntryPoint):
    parameter: int = Field(0, description='Custom configuration parameter')

    def load(self):
        from ikz_plugin.general.general import m_package

        return m_package


general = GeneralPackageEntryPoint(
    name='General',
    description='Schema package defined using the new plugin mechanism.',
)
