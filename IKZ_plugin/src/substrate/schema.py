import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
from ase.data import chemical_symbols
from nomad.datamodel.metainfo.basesections import (
    ElementalComposition,
    Activity,
    PureSubstance,
    ProcessStep,
    CompositeSystem,
    Measurement,
    MeasurementResult,
    Process,
    PureSubstanceComponent,
    PureSubstanceSection,
    EntityReference,
    CompositeSystemReference,
    PubChemPureSubstanceSection,
    SectionReference,
    Experiment,
)
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    SectionProperties,
)
from nomad.parsing.tabular import TableData
from structlog.stdlib import (
    BoundLogger,
)
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    ELNComponentEnum,
)
from nomad.metainfo import Package, Quantity, SubSection, MEnum, Datetime, Section
from nomad.datamodel.data import EntryData, ArchiveSection, Author
from nomad.search import search, MetadataPagination

from nomad.datamodel.metainfo.plot import PlotSection, PlotlyFigure

from laytec_epitt import LayTecEpiTTMeasurement
from hall import HallMeasurement
from basesections import (
    IKZCategory,
    Etching,
    Annealing,
)
from nomad_material_processing import (
    SubstrateReference,
    CrystallineSubstrate,
    Miscut,
    SubstrateCrystalProperties,
    Dopant,
    Geometry,
    Parallelepiped,
    ThinFilm,
    ThinFilmStack,
    ThinFilmStackReference,
)

from nomad.datamodel.metainfo.workflow import (
    Link,
    Task,
)

from nomad_measurements import (
    ActivityReference,
)

from characterization import (
    AFMmeasurement,
    LightMicroscope,
)

m_package = Package(name="substrate_IKZ")


class MiscutIKZ(Miscut):
    """
    The miscut in a crystalline substrate refers to
    the intentional deviation from a specific crystallographic orientation,
    commonly expressed as the angular displacement of a crystal plane.
    """

    m_def = Section(label="Miscut")

    b_angle = Quantity(
        type=float,
        description="crystallographic orientation of the substrate in [hkl]",
        a_eln=ELNAnnotation(
            component="NumberEditQuantity",
        ),
        a_tabular={
            "name": "Substrate/Miscut b angle",
            # "unit": "deg"
        },
        unit="deg",
    )
    angle = Quantity(
        type=float,
        description="angular displacement from crystallographic orientation of the substrate",
        a_eln=ELNAnnotation(
            component="NumberEditQuantity",
            defaultDisplayUnit="deg",
            label="c angle",
        ),
        unit="deg",
        a_tabular={
            "name": "Substrate/Miscut c angle",
            # "unit": "deg"
        },
    )
    angle_deviation = Quantity(
        type=float,
        description="uncertainty on the angular displacement",
        a_eln=ELNAnnotation(
            component="NumberEditQuantity",
            defaultDisplayUnit="deg",
            label="c angle deviation",
        ),
        unit="deg",
    )
    orientation = Quantity(
        type=str,
        description="crystallographic orientation of the substrate in [hkl]",
        a_eln=ELNAnnotation(
            component="StringEditQuantity",
        ),
        a_tabular={"name": "Substrate/Miscut c Orientation"},
    )


class SubstrateCrystalPropertiesIKZ(SubstrateCrystalProperties):
    """
    Characteristics arising from the ordered arrangement of atoms in a crystalline structure.
    These properties are defined by factors such as crystal symmetry, lattice parameters,
    and the specific arrangement of atoms within the crystal lattice.
    """

    m_def = Section(label="CrystalProperties")
    orientation = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component="StringEditQuantity",
        ),
        a_tabular={"name": "Substrate/Orientation"},
    )
    miscut = SubSection(section_def=MiscutIKZ)


