import numpy as np

from plotly.subplots import make_subplots
import plotly.express as px


from nomad.config import config
from nomad.datamodel.data import ArchiveSection, EntryData
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    ELNComponentEnum,
    SectionProperties,
)
from nomad.datamodel.metainfo.basesections import (
    Component,
    Experiment,
    ExperimentStep,
    Process,
    PureSubstance,
    PureSubstanceSection,
    SectionReference,
    System,
    SystemComponent,
)

from nomad.datamodel.metainfo.workflow import (
    Link,
)
from nomad.metainfo import (
    Quantity,
    Reference,
    SchemaPackage,
    Section,
    SubSection,
)
from nomad.parsing.tabular import TableData


from nomad.datamodel.metainfo.plot import (
    PlotlyFigure,
    PlotSection,
)

from nomad_material_processing import (
    CrystallineSubstrate,
    Geometry,
    Miscut,
    SubstrateCrystalProperties,
    SubstrateReference,
    ThinFilm,
    ThinFilmStack,
    ThinFilmStackReference,
)
from nomad_material_processing.vapor_deposition import (
    ChamberEnvironment,
    GasFlow,
    Pressure,
    SampleParameters,
    SubstrateHeater,
    Temperature,
    VaporDeposition,
    VaporDepositionStep,
    VolumetricFlowRate,
)
from nomad_material_processing.vapor_deposition.cvd import (
    BubblerEvaporator,
    CVDSource,
    FlashEvaporator,
    GasSupply,
    Rotation,
)
from nomad_measurements import (
    ActivityReference,
)
from nomad_measurements.xrd import ELNXRayDiffraction
from structlog.stdlib import (
    BoundLogger,
)

from ikz_plugin.characterization.schema import AFMmeasurement, LightMicroscope
from ikz_plugin.general.schema import (
    IKZMOVPE1Category,
    IKZMOVPECategory,
    SubstratePreparationStepReference,
)

from lakeshore_nomad_plugin.hall.schema import HallMeasurement
from laytec_epitt_plugin.schema import LayTecEpiTTMeasurement

configuration = config.get_plugin_entry_point('ikz_plugin.movpe:movpe_schema')

m_package = SchemaPackage()


def is_activity_section(section):
    return any('Activity' in i.label for i in section.m_def.all_base_sections)


def handle_section(section):
    if hasattr(section, 'reference') and is_activity_section(section.reference):
        return [ExperimentStep(activity=section.reference, name=section.reference.name)]
    if section.m_def.label == 'CharacterizationMovpe':
        sub_sect_list = []
        for sub_section in vars(section).values():
            if isinstance(sub_section, list):
                for item in sub_section:
                    if hasattr(item, 'reference') and is_activity_section(
                        item.reference
                    ):
                        sub_sect_list.append(
                            ExperimentStep(
                                activity=item.reference, name=item.reference.name
                            )
                        )
        return sub_sect_list
    if not hasattr(section, 'reference') and is_activity_section(section):
        return [ExperimentStep(activity=section, name=section.name)]


class BubblerPrecursor(PureSubstance, EntryData):
    """
    A precursor already loaded in a bubbler.
    To calculate the vapor pressure the Antoine equation is used.
    log10(p) = A - [B / (T + C)]
    It is a mathematical expression (derived from the Clausius-Clapeyron equation)
    of the relation between the vapor pressure (p) and the temperature (T) of pure substances.
    """

    m_def = Section(categories=[IKZMOVPECategory])
    name = Quantity(
        type=str,
        description='FILL',
        a_eln=ELNAnnotation(component='StringEditQuantity', label='Substance Name'),
    )
    cas_number = Quantity(
        type=str,
        description='FILL',
        a_eln=ELNAnnotation(component='StringEditQuantity', label='CAS number'),
    )
    weight = Quantity(
        type=np.float64,
        description="""
        Weight of precursor and bubbler.
        Attention: Before weighing bubblers,
        all gaskets and corresponding caps must be attached!
        """,
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='gram',
        ),
        unit='kg',
    )
    weight_difference = Quantity(
        type=np.float64,
        description='Weight when the bubbler is exhausted.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='gram',
        ),
        unit='kg',
    )
    total_comsumption = Quantity(
        type=np.float64,
        description='FILL DESCRIPTION.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='gram',
        ),
        unit='kg',
    )
    a_parameter = Quantity(
        type=np.float64,
        description='The A parameter of Antoine equation. Dimensionless.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='millimeter',
        ),
        unit='millimeter',
    )
    b_parameter = Quantity(
        type=np.float64,
        description='The B parameter of Antoine equation. Temperature units.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='celsius',
        ),
        unit='kelvin',
    )
    c_parameter = Quantity(
        type=np.float64,
        description='The C parameter of Antoine equation. Temperature units.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='celsius',
        ),
        unit='kelvin',
    )
    information_sheet = Quantity(
        type=str,
        description='pdf files containing certificate and other documentation',
        a_browser={'adaptor': 'RawFileAdaptor'},
        a_eln=ELNAnnotation(
            component='FileEditQuantity',
        ),
    )


