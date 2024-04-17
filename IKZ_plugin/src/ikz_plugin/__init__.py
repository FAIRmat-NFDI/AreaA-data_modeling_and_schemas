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
    Reference,
)

from nomad.datamodel.metainfo.basesections import (
    CompositeSystem,
    Component,
    System,
    Activity,
    ActivityStep,
    ProcessStep,
    Process,
    CompositeSystemReference,
    PureSubstanceSection,
    PureSubstanceComponent,
)

from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    ELNComponentEnum,
)

from nomad_material_processing import SubstrateReference

from nomad_measurements import ActivityReference

from nomad.utils import hash

from ikz_plugin.utils import create_archive

m_package = Package(name='basesections_IKZ')


class IKZCategory(EntryDataCategory):
    m_def = Category(label='IKZ', categories=[EntryDataCategory])


class IKZMOVPECategory(EntryDataCategory):
    m_def = Category(label='MOVPE', categories=[EntryDataCategory, IKZCategory])


class IKZMOVPE1Category(EntryDataCategory):
    m_def = Category(label='MOVPE 1', categories=[EntryDataCategory, IKZCategory])


class IKZMOVPE2Category(EntryDataCategory):
    m_def = Category(label='MOVPE 2', categories=[EntryDataCategory, IKZCategory])


class IKZDSCategory(EntryDataCategory):
    m_def = Category(
        label='Directional Solidification', categories=[EntryDataCategory, IKZCategory]
    )


class IKZHallCategory(EntryDataCategory):
    m_def = Category(label='Hall', categories=[EntryDataCategory, IKZCategory])


class SubstratePreparationStep(Activity):
    """
    A section used for referencing Activities performed on Substrate.
    """

    m_def = Section()


class SubstratePreparationStepReference(ActivityReference):
    """
    A section used for referencing SubstratePreparationSteps.
    """

    reference = Quantity(
        type=SubstratePreparationStep,
        description='A reference to a NOMAD `SubstratePreparationSteps` entry.',
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
            label='SubstratePreparationSteps Reference',
        ),
    )


class SolutionPreparationStep(ActivityStep):
    """
    A section used for referencing Activities performed on Substrate.
    """

    m_def = Section()


class ComponentConcentration(ArchiveSection):
    """
    The concentration of a component in a mixed material.
    """

    alias = Quantity(
        type=str,
        description='The alias given to this material, will be used to fill the system reference.',
        a_eln={'component': 'StringEditQuantity'},
    )
    intended_concentration = Quantity(
        type=np.float64,
        description='The concentration planned for the mixed material.',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'mol / liter'},
        unit='mol / liter',
        label='Intended Concentration',
    )
    obtained_concentration = Quantity(
        type=np.float64,
        description='The concentration calculated from the mixed material weights and volumes.',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'mol / liter'},
        unit='mol / liter',
        label='Obtained Concentration',
    )
    system = Quantity(
        type=Reference(System.m_def),
        description='A reference to the component system.',
        a_eln=dict(component='ReferenceEditQuantity'),
    )


class SolutionProperties(ArchiveSection):
    """
    Solution preparation class
    """

    ph_value = Quantity(
        type=np.dtype(np.float64), a_eln=dict(component='NumberEditQuantity')
    )

    final_volume = Quantity(
        type=np.dtype(np.float64),
        unit=('ml'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ml'),
    )
    components_concentration = SubSection(
        section_def=ComponentConcentration,
        repeats=True,
    )


class SolutionStorage(ArchiveSection):
    """
    Solution storage class
    """

    start_date = Quantity(type=Datetime, a_eln=dict(component='DateTimeEditQuantity'))

    end_date = Quantity(type=Datetime, a_eln=dict(component='DateTimeEditQuantity'))

    storage_condition = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'),
    )
    temperature = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'),
    )

    atmosphere = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity', props=dict(suggestions=['Ar', 'N2', 'Air'])
        ),
    )

    comments = Quantity(
        type=str,
        a_eln=dict(component='RichTextEditQuantity'),
    )


