import numpy as np
import yaml
import json
import math

from nomad.datamodel.data import EntryData, EntryDataCategory, ArchiveSection

from nomad.metainfo import (
    Package,
    Quantity,
    SubSection,
    Datetime,
    Section,
    Category,
    MEnum,
)

from nomad.datamodel.metainfo.basesections import (
    CompositeSystem,
    Component,
    System,
    Activity,
    ActivityStep,
    Process,
    CompositeSystemReference,
    PureSubstanceSection,
)

from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    ELNComponentEnum,
)

from nomad.utils import hash

from ikz_plugin.utils import create_archive

m_package = Package(name="basesections_IKZ")


class IKZCategory(EntryDataCategory):
    m_def = Category(label="IKZ", categories=[EntryDataCategory])


class IKZMOVPECategory(EntryDataCategory):
    m_def = Category(label="MOVPE", categories=[EntryDataCategory, IKZCategory])


class IKZMOVPE1Category(EntryDataCategory):
    m_def = Category(label="MOVPE 1", categories=[EntryDataCategory, IKZCategory])


class IKZMOVPE2Category(EntryDataCategory):
    m_def = Category(label="MOVPE 2", categories=[EntryDataCategory, IKZCategory])


class IKZDSCategory(EntryDataCategory):
    m_def = Category(
        label="Directional Solidification", categories=[EntryDataCategory, IKZCategory]
    )


class IKZHallCategory(EntryDataCategory):
    m_def = Category(label="Hall", categories=[EntryDataCategory, IKZCategory])


class SubstratePreparationStep(Activity):
    """
    A section used for referencing Activities performed on Substrate.
    """

    m_def = Section()


class SolutionPreparationStep(Activity):
    """
    A section used for referencing Activities performed on Substrate.
    """

    m_def = Section()


class SolutionProperties(ArchiveSection):
    ph_value = Quantity(
        type=np.dtype(np.float64), a_eln=dict(component="NumberEditQuantity")
    )

    final_volume = Quantity(
        type=np.dtype(np.float64),
        unit=("ml"),
        a_eln=dict(component="NumberEditQuantity", defaultDisplayUnit="ml"),
    )

    final_concentration = Quantity(
        type=np.dtype(np.float64),
        unit=("mg/ml"),
        a_eln=dict(component="NumberEditQuantity", defaultDisplayUnit="mg/ml"),
    )


class SolutionStorage(ArchiveSection):
    start_date = Quantity(type=Datetime, a_eln=dict(component="DateTimeEditQuantity"))

    end_date = Quantity(type=Datetime, a_eln=dict(component="DateTimeEditQuantity"))

    storage_condition = Quantity(
        type=str,
        a_eln=dict(component="StringEditQuantity"),
    )
    temperature = Quantity(
        type=np.dtype(np.float64),
        unit=("°C"),
        a_eln=dict(component="NumberEditQuantity", defaultDisplayUnit="°C"),
    )

    atmosphere = Quantity(
        type=str,
        a_eln=dict(
            component="EnumEditQuantity", props=dict(suggestions=["Ar", "N2", "Air"])
        ),
    )

    comments = Quantity(
        type=str,
        a_eln=dict(component="RichTextEditQuantity"),
    )