class Cylinder(Geometry):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section()
    height = Quantity(
        type=np.float64,
        description='docs',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='nanometer',
        ),
        unit='nanometer',
    )
    radius = Quantity(
        type=np.float64,
        description='docs',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='millimeter',
        ),
        unit='millimeter',
    )
    lower_cap_radius = Quantity(
        type=np.float64,
        description='docs',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='millimeter',
        ),
        unit='millimeter',
    )
    upper_cap_radius = Quantity(
        type=np.float64,
        description='docs',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='millimeter',
        ),
        unit='millimeter',
    )
    cap_surface_area = Quantity(
        type=np.float64,
        description='docs',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='millimeter ** 2',
        ),
        unit='millimeter ** 2',
    )
    lateral_surface_area = Quantity(
        type=np.float64,
        description='docs',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='millimeter ** 2',
        ),
        unit='millimeter ** 2',
    )


class MiscutMovpe(Miscut):
    """
    The miscut in a crystalline substrate refers to
    the intentional deviation from a specific crystallographic orientation,
    commonly expressed as the angular displacement of a crystal plane.
    """

    m_def = Section(label='Miscut')

    b_angle = Quantity(
        type=float,
        description='crystallographic orientation of the substrate in [hkl]',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
        ),
        a_tabular={
            'name': 'Substrate/Miscut b angle',
            # "unit": "deg"
        },
        unit='deg',
    )
    angle = Quantity(
        type=float,
        description='angular displacement from crystallographic orientation of the substrate',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='deg',
            label='c angle',
        ),
        unit='deg',
        a_tabular={
            'name': 'Substrate/Miscut c angle',
            # "unit": "deg"
        },
    )
    angle_deviation = Quantity(
        type=float,
        description='uncertainty on the angular displacement',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='deg',
            label='c angle deviation',
        ),
        unit='deg',
    )
    orientation = Quantity(
        type=str,
        description='crystallographic orientation of the substrate in [hkl]',
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
        ),
        a_tabular={'name': 'Substrate/Miscut c Orientation'},
    )


class SubstrateCrystalPropertiesMovpe(SubstrateCrystalProperties):
    """
    Characteristics arising from the ordered arrangement of atoms in a crystalline structure.
    These properties are defined by factors such as crystal symmetry, lattice parameters,
    and the specific arrangement of atoms within the crystal lattice.
    """

    m_def = Section(label='CrystalProperties')
    orientation = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
        ),
        a_tabular={'name': 'Substrate/Orientation'},
    )
    miscut = SubSection(section_def=MiscutMovpe)


class SubstrateMovpe(CrystallineSubstrate, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        label_quantity='lab_id', categories=[IKZMOVPECategory], label='Substrate'
    )
    as_received = Quantity(
        type=bool,
        description='Is the sample annealed?',
        a_eln=ELNAnnotation(
            component='BoolEditQuantity',
        ),
        # a_tabular={"name": "Substrate/As Received"},
    )
    etching = Quantity(
        type=bool,
        description='Usable Sample',
        a_eln=ELNAnnotation(
            component='BoolEditQuantity',
        ),
        # a_tabular={"name": "Substrate/Etching"},
    )
    annealing = Quantity(
        type=bool,
        description='Usable Sample',
        a_eln=ELNAnnotation(
            component='BoolEditQuantity',
        ),
        # a_tabular={"name": "Substrate/Annealing"},
    )
    # annealing_temperature = Quantity(
    #     type=np.float64,
    #     description='FILL THE DESCRIPTION',
    #     a_tabular={
    #         "name": "Substrate/Annealing Temperature"
    #     },
    #     a_eln={
    #         "component": "NumberEditQuantity",
    #         "defaultDisplayUnit": "celsius"
    #     },
    #     unit="celsius",
    # )
    tags = Quantity(
        type=str,
        description='FILL',
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
            label='Box ID',
        ),
        a_tabular={'name': 'Substrate/Substrate Box'},
    )
    re_etching = Quantity(
        type=bool,
        description='Usable Sample',
        a_eln=ELNAnnotation(
            component='BoolEditQuantity',
        ),
        a_tabular={'name': 'Substrate/Re-Etching'},
    )
    re_annealing = Quantity(
        type=bool,
        description='Usable Sample',
        a_eln=ELNAnnotation(
            component='BoolEditQuantity',
        ),
        a_tabular={'name': 'Substrate/Re-Annealing'},
    )
    epi_ready = Quantity(
        type=bool,
        description='Sample ready for epitaxy',
        a_eln=ELNAnnotation(
            component='BoolEditQuantity',
        ),
        a_tabular={'name': 'Substrate/Epi Ready'},
    )
    quality = Quantity(
        type=str,
        description='Defective Sample',
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
        ),
        a_tabular={'name': 'Substrate/Quality'},
    )
    information_sheet = Quantity(
        type=str,
        description='pdf files containing certificate and other documentation',
        a_browser={'adaptor': 'RawFileAdaptor'},
        a_eln=ELNAnnotation(
            component='FileEditQuantity',
        ),
    )
    description = Quantity(
        type=str,
        description='description',
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
            label='Notes',
        ),
    )


