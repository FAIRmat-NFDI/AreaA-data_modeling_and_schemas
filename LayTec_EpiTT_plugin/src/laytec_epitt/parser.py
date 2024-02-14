#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import re
import json
import yaml
import pandas as pd
from datetime import datetime

from nomad.utils import hash
from nomad.datamodel import EntryArchive
from nomad.metainfo import Quantity, Section
from nomad.parsing import MatchingParser
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
)
from nomad.datamodel.data import (
    EntryData,
)
from nomad.datamodel.datamodel import EntryArchive, EntryMetadata

from nomad_measurements import ProcessReference
from laytec_epitt.schema import (
    LayTecEpiTTMeasurement,
    IKZLayTecEpiTTCategory,
    ReflectanceWavelengthTransient,
    LayTecEpiTTMeasurementResult,
    MeasurementSettings,
)


def create_archive(
    entry_dict, context, file_name, file_type, logger, *, bypass_check: bool = False
):
    if not context.raw_path_exists(file_name) or bypass_check:
        with context.raw_file(file_name, "w") as outfile:
            if file_type == "json":
                json.dump(entry_dict, outfile)
            elif file_type == "yaml":
                yaml.dump(entry_dict, outfile)
        context.upload.process_updated_raw_file(file_name, allow_modify=True)
    else:
        logger.error(
            f"{file_name} archive file already exists."
            f"If you intend to reprocess the older archive file, remove the existing one and run reprocessing again."
        )


class RawFileLayTecEpiTT(EntryData):
    """
    Contains the raw file from LayTecEpiTT in situ monitoring
    """

    m_def = Section(categories=[IKZLayTecEpiTTCategory])
    measurement = Quantity(
        type=LayTecEpiTTMeasurement,
        a_eln=ELNAnnotation(
            component="ReferenceEditQuantity",
        ),
    )


class EpiTTParser(MatchingParser):
    def __init__(self):
        super().__init__(
            name="NOMAD LayTec EpiTT schema and parser plugin",
            code_name="EpiTT Parser",  #'HZB Unold Lab Parser',
            code_homepage="https://github.com/FAIRmat-NFDI/AreaA-data_modeling_and_schemas",
            supported_compressions=["gz", "bz2", "xz"],
        )

    def parse(self, mainfile: str, archive: EntryArchive, logger) -> None:
        data_file = mainfile.split("/")[-1]
        data_file_with_path = mainfile.split("raw/")[-1]
        measurement_data = LayTecEpiTTMeasurement()
        measurement_data.measurement_settings = MeasurementSettings()
        # .m_from_dict(LayTecEpiTTMeasurement.m_def.a_template)
        measurement_data.data_file = data_file_with_path

        def parse_epitt_data(file):
            line = file.readline().strip()
            parameters = {}
            header = []
            while (
                line.startswith(
                    (
                        "##",
                        "!",
                    )
                )
                or line.strip() == ""
            ):
                match = re.match(r"##(\w+)\s*=\s*(.*)", line.strip())
                if match:
                    parameter_name = match.group(1)
                    parameter_value = match.group(2)
                    if parameter_name == "YUNITS":
                        yunits = parameter_value.split("\t")
                        parameters[parameter_name] = yunits
                    else:
                        parameters[parameter_name] = parameter_value
                line = file.readline().strip()
            header = line.split("\t")
            data_in_df = pd.read_csv(file, sep="\t", names=header, skipfooter=1)
            return parameters, data_in_df

        if measurement_data.data_file:
            with archive.m_context.raw_file(data_file_with_path) as file:
                epitt_data = parse_epitt_data(file)
                name_string = ""
                paramters_for_name = [
                    "RUN_ID",
                    "RUNTYPE_ID",
                    "RUNTYPE_NAME",
                    "MODULE_NAME",
                    "WAFER_LABEL",
                    "WAFER",
                ]
                for p in paramters_for_name:
                    if p in epitt_data[0].keys():
                        name_string += "_" + epitt_data[0][p]
                if name_string != "":
                    measurement_data.name = name_string[1:]
                    measurement_data.lab_id = name_string[1:]
                if "TIME" in epitt_data[0].keys():
                    measurement_data.datetime = datetime.strptime(
                        epitt_data[0]["TIME"], "%Y-%m-%d-%H-%M-%S"
                    )  #'2020-08-27-11-11-30',
                measurement_data.measurement_settings = MeasurementSettings()  # ?
                if "MODULE_NAME" in epitt_data[0].keys():
                    measurement_data.measurement_settings.module_name = epitt_data[0][
                        "MODULE_NAME"
                    ]
                if "WAFER_LABEL" in epitt_data[0].keys():
                    measurement_data.measurement_settings.wafer_label = epitt_data[0][
                        "WAFER_LABEL"
                    ]
                if "WAFER_ZONE" in epitt_data[0].keys():
                    measurement_data.measurement_settings.wafer_zone = epitt_data[0][
                        "WAFER_ZONE"
                    ]
                if "WAFER" in epitt_data[0].keys():
                    measurement_data.measurement_settings.wafer = epitt_data[0]["WAFER"]
                # if "RUN_ID" in epitt_data[0].keys():
                #    self.run_ID = epitt_data[0]["RUN_ID"]
                if "RUNTYPE_ID" in epitt_data[0].keys():
                    measurement_data.measurement_settings.runtype_ID = epitt_data[0][
                        "RUNTYPE_ID"
                    ]
                if "RUNTYPE_NAME" in epitt_data[0].keys():
                    measurement_data.measurement_settings.runtype_name = epitt_data[0][
                        "RUNTYPE_NAME"
                    ]
                # measurement_data.time_transient = epitt_data[1]["BEGIN"]
                process = ProcessReference()
                process.lab_id = epitt_data[0]["RUN_ID"]
                process.normalize(archive, logger)
                measurement_data.process = process
                results = LayTecEpiTTMeasurementResult()
                results.process_time = epitt_data[1]["BEGIN"]
                results.pyrometer_temperature = epitt_data[1]["PyroTemp"]
                results.reflectance_wavelengths = []
                for wl, datacolname in zip(
                    ["REFLEC_WAVELENGTH", "PYRO_WAVELENGTH", "WHITE_WAVELENGTH"],
                    ["DetReflec", "RLo", "DetWhite"],
                ):
                    if wl in epitt_data[0].keys():
                        spectrum = epitt_data[1][datacolname]
                        transient_object = ReflectanceWavelengthTransient()
                        transient_object.wavelength = int(
                            round(float(epitt_data[0][wl]))
                        )  # * ureg("nanometer") #float(epitt_data[0][wl])* ureg('nanometer')
                        transient_object.wavelength_name = wl
                        transient_object.raw_intensity = spectrum / spectrum[0]
                        # smoothed_intesity is processed in the normalizer
                        results.reflectance_wavelengths.append(transient_object)
                measurement_data.results = [results]
            filetype = "yaml"
            filename = f"{data_file[:-4]}_measurement.archive.{filetype}"
            measurement_archive = EntryArchive(
                data=measurement_data,
                m_context=archive.m_context,
                metadata=EntryMetadata(upload_id=archive.m_context.upload_id),
            )
            create_archive(
                measurement_archive.m_to_dict(),
                archive.m_context,
                filename,
                filetype,
                logger,
            )
        archive.data = RawFileLayTecEpiTT(
            measurement=f"../uploads/{archive.m_context.upload_id}/archive/{hash(archive.m_context.upload_id, filename)}#data"
        )
        archive.metadata.entry_name = data_file + " in situ measurement file"