class Solution(CompositeSystem, EntryData):
    """Base class for a solution"""

    method = Quantity(
        type=MEnum("Shaker", "Ultrasoncic", "Waiting", "Stirring"),
        shape=[],
        a_eln=dict(
            component="EnumEditQuantity",
        ),
    )

    solvent_ratio = Quantity(type=str, a_eln=dict(component="StringEditQuantity"))

    temperature = Quantity(
        type=np.dtype(np.float64),
        unit=("°C"),
        a_eln=dict(component="NumberEditQuantity", defaultDisplayUnit="°C"),
    )

    time = Quantity(
        type=np.dtype(np.float64),
        unit=("minute"),
        a_eln=dict(component="NumberEditQuantity", defaultDisplayUnit="minute"),
    )

    speed = Quantity(
        type=np.dtype(np.float64),
        unit=("Hz"),
        a_eln=dict(component="NumberEditQuantity", defaultDisplayUnit="rpm"),
    )

    # components = SubSection(
    #     description="""
    #     A list of all the components of the composite system containing a name, reference
    #     to the system section and mass of that component.
    #     """,
    #     section_def=Component,
    #     repeats=True,
    # )
    solute = SubSection(
        description="""
        A list of all the components of the composite system containing a name, reference
        to the system section and mass of that component.
        """,
        section_def=Component,
        repeats=True,
    )
    additive = SubSection(
        description="""
        A list of all the components of the composite system containing a name, reference
        to the system section and mass of that component.
        """,
        section_def=Component,
        repeats=True,
    )
    solvent = SubSection(
        description="""
        A list of all the components of the composite system containing a name, reference
        to the system section and mass of that component.
        """,
        section_def=Component,
        repeats=True,
    )
    # solute = SubSection(section_def=SolutionChemical, repeats=True)
    # additive = SubSection(section_def=SolutionChemical, repeats=True)
    # solvent = SubSection(section_def=SolutionChemical, repeats=True)
    # other_solution = SubSection(section_def=OtherSolution, repeats=True)
    # preparation = SubSection(section_def=SolutionPreparation)
    properties = SubSection(section_def=SolutionProperties)
    # storage = SubSection(section_def=SolutionStorage, repeats=True)
    # solution_id = SubSection(section_def=ReadableIdentifiersCustom)

    def normalize(self, archive, logger) -> None:
        super(Solution, self).normalize(archive, logger)

        self.components = []
        if self.solute:
            self.components.extend(self.solute)
        if self.solvent:
            self.components.extend(self.solvent)


class QuantifyMaterial(
    Process, EntryData
):  #### TODO it overlaps someohow with Component class
    """
    Weigh or pipette a material.
    """

    alias = Quantity(
        type=str,
        a_eln={"component": "StringEditQuantity"},
    )
    container_mass = Quantity(
        type=float,
        description="FILL THE DESCRIPTION",
        a_eln={"component": "NumberEditQuantity", "defaultDisplayUnit": "gram"},
        unit="gram",
    )
    net_mass = Quantity(
        type=float,
        description="FILL THE DESCRIPTION",
        a_eln={"component": "NumberEditQuantity", "defaultDisplayUnit": "gram"},
        unit="gram",
    )
    brutto_mass = Quantity(
        type=float,
        description="FILL THE DESCRIPTION",
        a_eln={"component": "NumberEditQuantity", "defaultDisplayUnit": "gram"},
        unit="gram",
    )
    reference = Quantity(
        type=System,
        description="A reference to a NOMAD `CompositeSystem` entry.",
        a_eln=ELNAnnotation(
            component="ReferenceEditQuantity",
            label="Composite System Reference",
        ),
    )


# Weighing

#### TODO it overlaps someohow with Component class


class QuantifySolidMaterial(QuantifyMaterial, SolutionPreparationStep, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        a_eln=None,
        categories=[IKZCategory],
    )
    # molecular_weight


# Pipetting


#### TODO it overlaps someohow with Component class
class QuantifyLiquidMaterial(QuantifyMaterial, SolutionPreparationStep, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        a_eln=None,
        categories=[IKZCategory],
    )
    measured_volume = Quantity(
        type=float,
        description="FILL THE DESCRIPTION",
        a_eln={"component": "NumberEditQuantity", "defaultDisplayUnit": "liter"},
        unit="liter",
    )
    density = Quantity(
        type=float,
        description="FILL THE DESCRIPTION",
        a_eln={"component": "NumberEditQuantity", "defaultDisplayUnit": "gram / liter"},
        unit="gram / liter",
    )
    # molecular_weight


# class MixMaterial(Process, SolutionPreparationStep, EntryData):
#     """
#     Mix the quantified materials.
#     """