class ThinFilmMovpeIKZ(ThinFilm, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        label_quantity='lab_id',
        categories=[IKZMOVPECategory],
        label='ThinFilmMovpeIKZ',
    )
    lab_id = Quantity(
        type=str,
        description='the Sample created in the current growth',
        a_tabular={'name': 'GrowthRun/Sample Name'},
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
            label='Grown Sample ID',
        ),
    )
    test_quantities = Quantity(
        type=str,
        description='Test quantity',
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
        ),
    )


class ThinFilmStackMovpe(ThinFilmStack, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        label_quantity='lab_id',
        categories=[IKZMOVPECategory],
        label='ThinFilmStackMovpe',
    )
    lab_id = Quantity(
        type=str,
        description='the Sample created in the current growth',
        a_tabular={'name': 'GrowthRun/Sample Name'},
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
            label='Grown Sample ID',
        ),
    )
    test_quantities = Quantity(
        type=str,
        description='Test quantity',
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
        ),
    )


class ThinFilmStackMovpeReference(ThinFilmStackReference):
    """
    A section used for referencing a Grown Sample.
    """

    lab_id = Quantity(
        type=str,
        description='the Sample created in the current growth',
        a_tabular={'name': 'GrowthRun/Sample Name'},
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
            label='Grown Sample ID',
        ),
    )
    reference = Quantity(
        type=ThinFilmStackMovpe,
        description='A reference to a NOMAD `ThinFilmStackMovpe` entry.',
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
            label='ThinFilmStackMovpe Reference',
        ),
    )

    def normalize(self, archive, logger: BoundLogger) -> None:
        """
        The normalizer for the `ThinFilmStackMovpeReference` class.
        """
        super(ThinFilmStackMovpeReference, self).normalize(archive, logger)


class SystemComponentIKZ(SystemComponent):
    """
    A section for describing a system component and its role in a composite system.
    """

    molar_concentration = Quantity(
        type=np.float64,
        description='The solvent for the current substance.',
        unit='mol/liter',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mol/liter'),
        a_tabular={
            'name': 'Precursors/Molar conc',
            # "unit": "gram"
        },
    )
    system = Quantity(
        type=Reference(System.m_def),
        description='A reference to the component system.',
        a_eln=dict(component='ReferenceEditQuantity'),
    )


class PrecursorsPreparationIKZ(Process, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        a_eln={
            'hide': [
                'instruments',
                'steps',
                'samples',
            ]
        },
        label_quantity='name',
        categories=[IKZMOVPE1Category],
        label='PrecursorsPreparation',
    )
    data_file = Quantity(
        type=str,
        description='Upload here the spreadsheet file containing the deposition control data',
        a_browser={'adaptor': 'RawFileAdaptor'},
        a_eln={'component': 'FileEditQuantity'},
    )
    lab_id = Quantity(
        type=str,
        description='FILL',
        a_tabular={'name': 'Precursors/Sample ID'},
        a_eln={'component': 'StringEditQuantity', 'label': 'Sample ID'},
    )
    name = Quantity(
        type=str,
        description='FILL',
        a_tabular={'name': 'Precursors/number'},
        a_eln={
            'component': 'StringEditQuantity',
        },
    )
    description = Quantity(
        type=str,
        a_eln={'component': 'StringEditQuantity'},
    )
    flow_titanium = Quantity(  # TODO make this a single flow
        type=np.float64,
        description='FILL THE DESCRIPTION',
        a_tabular={'name': 'Precursors/Set flow Ti'},
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'ml / minute'},
        unit='ml / minute',
    )
    flow_calcium = Quantity(
        type=np.float64,
        description='FILL THE DESCRIPTION',
        a_tabular={'name': 'Precursors/Set flow Ca'},
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'ml / minute'},
        unit='ml / minute',
    )
    # precursors = SubSection(
    #     section_def=SystemComponent,
    #     description="""
    #     A precursor used in MOVPE. It can be a solution, a gas, or a solid.
    #     """,
    #     repeats=True,
    # )
    components = SubSection(
        description="""
        A list of all the components of the composite system containing a name, reference
        to the system section and mass of that component.
        """,
        section_def=Component,
        repeats=True,
    )


