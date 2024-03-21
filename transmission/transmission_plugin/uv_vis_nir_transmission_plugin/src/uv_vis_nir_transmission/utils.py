from typing import (
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from nomad.datamodel.data import (
        ArchiveSection,
    )
    from structlog.stdlib import (
        BoundLogger,
    )


def merge_sections(
    section: 'ArchiveSection',
    update: 'ArchiveSection',
    logger: 'BoundLogger' = None,
) -> None:
    if update is None:
        return
    if section is None:
        section = update.m_copy()
        return
    if not isinstance(section, type(update)):
        raise TypeError(
            'Cannot merge sections of different types: '
            f'{type(section)} and {type(update)}'
        )
    for name, quantity in update.m_def.all_quantities.items():
        if not update.m_is_set(quantity):
            continue
        if not section.m_is_set(quantity):
            section.m_set(quantity, update.m_get(quantity))
        elif (
            quantity.is_scalar
            and section.m_get(quantity) != update.m_get(quantity)
            or quantity.repeats
            and (section.m_get(quantity) != update.m_get(quantity)).any()
        ):
            warning = f'Merging sections with different values for quantity "{name}".'
            if logger:
                logger.warning(warning)
            else:
                print(warning)
    for name, sub_section_def in update.m_def.all_sub_sections.items():
        count = section.m_sub_section_count(sub_section_def)
        if count == 0:
            for update_sub_section in update.m_get_sub_sections(sub_section_def):
                section.m_add_sub_section(sub_section_def, update_sub_section)
        elif count == update.m_sub_section_count(sub_section_def):
            for i in range(count):
                merge_sections(
                    section.m_get_sub_section(sub_section_def, i),
                    update.m_get_sub_section(sub_section_def, i),
                    logger,
                )
        elif update.m_sub_section_count(sub_section_def) > 0:
            warning = (
                f'Merging sections with different number of "{name}" sub sections.'
            )
            if logger:
                logger.warning(warning)
            else:
                print(warning)