#     m_def = Section(
#         a_eln=None,
#         categories=[IKZCategory],
#     )
#     alias = Quantity(
#         type=str,
#         a_eln={"component": "StringEditQuantity"},
#     )
#     mixed_aliases = Quantity(
#         type=str,
#         a_eln={"component": "StringEditQuantity"},
#     )
#     mixing_time = Quantity(
#         type=float,
#         description="FILL THE DESCRIPTION",
#         a_eln={"component": "NumberEditQuantity", "defaultDisplayUnit": "second"},
#         unit="second",
#     )
#     temperature = Quantity(
#         type=np.float64,
#         description="FILL THE DESCRIPTION",
#         a_eln={"component": "NumberEditQuantity", "defaultDisplayUnit": "celsius"},
#         unit="celsius",
#     )
#     container_type = Quantity(
#         type=str,
#         a_eln={"component": "StringEditQuantity"},
#     )
#     rotation_speed = Quantity(
#         type=float,
#         description="FILL THE DESCRIPTION",
#         a_eln={"component": "NumberEditQuantity", "defaultDisplayUnit": "rpm"},
#         unit="rpm",
#     )
#     mixed_material = SubSection(
#         description="""
#         The mixed material.
#         """,
#         section_def=CompositeSystem,
#     )


class SolutionPreparationIKZ(Process, EntryData):
    """
    Solution preparation class
    """

    description = Quantity(
        type=str,
        a_eln={"component": "StringEditQuantity"},
    )
    atmosphere = Quantity(
        type=str,
        a_eln={"component": "StringEditQuantity"},
    )
    intended_sample_conc = Quantity(  # TODO make this a single flow
        type=np.float64,
        description="FILL THE DESCRIPTION",
        a_eln={"component": "NumberEditQuantity", "defaultDisplayUnit": "mol / liter"},
        unit="mol / liter",
    )
    obtained_conc = Quantity(  # TODO make this a single flow
        type=np.float64,
        description="FILL THE DESCRIPTION",
        a_eln={"component": "NumberEditQuantity", "defaultDisplayUnit": "mol / liter"},
        unit="mol / liter",
    )
    intended_tot_volume = Quantity(  # TODO make this a single flow
        type=np.float64,
        description="FILL THE DESCRIPTION",
        a_eln={"component": "NumberEditQuantity", "defaultDisplayUnit": "mol / liter"},
        unit="mol / liter",
    )
    obtained_tot_volume = Quantity(  # TODO make this a single flow
        type=np.float64,
        description="FILL THE DESCRIPTION",
        a_eln={"component": "NumberEditQuantity", "defaultDisplayUnit": "mol / liter"},
        unit="mol / liter",
    )
    mixing_time = Quantity(
        type=float,
        description="FILL THE DESCRIPTION",
        a_eln={"component": "NumberEditQuantity", "defaultDisplayUnit": "second"},
        unit="second",
    )
    temperature = Quantity(
        type=np.float64,
        description="FILL THE DESCRIPTION",
        a_eln={"component": "NumberEditQuantity", "defaultDisplayUnit": "celsius"},
        unit="celsius",
    )
    container_type = Quantity(
        type=str,
        a_eln={"component": "StringEditQuantity"},
    )
    rotation_speed = Quantity(
        type=float,
        description="FILL THE DESCRIPTION",
        a_eln={"component": "NumberEditQuantity", "defaultDisplayUnit": "rpm"},
        unit="rpm",
    )
    mixed_material = SubSection(
        description="""
        The mixed material.
        """,
        section_def=CompositeSystem,
    )
    ## TODO steps or components ???
    # steps = SubSection(
    #     section_def=SolutionPreparationStep,
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


class EtchingStep(ActivityStep):
    """
    A step of etching process.
    """

    m_def = Section()
    duration = Quantity(
        type=float,
        unit="second",
        description="Past time since process started (minutes)",
    )
    temperature = Quantity(
        type=np.float64,
        description="FILL THE DESCRIPTION",
        a_eln={"component": "NumberEditQuantity", "defaultDisplayUnit": "celsius"},
        unit="celsius",
    )
    etching_reagents = SubSection(section_def=CompositeSystem, repeats=True)