class PrecursorsPreparationIKZReference(ActivityReference):
    """
    A section used for referencing a PrecursorsPreparationIKZ.
    """

    m_def = Section(
        label='PrecursorsPreparationReference',
    )
    reference = Quantity(
        type=PrecursorsPreparationIKZ,
        description='A reference to a NOMAD `PrecursorsPreparationIKZ` entry.',
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
            label='PrecursorsPreparationIKZ Reference',
        ),
    )


class InSituMonitoringReference(SectionReference):
    """
    A section used for referencing a InSituMonitoring.
    """

    reference = Quantity(
        type=LayTecEpiTTMeasurement,
        description='A reference to a NOMAD `InSituMonitoring` entry.',
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
            label='In situ Monitoring Reference',
        ),
    )


class HallMeasurementReference(SectionReference):
    """
    A section used for referencing a HallMeasurement.
    The class is taken from the dedicated Lakeshore plugin
    """

    reference = Quantity(
        type=HallMeasurement,
        description='A reference to a NOMAD `HallMeasurement` entry.',
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
            label='Hall Measurement Reference',
        ),
    )


class SubstrateMovpeReference(SubstrateReference):
    """
    A section for describing a system component and its role in a composite system.
    """

    lab_id = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity,
            label='Substrate ID',
        ),
    )
    reference = Quantity(
        type=SubstrateMovpe,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.ReferenceEditQuantity,
            label='Substrate',
        ),
    )


class SubstrateInventory(EntryData, TableData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        a_eln=None,
        categories=[IKZMOVPECategory],
        label='SubstrateInventory',
    )
    data_file = Quantity(
        type=str,
        description='Upload here the spreadsheet file containing the substrates data',
        # a_tabular_parser={
        #     "parsing_options": {"comment": "#"},
        #     "mapping_options": [
        #         {
        #             "mapping_mode": "row",
        #             "file_mode": "multiple_new_entries",
        #             "sections": ["substrates"],
        #         }
        #     ],
        # },
        a_browser={'adaptor': 'RawFileAdaptor'},
        a_eln={'component': 'FileEditQuantity'},
    )
    substrates = SubSection(
        section_def=SubstrateMovpeReference,
        repeats=True,
    )
    steps = SubSection(
        section_def=SubstratePreparationStepReference,
        repeats=True,
    )


class AFMmeasurementReference(SectionReference):
    """
    A section used for referencing a AFMmeasurement.
    """

    reference = Quantity(
        type=AFMmeasurement,
        description='A reference to a NOMAD `AFMmeasurement` entry.',
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
            label='AFM Measurement Reference',
        ),
    )


class LiMimeasurementReference(SectionReference):
    """
    A section used for referencing a LightMicroscope.
    """

    reference = Quantity(
        type=LightMicroscope,
        description='A reference to a NOMAD `LightMicroscope` entry.',
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
            label='Light Microscope Measurement Reference',
        ),
    )


class XRDmeasurementReference(SectionReference):
    """
    A section used for referencing a LightMicroscope.
    """

    reference = Quantity(
        type=ELNXRayDiffraction,
        description='A reference to a NOMAD `ELNXRayDiffraction` entry.',
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
            label='XRD Measurement Reference',
        ),
    )


class CharacterizationMovpe(ArchiveSection):
    """
    A wrapped class to gather all the characterization methods in MOVPE
    """

    xrd = SubSection(
        section_def=XRDmeasurementReference,
        repeats=True,
    )
    in_situ_reflectance = SubSection(
        section_def=InSituMonitoringReference,
        repeats=True,
    )
    hall = SubSection(
        section_def=HallMeasurementReference,
        repeats=True,
    )
    afm = SubSection(
        section_def=AFMmeasurementReference,
        repeats=True,
    )
    light_microscopy = SubSection(
        section_def=LiMimeasurementReference,
        repeats=True,
    )


class ShaftTemperature(Temperature):
    """
    Central shaft temperature (to hold the susceptor)
    """

    pass


class FilamentTemperature(Temperature):
    """
    heating filament temperature
    """

    pass


class LayTecTemperature(Temperature):
    """
    Central shaft temperature (to hold the susceptor)
    """

    pass


class BubblerSourceIKZ(CVDSource):
    vapor_source = SubSection(
        section_def=BubblerEvaporator,
    )


class FlashSourceIKZ(CVDSource):
    vapor_source = SubSection(
        section_def=FlashEvaporator,
        description="""
        Example: A heater, a filament, a laser, a bubbler, etc.
        """,
    )


class GasSourceIKZ(CVDSource):
    vapor_source = SubSection(
        section_def=GasSupply,
    )


class GasFlowMovpe(GasFlow):
    gas = SubSection(
        section_def=PureSubstanceSection,
    )
    flow_rate = SubSection(
        section_def=VolumetricFlowRate,
        label='Push Flow Rate',
    )
    purge_flow_rate = SubSection(
        section_def=VolumetricFlowRate,
    )