class SubstrateIKZ(CrystallineSubstrate, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        label_quantity="lab_id", categories=[IKZCategory], label="Substrate"
    )

    datetime = Quantity(
        type=Datetime,
        description="Delivery Date of the Substrate",
        a_eln=ELNAnnotation(
            component="DateTimeEditQuantity",
            label="Delivery Date",
        ),
        a_tabular={"name": "Substrate/Delivery Date"},
    )
    lab_id = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component="StringEditQuantity",
            label="Substrate ID",
        ),
        a_tabular={"name": "Substrate/Substrates"},
    )
    supplier = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component="StringEditQuantity",
        ),
        a_tabular={"name": "Substrate/Supplier"},
    )
    supplier_id = Quantity(
        type=str,
        description="""An ID string that is unique from the supplier.""",
        a_eln=ELNAnnotation(
            component="StringEditQuantity",
            label="Polishing ID",
        ),
        a_tabular={"name": "Substrate/Polishing Number"},
    )
    tags = Quantity(
        type=str,
        description="FILL",
        a_eln=ELNAnnotation(
            component="StringEditQuantity",
            label="Box ID",
        ),
        a_tabular={"name": "Substrate/Substrate Box"},
    )
    as_received = Quantity(
        type=bool,
        description="Is the sample annealed?",
        a_eln=ELNAnnotation(
            component="BoolEditQuantity",
        ),
        a_tabular={"name": "Substrate/As Received"},
    )
    etching = Quantity(
        type=bool,
        description="Usable Sample",
        a_eln=ELNAnnotation(
            component="BoolEditQuantity",
        ),
        a_tabular={"name": "Substrate/Etching"},
    )
    annealing = Quantity(
        type=bool,
        description="Usable Sample",
        a_eln=ELNAnnotation(
            component="BoolEditQuantity",
        ),
        a_tabular={"name": "Substrate/Annealing"},
    )
    re_etching = Quantity(
        type=bool,
        description="Usable Sample",
        a_eln=ELNAnnotation(
            component="BoolEditQuantity",
        ),
        a_tabular={"name": "Substrate/Re-Etching"},
    )
    re_annealing = Quantity(
        type=bool,
        description="Usable Sample",
        a_eln=ELNAnnotation(
            component="BoolEditQuantity",
        ),
        a_tabular={"name": "Substrate/Re-Annealing"},
    )
    epi_ready = Quantity(
        type=bool,
        description="Sample ready for epitaxy",
        a_eln=ELNAnnotation(
            component="BoolEditQuantity",
        ),
        a_tabular={"name": "Substrate/Epi Ready"},
    )
    quality = Quantity(
        type=str,
        description="Defective Sample",
        a_eln=ELNAnnotation(
            component="StringEditQuantity",
        ),
        a_tabular={"name": "Substrate/Quality"},
    )
    documentation = Quantity(
        type=str,
        description="pdf files containing certificate and other documentation",
        a_browser={"adaptor": "RawFileAdaptor"},
        a_eln=ELNAnnotation(
            component="FileEditQuantity",
        ),
    )
    description = Quantity(
        type=str,
        description="description",
        a_eln=ELNAnnotation(
            component="StringEditQuantity",
            label="Notes",
        ),
    )
    geometry = SubSection(
        section_def=Parallelepiped,
    )
    crystal_properties = SubSection(section_def=SubstrateCrystalPropertiesIKZ)
    elemental_composition = SubSection(
        section_def=ElementalComposition,
        repeats=True,
    )
    dopants = SubSection(section_def=Dopant, repeats=True)


class SubstrateIKZReference(SubstrateReference):
    """
    A section for describing a system component and its role in a composite system.
    """

    lab_id = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity,
            label="Substrate ID",
        ),
    )
    reference = Quantity(
        type=SubstrateIKZ,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.ReferenceEditQuantity,
            label="Substrate",
        ),
    )


class SubstrateInventory(EntryData, TableData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        a_eln=None,
        #categories=[IKZMOVPECategory],
        label="SubstrateInventory",
    )
    substrate_data_file = Quantity(
        type=str,
        description="Upload here the spreadsheet file containing the substrates data",
        a_tabular_parser={
            "parsing_options": {"comment": "#"},
            "mapping_options": [
                {
                    "mapping_mode": "row",
                    "file_mode": "multiple_new_entries",
                    "sections": ["substrates"],
                }
            ],
        },
        a_browser={"adaptor": "RawFileAdaptor"},
        a_eln={"component": "FileEditQuantity"},
    )
    substrates = SubSection(
        section_def=SubstrateIKZReference,
        repeats=True,
    )


class SubstratePreparationStep(Activity):
    """
    A section used for referencing Activities performed on Substrate.
    """

    m_def = Section()


class EtchingForSubstrate(SubstratePreparationStep, Etching):
    pass


class AnnealingForSubstrate(SubstratePreparationStep, Annealing):
    pass


class AFMmeasurementForSubstrate(SubstratePreparationStep, AFMmeasurement):
    pass


class LightMicroscopeForSubstrate(SubstratePreparationStep, LightMicroscope):
    pass


class SubstratePreparationStepReference(ActivityReference):
    """
    A section used for referencing SubstratePreparationSteps.
    """

    reference = Quantity(
        type=SubstratePreparationStep,
        description="A reference to a NOMAD `SubstratePreparationSteps` entry.",
        a_eln=ELNAnnotation(
            component="ReferenceEditQuantity",
            label="Substrate Preparation Steps",
        ),
    )


class SubstratePreparation(Process, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        a_eln=None,
        categories=[IKZCategory],
    )
    method = Quantity(
        type=str,
        default="Substrate Process (MOVPE IKZ)",
    )
    description = Quantity(
        type=str,
        description="description",
        a_eln={"component": "StringEditQuantity"},
    )
    substrates = SubSection(
        section_def=SubstrateReference,
        repeats=True,
    )
    steps = SubSection(
        section_def=SubstratePreparationStepReference,
        repeats=True,
    )