class LiquidComponent(PureSubstanceComponent):
    """
    A section for describing a substance component and its role in a composite system.
    """

    substance_name = Quantity(
        type=str,
        description="""
        The name of the substance within the section where this component is contained.
        """,
        a_eln=dict(component='StringEditQuantity'),
    )
    volume = Quantity(
        type=np.float64,
        description='The solvent for the current substance.',
        unit='milliliter',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='milliliter'),
    )
    pure_substance = SubSection(
        section_def=PureSubstanceSection,
        description="""
        Section describing the pure substance that is the component.
        """,
    )


class Solution(CompositeSystem, EntryData):
    """
    Base class for a solution
    """

    solvent_ratio = Quantity(type=str, a_eln=dict(component='StringEditQuantity'))

    solute = SubSection(
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
    # other_solution = SubSection(section_def=OtherSolution, repeats=True)
    # preparation = SubSection(section_def=SolutionPreparation)
    properties = SubSection(section_def=SolutionProperties)
    # storage = SubSection(section_def=SolutionStorage, repeats=True)

    def normalize(self, archive, logger) -> None:
        super(Solution, self).normalize(archive, logger)

        self.components = []
        if self.solute:
            self.components.extend(self.solute)
        if self.solvent:
            self.components.extend(self.solvent)


class SolutionReference(CompositeSystemReference):
    """
    A section used for referencing a CompositeSystem.
    """

    reference = Quantity(
        type=Solution,
        description='A reference to a NOMAD `Solution` entry.',
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
            label='Solution Reference',
        ),
    )


class QuantifyMaterial(ProcessStep):
    """
    Weigh or pipette a material.
    """

    alias = Quantity(
        type=str,
        description='The alias given to this material, will be used in the mixing.',
        a_eln={'component': 'StringEditQuantity'},
    )
    container_mass = Quantity(
        type=float,
        description='The mass of the container.',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'gram'},
        unit='gram',
    )
    brutto_mass = Quantity(
        type=float,
        description='The mass of the material including the container.',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'gram'},
        unit='gram',
    )
    component = SubSection(
        description="""
        A list of all the components of the composite system containing a name, reference
        to the system section and mass of that component.
        """,
        section_def=Component,
        repeats=True,
    )


class QuantifySolidMaterial(QuantifyMaterial, SolutionPreparationStep):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        a_eln=None,
        categories=[IKZCategory],
    )


class QuantifyLiquidMaterial(QuantifyMaterial, SolutionPreparationStep):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        a_eln=None,
        categories=[IKZCategory],
    )
    measured_volume = Quantity(
        type=float,
        description='The volume of the liquid material.',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'liter'},
        unit='liter',
    )
    density = Quantity(
        type=float,
        description='The density of the liquid material.',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'gram / liter'},
        unit='gram / liter',
    )


class MixMaterial(SolutionPreparationStep):
    """
    Mix the quantified materials.
    """

    m_def = Section(
        a_eln=None,
        categories=[IKZCategory],
    )
    aliases = Quantity(
        type=str,
        description='The aliases of materials that will be used in the mixing.',
        a_eln={'component': 'StringEditQuantity'},
        shape=['*'],
    )
    mixed_alias = Quantity(
        type=str,
        description='The alias given to the mixed material, used to mix with other components afterwards.',
        a_eln={'component': 'StringEditQuantity'},
    )
    temperature = Quantity(
        type=np.float64,
        description='The temperature of the mixing process.',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'celsius'},
        unit='kelvin',
    )
    container_type = Quantity(
        type=str,
        description='The type of container used for mixing.',
        a_eln={'component': 'StringEditQuantity'},
    )
    rotation_speed = Quantity(
        type=float,
        description='The rotation speed of the mixing process.',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'rpm'},
        unit='rpm',
    )
    components_concentration = SubSection(
        section_def=ComponentConcentration,
        repeats=True,
    )