class ChamberEnvironmentMovpe(ChamberEnvironment):
    uniform_gas_flow_rate = SubSection(
        section_def=VolumetricFlowRate,
    )
    pressure = SubSection(
        section_def=Pressure,
    )
    throttle_valve = SubSection(
        section_def=Pressure,
    )
    rotation = SubSection(
        section_def=Rotation,
    )
    heater = SubSection(
        section_def=SubstrateHeater,
    )


class SampleParametersMovpe(SampleParameters):
    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'shaft_temperature',
                    'filament_temperature',
                    'laytec_temperature',
                    'substrate_temperature',
                    'in_situ_reflectance',
                    'growth_rate',
                    'layer',
                    'substrate',
                ],
            ),
        ),
        a_plotly_graph_object=[
            {
                'label': 'shaft temperature',
                'index': 0,
                'dragmode': 'pan',
                'data': {
                    'type': 'scattergl',
                    'line': {'width': 2},
                    'marker': {'size': 6},
                    'mode': 'lines+markers',
                    'name': 'Temperature',
                    'x': '#shaft_temperature/time',
                    'y': '#shaft_temperature/value',
                },
                'layout': {
                    'title': {'text': 'Shaft Temperature'},
                    'xaxis': {
                        'showticklabels': True,
                        'fixedrange': True,
                        'ticks': '',
                        'title': {'text': 'Process time [min]'},
                        'showline': True,
                        'linewidth': 1,
                        'linecolor': 'black',
                        'mirror': True,
                    },
                    'yaxis': {
                        'showticklabels': True,
                        'fixedrange': True,
                        'ticks': '',
                        'title': {'text': 'Temperature [°C]'},
                        'showline': True,
                        'linewidth': 1,
                        'linecolor': 'black',
                        'mirror': True,
                    },
                    'showlegend': False,
                },
                'config': {
                    'displayModeBar': False,
                    'scrollZoom': False,
                    'responsive': False,
                    'displaylogo': False,
                    'dragmode': False,
                },
            },
            {
                'label': 'filament temperature',
                'index': 1,
                'dragmode': 'pan',
                'data': {
                    'type': 'scattergl',
                    'line': {'width': 2},
                    'marker': {'size': 6},
                    'mode': 'lines+markers',
                    'name': 'Filament Temperature',
                    'x': '#filament_temperature/time',
                    'y': '#filament_temperature/value',
                },
                'layout': {
                    'title': {'text': 'Filament Temperature'},
                    'xaxis': {
                        'showticklabels': True,
                        'fixedrange': True,
                        'ticks': '',
                        'title': {'text': 'Process time [min]'},
                        # "showline": True,
                        'linewidth': 1,
                        'linecolor': 'black',
                        'mirror': True,
                    },
                    'yaxis': {
                        'showticklabels': True,
                        'fixedrange': True,
                        'ticks': '',
                        'title': {'text': 'Temperature [°C]'},
                        # "showline": True,
                        'linewidth': 1,
                        'linecolor': 'black',
                        'mirror': True,
                    },
                    'showlegend': False,
                },
                'config': {
                    'displayModeBar': False,
                    'scrollZoom': False,
                    'responsive': False,
                    'displaylogo': False,
                    'dragmode': False,
                },
            },
        ],
    )
    name = Quantity(
        type=str,
        description="""
        Sample name.
        """,
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
        ),
    )
    distance_to_source = Quantity(
        type=float,
        unit='meter',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'millimeter'},
        description="""
        The distance between the substrate and the source.
        It is an array because multiple sources can be used.
        """,
        shape=[1],
    )
    shaft_temperature = SubSection(
        section_def=ShaftTemperature,
    )
    filament_temperature = SubSection(
        section_def=FilamentTemperature,
    )
    laytec_temperature = SubSection(
        section_def=LayTecTemperature,
    )
    in_situ_reflectance = SubSection(
        section_def=InSituMonitoringReference,
    )


class GrowthStepMovpeIKZ(VaporDepositionStep, PlotSection):
    """
    Growth step for MOVPE IKZ
    """

    # name
    # step_index
    # creates_new_thin_film
    # duration
    # sources
    # sample_parameters
    # environment
    # description

    step_index = Quantity(
        type=str,
        description='the step index',
        a_tabular={'name': 'Constant Parameters/Step'},
        a_eln={
            'component': 'StringEditQuantity',
        },
    )


