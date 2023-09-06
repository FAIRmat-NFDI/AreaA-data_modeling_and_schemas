import json

from nomad.metainfo import (
    Package, Quantity, SubSection, Section)
from nomad.datamodel.data import EntryData
from nomad.datamodel.metainfo.workflow import Link
from nomad.datamodel.metainfo.eln import Entity, Activity, SampleID
from nomad.datamodel.util import parse_path


m_package = Package(name='basesections_IKZ')


class CollectionOfSystems(Entity, EntryData):
    '''
    A base class for a batch of materials. Each component of the batch is
    of a (sub)type of `System`.
    '''

    systems = SubSection(sub_section=Link, repeats=True, description=(
        'All the links to sections that represent the members of this batch.'))


def create_archive(entry_dict, context, file_name):
    if not context.raw_path_exists(file_name):
        with context.raw_file(file_name, 'w') as outfile:
            json.dump(entry_dict, outfile)
        context.process_updated_raw_file(file_name)


class SampleCut(EntryData, Activity):
    ''' An Activity that can be used for cutting a sample in multiple ones. '''

    number_of_samples = Quantity(
        type=int,
        description='The number of samples generated from this "Sample Cut" Task.',
        a_eln=dict(component='NumberEditQuantity'))
    input_sample = SubSection(sub_section=Link, repeats=True, description=(
        'All the links to sections that represent the inputs for this task.'))
    output_samples = SubSection(sub_section=Link, repeats=True, description=(
        'All the links to sections that represent the outputs for this task.'))

    def normalize(self, archive, logger):
        super(SampleCut, self).normalize(archive, logger)

        if self.inputs:
            if len(self.inputs) != 1:
                logger.warn(f"Error in '{self.name}': Only one input expected, but {len(self.inputs)} inputs given.")
            if self.output_samples:
                logger.warn(f"Error in '{self.name}': No output samples expected,"
                            f" but {len(self.output_samples)} output samples given.")
            if not self.number_of_samples:
                logger.warn(f"Error in '{self.name}': 'number_of_samples' expected, but None found.")
            if not (SampleID in attr for attr in self.inputs[0].section.m_proxy_type.resolve(self.inputs[0].section).__dict__.values()):
                logger.warn(f"Error in '{self.inputs[0].name}': 'SampleID' class expected, but None found.")
            for attribute in self.inputs[0].section.m_proxy_type.resolve(self.inputs[0].section).__dict__.values():
                if isinstance(attribute, SampleID):
                    parent_attribute = attribute
                    if not parent_attribute.sample_short_name:
                        logger.warn(f"Error in '{self.inputs[0].name}': 'sample_short_name' expected, but None found.")

            _, upload_id, mainfile, _, _ = parse_path(self.inputs[0].section.m_proxy_value)
            if '.data.archive.yaml' in mainfile:
                pass
            else:
                parent = self.m_context.load_archive(mainfile, upload_id, None)
                mainfile = parent.metadata.entry_name

            parent_object: Section = self.inputs[0].section
            collection = CollectionOfSystems()
            from nomad.datamodel import EntryArchive, EntryMetadata
            for sample_index in range(self.number_of_samples):
                children_name = f"{mainfile.split('.data.archive.yaml')[0]}_{sample_index}"
                children_object = parent_object.m_copy(deep=True)
                for attribute in children_object.__dict__.values():
                    if isinstance(attribute, SampleID):
                        attribute.sample_short_name = f'{parent_attribute.sample_short_name}_{sample_index}'
                        attribute.sample_id = None
                children_object.lab_id = None
                # children_object.results.eln.lab_ids = []
                filename = f"{children_name}.data.archive.yaml"
                create_archive(EntryArchive(data=children_object).m_to_dict(), self.m_context, filename)
                collection.systems.append(Link(section=f"../upload/raw/{filename}#data",
                                          name=children_name))

            collection_filename = f"{mainfile.split('.data.archive.yaml')[0]}_collection.data.archive.yaml"
            create_archive(EntryArchive(metadata=EntryMetadata(entry_type=CollectionOfSystems),
                           data=collection).m_to_dict(), self.m_context, collection_filename)
            self.output_samples = []
            self.output_samples.append(Link(section=f"../upload/raw/{collection_filename}#data",
                                            name=collection_filename.split('.data.archive.yaml')[0]))


m_package.__init_metainfo__()
