"""
Module containing NOMAD classes for material systems used in UV/Vis/NIR Transmission.
"""

import numpy as np
from ase.data import chemical_symbols

from nomad.datamodel.metainfo.basesections import (
    CompositeSystem,
    PubChemPureSubstanceSection,
    PureSubstance,
    SystemComponent,
    EntryData,
)
from nomad.metainfo import (
    Quantity,
    SubSection,
    MEnum,
    Section,
)
from nomad.datamodel.data import (
    ArchiveSection,
)
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    SectionProperties,
    Filter,
)


class CrystalProperties(ArchiveSection):
    pass


class CrystallinePureSubstance(PureSubstance, EntryData):
    m_def = Section(
        description='A pure substance component having a crystalline structure.',
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'substance_name',
                    'molecular_formula',
                ]
            )
        ),
    )
    molecular_formula = Quantity(
        type=str,
        description='Molecular formula of the component.',
        a_eln={'component': 'StringEditQuantity'},
    )
    crystal_properties = SubSection(
        section_def=CrystalProperties,
        description='Properties of the crystalline structure.',
    )

    def normalize(self, archive, logger: 'BoundLogger') -> None:
        # make PubChem API calls when required
        if self.pure_substance is None or self.pure_substance.iupac_name is None:
            pure_substance = PubChemPureSubstanceSection()
            if self.molecular_formula is not None:
                pure_substance.molecular_formula = self.molecular_formula
            pure_substance.normalize(archive, logger)
            if pure_substance.iupac_name is not None:
                # material was found in PubChem database
                self.pure_substance = pure_substance
                self.molecular_formula = pure_substance.molecular_formula
        super().normalize(archive, logger)


class HostComponent(SystemComponent):
    m_def = Section(
        description='Host component of the solid solution composed of crystalline '
        'substance.',
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'system',
                    'molecular_formula',
                ]
            )
        ),
    )
    system = Quantity(
        type=CrystallinePureSubstance,
        a_eln=dict(component='ReferenceEditQuantity'),
    )
    molecular_formula = Quantity(
        type=str,
        description='The molecular formula of the host component, e.g., LiYF4.',
        a_eln=dict(component='StringEditQuantity'),
    )

    def normalize(self, archive, logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)
        try:
            self.molecular_formula = self.system.pure_substance.molecular_formula
        except AttributeError:
            pass


class DopantComponent(SystemComponent):
    m_def = Section(
        description='Dopant component of the solid solution composed of a crystalline '
        'substance.',
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'system',
                    'molecular_formula',
                ]
            )
        ),
    )
    system = Quantity(
        type=CrystallinePureSubstance,
        a_eln=dict(component='ReferenceEditQuantity'),
    )
    molecular_formula = Quantity(
        type=str,
        description='The molecular formula of the dopant component, e.g., Pr.',
        a_eln=dict(component='StringEditQuantity'),
    )

    def normalize(self, archive, logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)
        try:
            self.molecular_formula = self.system.pure_substance.molecular_formula
        except AttributeError:
            pass


class ElementalDopantComponent(DopantComponent):
    m_def = Section(
        description=(
            'An elemental dopant added in small quantities which substitutes another '
            'element in the solvent.'
        ),
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'system',
                    'molecular_formula',
                    'substitution_element',
                    'nominal_concentration',
                    'measured_concentration',
                ],
            )
        ),
    )
    molecular_formula = Quantity(
        type=MEnum(chemical_symbols[1:]),
        description='The symbol of the dopant element, e.g., Pr.',
        a_eln=dict(component='AutocompleteEditQuantity'),
    )
    substitution_element = Quantity(
        type=MEnum(chemical_symbols[1:]),
        description=('The element in the host crystal that is being replaced.'),
        a_eln=dict(component='AutocompleteEditQuantity'),
    )
    nominal_concentration = Quantity(
        type=np.float64,
        description=(
            'Atomic percentage of solute element with respect to the '
            'substitution element determined during preparation. '
            'For example, 1 at.% Pr-doped LiYF4 is equivalent to Li(Pr0.01Y0.99)F4'
        ),
        a_eln={
            'component': 'NumberEditQuantity',
            'minValue': 0,
            'maxValue': 100,
        },
        unit='dimensionless',
    )
    measured_concentration = Quantity(
        type=np.float64,
        description=(
            'Atomic percentage of solute element with respect to the '
            'substitution element measured in the prepared sample using techniques like '
            'Transmission Spectrophotometry.'
        ),
        a_eln={
            'component': 'NumberEditQuantity',
            'minValue': 0,
            'maxValue': 100,
        },
        unit='dimensionless',
    )