class GrowthStepMovpe1IKZ(GrowthStepMovpeIKZ):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        a_eln={'overview': True},
        label='Growth Step Movpe 1',
    )
    comment = Quantity(
        type=str,
        description='description',
        a_eln={'component': 'StringEditQuantity'},
        label='Notes',
    )
    temperature_substrate = Quantity(  # CHECK why they are not in the new excel
        type=np.float64,
        description='FILL THE DESCRIPTION',
        a_tabular={'name': 'Constant Parameters/Substrate temperature'},
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'celsius'},
        unit='celsius',
    )
    peristaltic_pump_rotation_titan = (
        Quantity(  # CHECK why they are not in the new excel
            type=np.float64,
            description='FILL THE DESCRIPTION',
            a_tabular={'name': 'Constant Parameters/Peristaltic pump rotation Titan'},
            a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'celsius'},
            unit='celsius',
        )
    )
    peristaltic_pump_rotation_Sr_La = (
        Quantity(  # CHECK why they are not in the new excel
            type=np.float64,
            description='FILL THE DESCRIPTION',
            a_tabular={'name': 'Constant Parameters/Peristaltic pump rotation Sr La'},
            a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'celsius'},
            unit='celsius',
        )
    )
    duration = VaporDepositionStep.duration.m_copy()

    sample_parameters = SubSection(
        section_def=SampleParametersMovpe,
        repeats=True,
        label='Samples',
    )
    sources = SubSection(
        section_def=CVDSource,
        repeats=True,
    )
    environment = SubSection(
        section_def=ChamberEnvironmentMovpe,
    )

    def normalize(self, archive, logger):
        super(GrowthStepMovpe1IKZ, self).normalize(archive, logger)

        max_rows = 4
        max_cols = 2
        figure1 = make_subplots(
            rows=max_rows,
            cols=max_cols,
            subplot_titles=[
                'Chamber Pressure',
                'Filament T',
                'FE1 Back Pressure',
                'FE2 Back Pressure',
                'Oxygen T',
                'Rotation',
                'Shaft T',
                'Throttle Valve',
            ],
        )  # , shared_yaxes=True)
        arrays = {
            'chamber_pressure': self.environment.pressure,
            'filament_temp': self.sample_parameters[0].filament_temperature,
            'flash_evap1': self.sources[0].vapor_source.pressure,
            'flash_evap2': self.sources[1].vapor_source.pressure,
            'oxy_temp': self.sources[2].vapor_source.temperature,
            'rotation': self.environment.rotation,
            'shaft_temp': self.sample_parameters[0].shaft_temperature,
            'throttle_valve': self.environment.throttle_valve,
        }
        row = 1
        col = 0
        # for logged_par in sorted(arrays):
        #     # for logged_par_instance in arrays[logged_par]['obj']:
        #     if (
        #         arrays[logged_par]["obj"].value.m.any()
        #         and arrays[logged_par]["obj"].time.m.any()
        #     ):
        #         arrays[logged_par]["x"].append(arrays[logged_par]["obj"].time.m)
        #         arrays[logged_par]["y"].append(arrays[logged_par]["obj"].value.m)
        #     # else:
        #     #     logger.warning(f"{str(logged_par_instance)} was empty, check the cells or the column headers in your excel file.")
        #     if arrays[logged_par]["x"] and arrays[logged_par]["y"]:
        #         scatter = px.scatter(
        #             x=arrays[logged_par]["x"], y=arrays[logged_par]["y"]
        #         )
        #         if col == max_cols:
        #             row += 1
        #             col = 0
        #         if col < max_cols:
        #             col += 1
        #         figure1.add_trace(scatter.data[0], row=row, col=col)
        for logged_par in sorted(arrays):
            if (
                arrays[logged_par] is not None
                and arrays[logged_par].value is not None
                and arrays[logged_par].value.m is not None
                and arrays[logged_par].time is not None
                and arrays[logged_par].time.m is not None
            ):
                #     arrays[logged_par]["x"].append(arrays[logged_par]["obj"].time.m)
                #     arrays[logged_par]["y"].append(arrays[logged_par]["obj"].value.m)
                # else:
                #     print("empty")
                # if arrays[logged_par]["x"] and arrays[logged_par]["y"]:
                #     for x, y in zip(arrays[logged_par]["x"], arrays[logged_par]["y"]):
                #         figure1.add_trace(
                #             px.scatter(x=x, y=y).data[0], row=row, col=(col % max_cols) + 1
                #         )
                #     col += 1
                #     if col % max_cols == 0:
                #         row += 1
                x = arrays[logged_par].time.m
                y = arrays[logged_par].value.m
                col += 1
                if col > max_cols:
                    col = 1
                    row += 1
                if np.any(np.isfinite(x)) and np.any(np.isfinite(y)):
                    scatter = px.scatter(
                        x=x,
                        y=y,
                    )
                    figure1.add_trace(scatter.data[0], row=row, col=col)
                figure1.update_layout(
                    template='plotly_white',
                    height=800,
                    width=300,
                    # title_text='Creating Subplots in Plotly',
                )
            else:
                logger.warning(
                    f'{arrays[logged_par]} is an empty path, check your excel file and your parser.'
                )
        figure1.update_traces(line=dict(width=10), marker=dict(size=10))
        figure1.update_yaxes(
            ticks='outside',  # "",
            showticklabels=True,
            showline=True,
            linewidth=1,
            linecolor='black',
            mirror=True,
            row=[1, 2, 3, 4],
            col=[1, 2],
        )
        figure1.update_xaxes(
            ticks='outside',  # "",
            showticklabels=True,
            showline=True,
            linewidth=1,
            linecolor='black',
            mirror=True,
            row=[1, 2, 3, 4],
            col=[1, 2],
        )
        self.figures = [
            PlotlyFigure(label='figure 1', figure=figure1.to_plotly_json())
        ]  # .append(PlotlyFigure(label='figure 1', figure=figure1.to_plotly_json()))


