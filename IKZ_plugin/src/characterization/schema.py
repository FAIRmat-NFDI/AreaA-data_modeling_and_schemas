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
from basesections import IKZCategory
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
from nomad_material_processing.chemical_vapor_deposition import (
    CVDBubbler,
    CVDVaporRate,
    CVDSource,
)

from nomad_measurements import (
    ActivityReference,
)

m_package = Package(name="characterization_IKZ")


class AFMresults(MeasurementResult):
    """
    The results of an AFM measurement
    """

    roughness = Quantity(
        type=np.float64,
        description="RMS roughness value obtained by AFM",
        a_eln={"component": "NumberEditQuantity", "defaultDisplayUnit": "picometer"},
        unit="picometer",
    )
    surface_features = Quantity(
        type=MEnum(["Step Flow", "Step Bunching", "2D Island"]),
        a_eln={"component": "EnumEditQuantity"},
    )
    scale = Quantity(
        type=np.float64,
        description="scale of the image, to be multiplied by 5 to know the image size",
        a_eln={"component": "NumberEditQuantity", "defaultDisplayUnit": "nanometer"},
        unit="nanometer",
    )
    image = Quantity(
        type=str,
        description="image showing the thickness measurement points",
        a_browser={"adaptor": "RawFileAdaptor"},
        a_eln={"component": "FileEditQuantity"},
    )
    crop_image = Quantity(
        type=str,
        description="crop image ready to be used for AI-based analysis",
        a_browser={"adaptor": "RawFileAdaptor"},
        a_eln={"component": "FileEditQuantity"},
    )


class AFMmeasurement(Measurement, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        a_eln={"hide": ["steps"]},
        categories=[IKZCategory],
        label="AFM",
    )

    method = Quantity(
        type=str,
        default="AFM (IKZ MOVPE)",
    )
    description = Quantity(
        type=str,
        a_eln={"component": "StringEditQuantity"},
    )
    datetime = Quantity(
        type=Datetime,
        a_eln={"component": "DateTimeEditQuantity"},
    )
    results = SubSection(
        section_def=AFMresults,
        repeats=True,
    )


class LiMiresults(MeasurementResult):
    """
    The results of a Light Microscope measurement
    """

    image = Quantity(
        type=str,
        description="image showing the thickness measurement points",
        a_browser={"adaptor": "RawFileAdaptor"},
        a_eln={"component": "FileEditQuantity"},
    )
    crop_image = Quantity(
        type=str,
        description="crop image ready to be used for AI-based analysis",
        a_browser={"adaptor": "RawFileAdaptor"},
        a_eln={"component": "FileEditQuantity"},
    )
    scale = Quantity(
        type=np.float64,
        description="scale of the image",
        a_eln={"component": "NumberEditQuantity", "defaultDisplayUnit": "micrometer"},
        unit="micrometer",
    )


class LightMicroscope(Measurement, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        a_eln={"hide": ["steps"]},
        categories=[IKZCategory],
        label="Light Microscope",
    )
    method = Quantity(
        type=str,
        default="Light Microscope (MOVPE IKZ)",
    )
    datetime = Quantity(
        type=Datetime,
        a_eln={"component": "DateTimeEditQuantity"},
    )
    results = SubSection(
        section_def=LiMiresults,
        repeats=True,
    )