class SolidSolution(CompositeSystem):
    m_def = Section(
        links=['https://doi.org/10.1351/goldbook.M03940'],
        description=(
            'A crystal containing other constituents (solutes) which fit into and '
            'are distributed in the lattice of the host crystal (solvent).'
        ),
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'molecular_formula',
                    'host',
                    'dopants',
                    'elemental_composition',
                    'crystal_properties',
                ],
                visible=Filter(
                    exclude=[
                        'datetime',
                        'lab_id',
                        'description',
                        'components',
                    ],
                ),
            ),
        ),
    )
    molecular_formula = Quantity(
        type=str,
        description='Molecular formula of the solid solution. Dopant concentrations is '
        'expressed relatively as fraction of substitution element. For example, '
        '1 at.% Pr-doped LiYF4 is expressed as Li(Pr0.01Y0.99)F4',
        a_eln={'component': 'StringEditQuantity'},
    )
    host = SubSection(
        section_def=HostComponent,
    )
    dopants = SubSection(
        section_def=ElementalDopantComponent,
        repeats=True,
    )
    crystal_properties = SubSection(
        section_def=CrystalProperties,
        description='Properties of the crystalline structure.',
    )

    def adjust_composition_for_dopant_substitution(self, archive, logger):
        """
        Adjust the atomic fraction of each element based on each dopant substitution.
        Dopants are solutes which are added in small quantities to the solvent.
        Dopant concentration is given as a percentage of the substitution element. It can
        be the measured concentration (first preference) or the nominal concentration.
        """

        if not self.host:
            return
        if not self.dopants:
            return
        for dopant in self.dopants:
            if dopant.measured_concentration is not None:
                dopant_concentration = dopant.measured_concentration
            elif dopant.nominal_concentration is not None:
                dopant_concentration = dopant.nominal_concentration
            else:
                continue

            # find the substitution element and the dopant in the elemental composition
            # and adjust their atomic fractions
            for element_substituted in self.elemental_composition:
                if element_substituted.element == dopant.substitution_element:
                    for element_substituting in self.elemental_composition:
                        if element_substituting.element == dopant.molecular_formula:
                            element_substituting.atomic_fraction = (
                                dopant_concentration
                                / 100
                                * element_substituted.atomic_fraction
                            )
                            element_substituted.atomic_fraction -= (
                                element_substituting.atomic_fraction
                            )
                            break
                    break

    @staticmethod
    def derive_molecular_formula(host, dopants):
        """
        Derive the molecular formula of the solid solution based on dopant substitutions.
        """
        if host.molecular_formula:
            molecular_formula = host.molecular_formula
        else:
            return ''
        for dopant in dopants:
            if dopant.molecular_formula is None or dopant.substitution_element is None:
                continue
            if dopant.measured_concentration is not None:
                dopant_concentration = dopant.measured_concentration
            elif dopant.nominal_concentration is not None:
                dopant_concentration = dopant.nominal_concentration
            else:
                continue
            fractional_symbol = (
                '('
                + dopant.molecular_formula
                + str('{:.2f}'.format(dopant_concentration.magnitude / 100))
                + ' '
                + dopant.substitution_element
                + str('{:.2f}'.format(1 - dopant_concentration.magnitude / 100))
                + ')'
            )
            molecular_formula = molecular_formula.replace(
                dopant.substitution_element, fractional_symbol
            )

        return molecular_formula

    def normalize(self, archive, logger: 'BoundLogger') -> None:
        self.components = []
        self.elemental_composition = []
        if self.host:
            self.components.append(self.host)
        if self.dopants:
            for dopant in self.dopants:
                self.components.append(dopant)
        super().normalize(archive, logger)

        if self.host and self.dopants:
            self.adjust_composition_for_dopant_substitution(archive, logger)
            # reset the mass fractions and recalculate them
            for element in self.elemental_composition:
                element.mass_fraction = None
            super().normalize(archive, logger)

            self.molecular_formula = self.derive_molecular_formula(
                host=self.host, dopants=self.dopants
            )