class GrowthStepMovpe2IKZ(GrowthStepMovpeIKZ):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        label='Growth Step Movpe 2',
        a_eln=None,
    )
    name = Quantity(
        type=str,
        description="""
        A short and descriptive name for this step.
        """,
        a_tabular={'name': 'GrowthRun/Step name'},
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
            label='Step name',
        ),
    )
    step_index = Quantity(
        type=str,
        description='the ID from RTG',
        a_tabular={'name': 'GrowthRun/Step Index'},
        a_eln={
            'component': 'StringEditQuantity',
        },
    )
    duration = Quantity(
        type=float,
        unit='second',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
        ),
    )

    comment = Quantity(
        type=str,
        description='description',
        a_eln={'component': 'StringEditQuantity'},
        label='Notes',
    )
    sample_parameters = SubSection(
        section_def=SampleParametersMovpe,
        repeats=True,
    )
    sources = SubSection(
        section_def=CVDSource,
        repeats=True,
    )
    environment = SubSection(
        section_def=ChamberEnvironmentMovpe,
    )
    in_situ_reflectance = SubSection(
        section_def=InSituMonitoringReference,
    )


class GrowthMovpeIKZ(VaporDeposition, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'method',
                    'data_file',
                    'datetime',
                    'end_time',
                    'duration',
                ],
            ),
            # hide=[
            #     "instruments",
            #     "steps",
            #     "samples",
            #     "description",
            #     "location",
            #     "lab_id",
            # ],
        ),
        label_quantity='lab_id',
        categories=[IKZMOVPECategory],
        label='Growth Process',
    )

    # datetime
    # name
    # description
    # lab_id
    # method
    method = Quantity(
        type=str,
        default='MOVPE IKZ',
    )
    data_file = Quantity(
        type=str,
        description='Upload here the spreadsheet file containing the deposition control data',
        # a_tabular_parser={
        #     "parsing_options": {"comment": "#"},
        #     "mapping_options": [
        #         {
        #             "mapping_mode": "row",
        #             "file_mode": "multiple_new_entries",
        #             "sections": ["#root"],
        #         }
        #     ],
        # },
        a_browser={'adaptor': 'RawFileAdaptor'},
        a_eln={'component': 'FileEditQuantity'},
    )
    description = Quantity(
        type=str,
        description='description',
        a_eln={'component': 'StringEditQuantity'},
        label='Notes',
    )
    recipe_id = Quantity(
        type=str,
        description='the ID from RTG',
        a_tabular={'name': 'GrowthRun/Recipe Name'},
        a_eln={'component': 'StringEditQuantity', 'label': 'Recipe ID'},
    )
    steps = SubSection(
        section_def=GrowthStepMovpeIKZ,
        repeats=True,
    )

    def normalize(self, archive, logger):
        # for sample in self.samples:
        #     sample.normalize(archive, logger)
        # for parent_sample in self.parent_sample:
        #     parent_sample.normalize(archive, logger)
        # for substrate in self.substrate:
        #     substrate.normalize(archive, logger)

        archive.workflow2 = None
        super(GrowthMovpeIKZ, self).normalize(archive, logger)
        if self.steps is not None:
            inputs = []
            outputs = []
            for step in self.steps:
                if step.sample_parameters is not None:
                    for sample in step.sample_parameters:
                        if sample.layer is not None:
                            outputs.append(
                                Link(
                                    name=f'{sample.layer.name}',
                                    section=sample.layer.reference,
                                )
                            )
                        if sample.substrate is not None:
                            outputs.append(
                                Link(
                                    name=f'{sample.substrate.name}',
                                    section=sample.substrate.reference,
                                )
                            )

                        if (
                            sample.substrate is not None
                            and sample.substrate.reference is not None
                        ):
                            if hasattr(
                                getattr(sample.substrate.reference, 'substrate'),
                                'name',
                            ):
                                inputs.append(
                                    Link(
                                        name=f'{sample.substrate.reference.substrate.name}',
                                        section=getattr(
                                            sample.substrate.reference.substrate,
                                            'reference',
                                            None,
                                        ),
                                    )
                                )
            archive.workflow2.outputs.extend(set(outputs))
            archive.workflow2.inputs.extend(set(inputs))