class Etching(Process, SubstratePreparationStep, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        a_eln=None,
        categories=[IKZCategory],
    )
    method = Quantity(
        type=str,
        default="Etching (MOVPE IKZ)",
    )
    datetime = Quantity(
        type=Datetime,
        description="FILL",
        a_eln={"component": "DateTimeEditQuantity", "label": "deposition_date"},
    )
    steps = SubSection(
        description="""
        The steps of the etching process.
        """,
        section_def=EtchingStep,
        repeats=True,
    )


class Annealing(Process, SubstratePreparationStep, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        a_eln=None,
        categories=[IKZCategory],
    )
    method = Quantity(
        type=str,
        default="Annealing (MOVPE IKZ)",
    )
    datetime = Quantity(
        type=Datetime,
        description="FILL",
        a_eln={"component": "DateTimeEditQuantity", "label": "deposition_date"},
    )
    temperature = Quantity(
        type=np.float64,
        description="FILL THE DESCRIPTION",
        a_eln={"component": "NumberEditQuantity", "defaultDisplayUnit": "celsius"},
        unit="celsius",
    )
    elapsed_time = Quantity(
        type=np.float64,
        description="Past time since process started (minutes)",
        a_eln={"component": "NumberEditQuantity", "defaultDisplayUnit": "minute"},
        unit="minute",
    )
    anealing_reagents = SubSection(
        section_def=CompositeSystemReference,
    )


class SampleCutIKZ(Process, EntryData):
    """
    An Activity that can be used for cutting a sample in multiple ones.
    """

    m_def = Section(
        a_eln={"hide": ["steps", "samples", "instruments"]},
        label="Sample Cut",
        categories=[IKZCategory],
    )
    number_of_samples = Quantity(
        type=int,
        description='The number of samples generated from this "Sample Cut" Task.',
        a_eln=dict(component="NumberEditQuantity"),
    )
    parent_sample = SubSection(
        description="""
        The parent sample that is going to be cut.
        """,
        section_def=CompositeSystemReference,
    )
    children_samples = SubSection(
        description="""
        The children samples that are going to be created.
        """,
        section_def=CompositeSystemReference,
        repeats=True,
    )

    def normalize(self, archive, logger):
        from nomad.datamodel import EntryArchive, EntryMetadata

        super(SampleCutIKZ, self).normalize(archive, logger)
        filetype = "yaml"
        if not self.number_of_samples:
            logger.error(
                f"Error in SampleCut: 'number_of_samples' expected, but None found."
            )
        if not self.parent_sample:
            logger.error(
                f"Error in SampleCut: 'parent_sample' expected, but None found."
            )
        if self.children_samples:
            logger.error(
                f"Error in SampleCut: No children samples expected,"
                f" but {len(self.children_samples)} children samples given."
                f" Remove the children samples and save again."
            )
        generated_samples = []
        if self.parent_sample and self.number_of_samples:
            for sample_index in range(self.number_of_samples):
                children_filename = f"{self.parent_sample.reference.lab_id}_child{sample_index}.CompositeSystem.archive.{filetype}"
                children_object = self.parent_sample.reference.m_copy(deep=True)
                children_object.name = (
                    f"{self.parent_sample.reference.lab_id}_child{sample_index}"
                )
                children_object.lab_id = (
                    f"{self.parent_sample.reference.lab_id}_child{sample_index}"
                )
                children_archive = EntryArchive(
                    data=children_object,
                    m_context=archive.m_context,
                    metadata=EntryMetadata(upload_id=archive.m_context.upload_id),
                )
                create_archive(
                    children_archive.m_to_dict(),
                    archive.m_context,
                    children_filename,
                    filetype,
                    logger,
                )
                generated_samples.append(
                    CompositeSystemReference(
                        name=children_object.name,
                        reference=f"../uploads/{archive.m_context.upload_id}/archive/{hash(archive.m_context.upload_id, children_filename)}#data",
                    ),
                )
            self.children_samples = generated_samples


m_package.__init_metainfo__()
