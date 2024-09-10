import yaml
from nomad.config.models.plugins import AppEntryPoint
from nomad.config.models.ui import (
    App,
    Column,
    Columns,
    FilterMenu,
    FilterMenus,
    Filters,
)

movpesubstrateapp = AppEntryPoint(
    name='MOVPESubstratesApp',
    description='Explore MOVPE substrates.',
    app=App(
        label='MOVPE Substrates',
        path='movpesubstrateapp',
        category='MOVPE',
        columns=Columns(
            selected=[
                'data.name#ikz_plugin.movpe.schema.SubstrateMovpe',
                'data.supplier#ikz_plugin.movpe.schema.SubstrateMovpe',
                'data.datetime#ikz_plugin.movpe.schema.SubstrateMovpe',
                'data.lab_id#ikz_plugin.movpe.schema.SubstrateMovpe',
                'data.crystal_properties.orientation#ikz_plugin.movpe.schema.SubstrateMovpe',
                'data.crystal_properties.miscut.angle#ikz_plugin.movpe.schema.SubstrateMovpe',
                'data.crystal_properties.miscut.orientation#ikz_plugin.movpe.schema.SubstrateMovpe',
                'data.geometry.length#ikz_plugin.movpe.schema.SubstrateMovpe',
                'data.geometry.width#ikz_plugin.movpe.schema.SubstrateMovpe',
                'data.electronic_properties.conductivity_type#ikz_plugin.movpe.schema.SubstrateMovpe',
                'data.tags#ikz_plugin.movpe.schema.SubstrateMovpe',
                'data.description#ikz_plugin.movpe.schema.SubstrateMovpe',
            ],
            options={
                'data.name#ikz_plugin.movpe.schema.SubstrateMovpe': Column(),
                'data.supplier#ikz_plugin.movpe.schema.SubstrateMovpe': Column(
                    label='Supplier ID'
                ),
                'data.datetime#ikz_plugin.movpe.schema.SubstrateMovpe': Column(
                    label='Delivery Date'
                ),
                'data.lab_id#ikz_plugin.movpe.schema.SubstrateMovpe': Column(
                    label='Substrate ID'
                ),
                'data.tags#ikz_plugin.movpe.schema.SubstrateMovpe': Column(
                    label='Substrate Box'
                ),
                'data.description#ikz_plugin.movpe.schema.SubstrateMovpe': Column(
                    label='Comment'
                ),
                'data.etching#ikz_plugin.movpe.schema.SubstrateMovpe': Column(),
                'data.annealing#ikz_plugin.movpe.schema.SubstrateMovpe': Column(),
                'data.re_etching#ikz_plugin.movpe.schema.SubstrateMovpe': Column(),
                'data.re_annealing#ikz_plugin.movpe.schema.SubstrateMovpe': Column(),
                'data.epi_ready#ikz_plugin.movpe.schema.SubstrateMovpe': Column(),
                'data.geometry.length#ikz_plugin.movpe.schema.SubstrateMovpe': Column(
                    label='Length', unit='mm'
                ),
                'data.geometry.width#ikz_plugin.movpe.schema.SubstrateMovpe': Column(
                    label='Width', unit='mm'
                ),
                'data.dopants.elements#ikz_plugin.movpe.schema.SubstrateMovpe': Column(),
                'data.dopants.doping_level#ikz_plugin.movpe.schema.SubstrateMovpe': Column(),
                'data.crystal_properties.orientation#ikz_plugin.movpe.schema.SubstrateMovpe': Column(),
                'data.crystal_properties.miscut.angle#ikz_plugin.movpe.schema.SubstrateMovpe': Column(
                    label='Miscut Angle'
                ),
                'data.crystal_properties.miscut.orientation#ikz_plugin.movpe.schema.SubstrateMovpe': Column(
                    label='Miscut Orientation'
                ),
                'data.electronic_properties.conductivity_type#ikz_plugin.movpe.schema.SubstrateMovpe': Column(),
            },
        ),
        filter_menus=FilterMenus(
            options={
                'material': FilterMenu(label='Material'),
                'eln': FilterMenu(label='Electronic Lab Notebook'),
                'custom_quantities': FilterMenu(label='User Defined Quantities'),
                'author': FilterMenu(label='Author / Origin / Dataset'),
                'metadata': FilterMenu(label='Visibility / IDs / Schema'),
            }
        ),
        filters=Filters(
            include=['*#ikz_plugin.movpe.schema.SubstrateMovpe'],
        ),
        filters_locked={
            'section_defs.definition_qualified_name': [
                'ikz_plugin.movpe.schema.SubstrateMovpe',
            ],
        },
    ),
)