class GrowthMovpeIKZReference(ActivityReference):
    """
    A section used for referencing a GrowthMovpeIKZ.
    """

    m_def = Section(
        label='GrowthProcessReference',
    )
    reference = Quantity(
        type=GrowthMovpeIKZ,
        description='A reference to a NOMAD `GrowthMovpeIKZ` entry.',
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        ),
    )


class GrowthMovpe1IKZConstantParameters(Process, EntryData, TableData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        # a_eln={"hide": ["samples"]},
        label_quantity='lab_id',  # "growth_id",
        categories=[IKZMOVPE1Category],
        label='Growth Process Constant parameters',
    )
    data_file = Quantity(
        type=str,
        description='Upload here the spreadsheet file containing the growth data',
        a_tabular_parser={
            'parsing_options': {'comment': '#'},
            'mapping_options': [
                {
                    'mapping_mode': 'row',
                    'file_mode': 'current_entry',
                    'sections': ['steps'],
                }
            ],
        },
        a_browser={'adaptor': 'RawFileAdaptor'},
        a_eln={'component': 'FileEditQuantity'},
    )
    method = Quantity(
        type=str,
        default='Growth (MOVPE 1 IKZ)',
    )
    description = Quantity(
        type=str,
        description='description',
        a_tabular={'name': 'Overview/Notes'},
        a_eln={'component': 'StringEditQuantity', 'label': 'Notes'},
    )
    lab_id = Quantity(
        type=str,
        description='FILL',
        a_eln={'component': 'StringEditQuantity', 'label': 'Constant Parameters ID'},
    )
    composition = Quantity(
        type=str,
        description='FILL THE DESCRIPTION',
        a_tabular={'name': 'Overview/Composition'},
        a_eln={
            'component': 'StringEditQuantity',
        },
    )
    substrate_temperature = Quantity(
        type=np.float64,
        description='FILL THE DESCRIPTION',
        a_tabular={'name': 'Overview/Substrate T'},
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'celsius'},
        unit='celsius',
    )
    oxygen_argon_ratio = Quantity(
        type=np.float64,
        description='FILL THE DESCRIPTION',
        a_tabular={'name': 'Overview/Oxygen Argon ratio'},
        a_eln={
            'component': 'NumberEditQuantity',
        },
    )
    steps = SubSection(
        section_def=GrowthStepMovpe1IKZ,
        repeats=True,
    )


class GrowthMovpe1IKZConstantParametersReference(ActivityReference):
    """
    A section used for referencing a GrowthMovpe1IKZConstantParameters.
    """

    m_def = Section(
        label='GrowthProcesses',
    )
    reference = Quantity(
        type=GrowthMovpe1IKZConstantParameters,
        description='A reference to a NOMAD `GrowthMovpe1IKZConstantParameters` entry.',
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
            label='GrowthMovpe1IKZConstantParameters Reference',
        ),
    )


class ExperimentMovpeIKZ(Experiment, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        # a_eln={"hide": ["steps"]},
        categories=[IKZMOVPECategory],
        label='MOVPE Experiment',
    )

    method = Quantity(
        type=str,
    )
    data_file = Quantity(
        type=str,
        description='Upload here the spreadsheet file containing the growth data',
        a_browser={'adaptor': 'RawFileAdaptor'},
        a_eln={'component': 'FileEditQuantity'},
    )
    description = Quantity(
        type=str,
        description='description',
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
            label='Notes',
        ),
    )
    substrate_temperature = Quantity(
        type=np.float64,
        description='FILL THE DESCRIPTION',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='celsius',
        ),
        unit='kelvin',
    )
    oxygen_argon_ratio = Quantity(
        type=str,
        description='FILL THE DESCRIPTION',
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
        ),
    )
    composition = Quantity(
        type=str,
        description='FILL THE DESCRIPTION',
        a_eln={
            'component': 'StringEditQuantity',
        },
    )
    precursors_preparation = SubSection(
        section_def=PrecursorsPreparationIKZReference,
    )
    growth_run = SubSection(
        section_def=GrowthMovpeIKZReference,
    )
    characterization = SubSection(section_def=CharacterizationMovpe)

    steps = SubSection(
        section_def=ActivityReference,
        repeats=True,
    )

    def normalize(self, archive, logger):
        archive_sections = (
            attr for attr in vars(self).values() if isinstance(attr, ArchiveSection)
        )
        step_list = []
        for section in archive_sections:
            try:
                step_list.extend(handle_section(section))
            except (AttributeError, TypeError, NameError) as e:
                print(f'An error occurred: {e}')
        self.steps = [step for step in step_list if step is not None]

        archive.workflow2 = None
        super(ExperimentMovpeIKZ, self).normalize(archive, logger)


m_package.__init_metainfo__()
