from nomad.datamodel.metainfo.basesections import (
    ElementalComposition,
    Activity,
    Process,
)
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
)
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
)
from nomad.metainfo import Package, Quantity, SubSection, MEnum, Datetime, Section
from nomad.datamodel.data import EntryData

from ikz_plugin import (
    IKZCategory,
    SubstratePreparationStep,
)
from nomad_material_processing import (
    SubstrateReference,
    CrystallineSubstrate,
    Miscut,
    SubstrateCrystalProperties,
    Dopant,
    Parallelepiped,
)

from nomad_measurements import (
    ActivityReference,
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