class SolutionPreparationIKZ(Process, EntryData):
    """
    Solution preparation class
    """

    method = Quantity(
        type=MEnum('Shaker', 'Ultrasoncic', 'Waiting', 'Stirring'),
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
        ),
        categories=[IKZCategory],
    )
    description = Quantity(
        type=str,
        description='The description of the solution preparation.',
        a_eln={'component': 'StringEditQuantity'},
    )
    atmosphere = Quantity(
        type=str,
        description='The atmosphere used for the solution preparation.',
        a_eln={'component': 'StringEditQuantity'},
    )
    intended_tot_volume = Quantity(
        type=float,
        description='The planned total volume of the solution.',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'liter'},
        unit='liter',
    )
    obtained_tot_volume = Quantity(
        type=float,
        description='The obtained total volume of the solution.',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'liter'},
        unit=' liter',
    )
    solution = SubSection(
        section_def=SolutionReference,
        description="""
        The obtained solution, composed by the sum of each mixing step.
        """,
    )
    steps = SubSection(
        section_def=SolutionPreparationStep,
        repeats=True,
    )


class EtchingStep(ActivityStep):
    """
    A step of etching process.
    """

    m_def = Section()
    duration = Quantity(
        type=float,
        unit='second',
        description='The duration of the etching step.',
    )
    temperature = Quantity(
        type=np.float64,
        description='The temperature of the etching process.',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'celsius'},
        unit='celsius',
    )
    etching_reagents = SubSection(section_def=CompositeSystem, repeats=True)


class Etching(SubstratePreparationStep, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        a_eln=None,
        categories=[IKZCategory],
    )
    method = Quantity(
        type=str,
        description='The etching method.',
        default='Etching (MOVPE IKZ)',
    )
    steps = SubSection(
        description="""
        The steps of the etching process.
        """,
        section_def=EtchingStep,
        repeats=True,
    )


class Annealing(SubstratePreparationStep, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        a_eln=None,
        categories=[IKZCategory],
    )
    method = Quantity(
        type=str,
        description='The annealing method.',
        default='Annealing (MOVPE IKZ)',
    )
    temperature = Quantity(
        type=np.float64,
        description='The temperature of the annealing process.',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'celsius'},
        unit='celsius',
    )
    elapsed_time = Quantity(
        type=np.float64,
        description='The elapsed time since the annealing process started.',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'minute'},
        unit='minute',
    )
    annealing_reagents = SubSection(
        section_def=CompositeSystemReference,
    )


class SubstratePreparationIKZ(Process, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        a_eln=None,
        label='Substrate Preparation',
        categories=[IKZCategory],
    )
    method = Quantity(
        type=str,
        default='Substrate Process (MOVPE IKZ)',
    )
    description = Quantity(
        type=str,
        description='description',
        a_eln={'component': 'StringEditQuantity'},
    )
    substrates = SubSection(
        section_def=SubstrateReference,
        repeats=True,
    )
    steps = SubSection(
        section_def=SubstratePreparationStepReference,
        repeats=True,
    )


class SampleCutIKZ(Process, EntryData):
    """
    An Activity that can be used for cutting a sample in multiple ones.
    """

    m_def = Section(
        a_eln={'hide': ['steps', 'samples', 'instruments']},
        label='Sample Cut',
        categories=[IKZCategory],
    )
    number_of_samples = Quantity(
        type=int,
        description='The number of samples generated from this "Sample Cut" Task.',
        a_eln=dict(component='NumberEditQuantity'),
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
        filetype = 'yaml'
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
                f'Error in SampleCut: No children samples expected,'
                f' but {len(self.children_samples)} children samples given.'
                f' Remove the children samples and save again.'
            )
        generated_samples = []
        if self.parent_sample and self.number_of_samples:
            for sample_index in range(self.number_of_samples):
                children_filename = f'{self.parent_sample.reference.lab_id}_child{sample_index}.CompositeSystem.archive.{filetype}'
                children_object = self.parent_sample.reference.m_copy(deep=True)
                children_object.name = (
                    f'{self.parent_sample.reference.lab_id}_child{sample_index}'
                )
                children_object.lab_id = (
                    f'{self.parent_sample.reference.lab_id}_child{sample_index}'
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
                        reference=f'../uploads/{archive.m_context.upload_id}/archive/{hash(archive.m_context.upload_id, children_filename)}#data',
                    ),
                )
            self.children_samples = generated_samples


m_package.__init_metainfo__()
