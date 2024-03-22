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
from io import StringIO
import numpy as np
import pandas as pd
from datetime import datetime

from structlog.stdlib import (
    BoundLogger,
)
#from PPMS.schema import PPMSMeasurement, PPMSData, Sample, ChannelData, ETOData

from nomad.units import ureg

from nomad.metainfo import Package, Section, MEnum, SubSection

from nomad.datamodel.metainfo.basesections import Measurement

from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    SectionProperties,
)
from nomad.datamodel.data import (
    EntryData,
)
from nomad.datamodel.data import (
    ArchiveSection,
)

from nomad.metainfo import (
    Package,
    Quantity,
)

from nomad.datamodel.metainfo.eln import (
    CompositeSystem,
)

from nomad.datamodel.metainfo.plot import PlotSection, PlotlyFigure

from nomad.datamodel.metainfo.basesections import ActivityStep

from cpfs_basesections.cpfs_schemes import (
    CPFSCrystal,
)

from nomad.search import search

from ppms.schema import (
    Sample,
    PPMSMeasurement,
)

from ppms.ppmsdatastruct import (
    PPMSData,
)

from time import (
    sleep,
    perf_counter
)

m_package = Package(name='cpfs_ppms')


class CPFSSample(Sample):
    sample_id = Quantity(
        type=CPFSCrystal,
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        )
    )
    width = Quantity(
        type=np.float64,
        unit='meter',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='millimeter'
        ),
    )
    length = Quantity(
        type=np.float64,
        unit='meter',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='millimeter'
        ),
    )
    depth = Quantity(
        type=np.float64,
        unit='meter',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='millimeter'
        ),
    )

class CPFSETOSymmetrizedData(PPMSData):
    field = Quantity(
        type=np.dtype(np.float64),
        unit='gauss',
        shape=['*'],
        description='FILL')
    rho_xx_up = Quantity(
        type=np.dtype(np.float64),
        unit='ohm*meter',
        shape=['*'],
        description='FILL')
    rho_xx_down = Quantity(
        type=np.dtype(np.float64),
        unit='ohm*meter',
        shape=['*'],
        description='FILL')
    mr_up = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit='dimensionless',
        description='FILL')
    mr_down = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit='dimensionless',
        description='FILL')
    rho_xy_up = Quantity(
        type=np.dtype(np.float64),
        unit='ohm*meter',
        shape=['*'],
        description='FILL')
    rho_xy_down = Quantity(
        type=np.dtype(np.float64),
        unit='ohm*meter',
        shape=['*'],
        description='FILL')

class CPFSETOAnalyzedData(PPMSData):
    field = Quantity(
        type=np.dtype(np.float64),
        unit='gauss',
        shape=['*'],
        description='FILL')
    rho_xx_up = Quantity(
        type=np.dtype(np.float64),
        unit='ohm*meter',
        shape=['*'],
        description='FILL')
    rho_xx_down = Quantity(
        type=np.dtype(np.float64),
        unit='ohm*meter',
        shape=['*'],
        description='FILL')
    sigma_xx_up = Quantity(
        type=np.dtype(np.float64),
        unit='siemens/m',
        shape=['*'],
        description='FILL')
    sigma_xx_down = Quantity(
        type=np.dtype(np.float64),
        unit='siemens/m',
        shape=['*'],
        description='FILL')
    rho_ohe_up = Quantity(
        type=np.dtype(np.float64),
        unit='ohm*meter',
        shape=['*'],
        description='FILL')
    rho_ohe_down = Quantity(
        type=np.dtype(np.float64),
        unit='ohm*meter',
        shape=['*'],
        description='FILL')
    rho_ahe_up = Quantity(
        type=np.dtype(np.float64),
        unit='ohm*meter',
        shape=['*'],
        description='FILL')
    rho_ahe_down = Quantity(
        type=np.dtype(np.float64),
        unit='ohm*meter',
        shape=['*'],
        description='FILL')
    sigma_ahe_up = Quantity(
        type=np.dtype(np.float64),
        unit='siemens/m',
        shape=['*'],
        description='FILL')
    sigma_ahe_down = Quantity(
        type=np.dtype(np.float64),
        unit='siemens/m',
        shape=['*'],
        description='FILL')
    carrier_concentration = Quantity(
        type=np.dtype(np.float64),
        unit='1/meter**3',
        description='FILL')
    carrier_mobility = Quantity(
        type=np.dtype(np.float64),
        unit='meter**2/volt/second',
        description='FILL')

class CPFSPPMSMeasurement(PPMSMeasurement,EntryData):

    # m_def = Section(
    #     a_eln=dict(lane_width='600px'),
    #     a_plot={"plotly_graph_object": {
    #             "data": {
    #             "x": "#data/temperature",
    #             "y": "#data/field",
    #             },
    #         }
    # },
    # )
    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                   'name',
                   'datetime',
                   'data_file',
                   'sequence_file',
                   'description',
                   'software',
                   'startupaxis',
               ],
            ),
            lane_width='600px',
            ),
    )

    symmetrized_data = SubSection(
        section_def = CPFSETOSymmetrizedData,
        repeats = True,
    )

    analyzed_data = SubSection(
        section_def = CPFSETOAnalyzedData,
        repeats = True,
    )

    channel_measurement_type = Quantity(
        type=MEnum(
            'TMR',
            'Hall',
            'undefined',
        ),
        shape=['*'],
        a_eln=ELNAnnotation(
            component='EnumEditQuantity',
        ),
    )

    def normalize(self, archive, logger: BoundLogger) -> None:

        super(CPFSPPMSMeasurement, self).normalize(archive, logger)

        with archive.m_context.raw_file(self.data_file, 'r') as file:
            data = file.read()

        header_match = re.search(r'\[Header\](.*?)\[Data\]', data, re.DOTALL)
        header_section = header_match.group(1).strip()
        header_lines = header_section.split('\n')

        while self.samples:
            self.m_remove_sub_section(CPFSPPMSMeasurement.samples, 0)

        for i in ["1","2"]:

            sample_headers = [line for line in header_lines if line.startswith("INFO") and 'SAMPLE'+i+'_' in line]
            if sample_headers:
                sample = CPFSSample()
                for line in sample_headers:
                    parts = re.split(r',\s*', line)
                    key = parts[-1].lower().replace('sample'+i+'_','')
                    if key=="material":
                        for line in parts[1:-1]:
                            if line.startswith("l="):
                                setattr(sample,"length",float(line.strip("l=").strip("mm"))/1000.)
                            if line.startswith("w="):
                                setattr(sample,"width",float(line.strip("w=").strip("mm"))/1000.)
                            if line.startswith("t="):
                                setattr(sample,"depth",float(line.strip("t=").strip("mm"))/1000.)
                    if key=="comment":
                        setattr(sample, key, ", ".join(parts[1:-1]))
                        #ids="_".join(parts[1].split("_")[1:3])
                        ids=parts[1].split("_")[1]
                        logger.info(ids)
                        search_result = search(
                            owner="user",
                            query={
                                "results.eln.sections:any": ["CPFSCrystal"],
                                "results.eln.names:any": [ids+r'*']
                            },
                            user_id=archive.metadata.main_author.user_id,
                            )
                        if len(search_result.data)>0:
                            sample.sample_id=f"../uploads/{search_result.data[0]['upload_id']}/archive/{search_result.data[0]['entry_id']}#data"
                            sample.name=search_result.data[0]['search_quantities'][0]['str_value']
                        else:
                            logger.warning("The sample given in the header could not be found and couldn't be referenced.")
                    elif hasattr(sample, key):
                        setattr(sample, key, ", ".join(parts[1:-1]))
                if not sample.length:
                    logger.info("Length for sample "+str(i)+" not found, set to 1. Value of resistivity will be wrong.")
                    setattr(sample,"length",1.)
                if not sample.width:
                    logger.info("Width for sample "+str(i)+" not found, set to 1. Value of resistivity will be wrong.")
                    setattr(sample,"width",1.)
                if not sample.depth:
                    logger.info("Depth for sample "+str(i)+" not found, set to 1. Value of resistivity will be wrong.")
                    setattr(sample,"depth",1.)
                self.m_add_sub_section(CPFSPPMSMeasurement.samples, sample)

        # sample2_headers = [line for line in header_lines if line.startswith("INFO") and 'SAMPLE2_' in line]
        # if sample2_headers:
        #     sample_2 = CPFSSample()
        #     for line in sample2_headers:
        #         parts = re.split(r',\s*', line)
        #         key = parts[-1].lower().replace('sample2_','')
        #         if key=="sample_id":
        #             search_result = search(
        #                 owner="user",
        #                 query={
        #                     "results.eln.sections:any": ["CPFSCrystal"],
        #                     "results.eln.names:any": [parts[1]+r'*']
        #                 },
        #                 user_id=archive.metadata.main_author.user_id,
        #                 )
        #             if len(search_result.data)>0:
        #                 sample_2.sample_id=f"../uploads/{search_result.data[0]['upload_id']}/archive/{search_result.data[0]['entry_id']}#data"
        #                 sample_2.name=search_result.data[0]['search_quantities'][0]['str_value']
        #             else:
        #                 logger.warning("The sample given in the header could not be found and couldn't be referenced.")
        #         elif hasattr(sample_2, key):
        #             setattr(sample_2, key, ", ".join(parts[1:-1]))

        # self.m_add_sub_section(CPFSPPMSMeasurement.samples, sample_1)
        # self.m_add_sub_section(CPFSPPMSMeasurement.samples, sample_2)

        #find measurement modes, for now coming from sample.comment
        modelist=[]
        for channel in ["Ch1_","Ch2_"]:
            if channel+"TMR" in self.samples[0].comment:
                modelist.append("TMR")
            elif channel+"Hall" in self.samples[0].comment:
                modelist.append("Hall")
            else:
                modelist.append("undefined")
        self.channel_measurement_type=modelist

        if self.software.startswith("Electrical Transport Option"):
            #Try to symmetrize data for each measurement
            maxfield=90000*ureg("gauss")
            data_symmetrized = []
            for mdata in self.data:
                #For now only for field sweeps
                if not mdata.name.startswith("Field sweep"):
                    continue
                sym_data=CPFSETOSymmetrizedData()
                sym_data.name=mdata.name
                sym_data.title=mdata.name
                fitlength=len(mdata.magnetic_field)/4
                fitlength-=fitlength % -100
                fitlength+=1
                fitfield=np.linspace(-maxfield,maxfield,int(fitlength))
                sym_data.field=fitfield
                for channel in [0,1]:
                    field=mdata.magnetic_field[np.invert(pd.isnull(mdata.channels[channel].resistance))]
                    res=mdata.channels[channel].resistance[np.invert(pd.isnull(mdata.channels[channel].resistance))]
                    #Check if field sweeps down and up:
                    downsweep=[]
                    upsweep=[]
                    for i in range(len(field)):
                        if abs(field[i]-maxfield)<self.field_tolerance:
                            if len(downsweep)==0:
                                downsweep.append(i) #downsweep started
                            if len(upsweep)==1:
                                upsweep.append(i) # upsweep finished
                        if abs(field[i]+maxfield)<self.field_tolerance:
                            if len(downsweep)==1:
                                downsweep.append(i) #downsweep finished
                            if len(upsweep)==0:
                                upsweep.append(i) # upsweep started
                    if len(upsweep)!=2 or len(downsweep)!=2:
                        logger.warning("Measurement "+mdata.name+" did not contain up- and downsweep in field.")
                        continue
                    downfit=np.interp(fitfield,np.flip(field[downsweep[0]:downsweep[1]]),np.flip(res[downsweep[0]:downsweep[1]]))
                    upfit=np.interp(fitfield,field[upsweep[0]:upsweep[1]],res[upsweep[0]:upsweep[1]])
                    if self.channel_measurement_type[channel]=="Hall":
                        intermediate=(upfit+np.flip(downfit))/2.
                        sym_data.rho_xy_down=(downfit-np.flip(intermediate))*self.samples[channel].depth
                        sym_data.rho_xy_up=(upfit-intermediate)*self.samples[channel].depth
                    if self.channel_measurement_type[channel]=="TMR":
                        intermediate=(np.flip(downfit)-upfit)/2.
                        sym_data.rho_xx_down=(downfit+np.flip(intermediate))*self.samples[channel].depth*self.samples[channel].width/self.samples[channel].length
                        sym_data.rho_xx_up=(upfit-intermediate)*self.samples[channel].depth*self.samples[channel].width/self.samples[channel].length
                        sym_data.mr_down=(sym_data.rho_xx_down-sym_data.rho_xx_down[int(fitlength/2)])/sym_data.rho_xx_down[int(fitlength/2)]
                        sym_data.mr_up=(sym_data.rho_xx_up-sym_data.rho_xx_up[int(fitlength/2)])/sym_data.rho_xx_up[int(fitlength/2)]
                data_symmetrized.append(sym_data)


                #create symmetrized output files
                filename="symmetrized_data_"+"_".join(sym_data.name.split())+"_"+self.data_file.strip(".dat")
                with archive.m_context.raw_file(filename, 'w') as outfile:
                    outfile.write("#Field (Oe)     rho_xx_up       rho_xx_down      mr_up           mr_down         rho_xy_up       rho_xy_down      \n")
                    for i in range(int(fitlength)):
                        outfile.write("{0:16.8e}".format(fitfield[i].magnitude))
                        if sym_data.rho_xx_up is not None:
                            outfile.write("{0:16.8e}".format(sym_data.rho_xx_up[i].magnitude))
                        else:
                            outfile.write("NaN             ")
                        if sym_data.rho_xx_down is not None:
                            outfile.write("{0:16.8e}".format(sym_data.rho_xx_down[i].magnitude))
                        else:
                            outfile.write("NaN             ")
                        if sym_data.mr_up is not None:
                            outfile.write("{0:16.8e}".format(sym_data.mr_up[i].magnitude))
                        else:
                            outfile.write("NaN             ")
                        if sym_data.mr_down is not None:
                            outfile.write("{0:16.8e}".format(sym_data.mr_down[i].magnitude))
                        else:
                            outfile.write("NaN             ")
                        if sym_data.rho_xy_up is not None:
                            outfile.write("{0:16.8e}".format(sym_data.rho_xy_up[i].magnitude))
                        else:
                            outfile.write("NaN             ")
                        if sym_data.rho_xy_down is not None:
                            outfile.write("{0:16.8e}".format(sym_data.rho_xy_down[i].magnitude))
                        else:
                            outfile.write("NaN             ")
                        outfile.write("\n")


            self.symmetrized_data=data_symmetrized

            #Analyze data: split in ordinary and anomalous, calculate conductivities
            cutofffield=50000*ureg("gauss")
            data_analyzed = []
            for data in self.symmetrized_data:
                ana_data=CPFSETOAnalyzedData()
                ana_data.name=data.name
                ana_data.title=data.name
                ana_data.field=data.field
                ana_data.rho_xx_up=data.rho_xx_up
                ana_data.rho_xx_down=data.rho_xx_down
                ana_data.sigma_xx_up=1./data.rho_xx_up
                ana_data.sigma_xx_down=1./data.rho_xx_down

                fitstart=int(len(data.field)*(180000-cutofffield.magnitude)/180000)
                rho_xy_up_fit=np.poly1d([np.polyfit(data.field[fitstart:].magnitude,data.rho_xy_up[fitstart:].magnitude,1)[0],0])*data.rho_xy_up.units
                rho_xy_down_fit=np.poly1d([np.polyfit(data.field[fitstart:].magnitude,data.rho_xy_down[fitstart:].magnitude,1)[0],0])*data.rho_xy_down.units
                ana_data.rho_ohe_up=rho_xy_up_fit(ana_data.field.magnitude)
                ana_data.rho_ohe_down=rho_xy_down_fit(ana_data.field.magnitude)
                ana_data.rho_ahe_up=data.rho_xy_up-ana_data.rho_ohe_up
                ana_data.rho_ahe_down=data.rho_xy_down-ana_data.rho_ohe_down
                ana_data.sigma_ahe_up=ana_data.rho_ahe_up/(ana_data.rho_ahe_up**2+data.rho_xx_up**2)
                ana_data.sigma_ahe_down=ana_data.rho_ahe_down/(ana_data.rho_ahe_down**2+data.rho_xx_down**2)

                #ana_data.carrier_concentration=1/(rho_xy)

                data_analyzed.append(ana_data)

            self.analyzed_data=data_analyzed

            #Now create the according plots
            import plotly.express as px
            import plotly.graph_objs as go
            from plotly.subplots import make_subplots
            #self.figures=[]

            #Symmetrized plots
            figure1 = make_subplots(rows=1, cols=1, subplot_titles=(["TMR"]))
            figure2 = make_subplots(rows=1, cols=1, subplot_titles=(["MR"]))
            figure3 = make_subplots(rows=1, cols=1, subplot_titles=(["Hall"]))
            for data in self.symmetrized_data:
                color=int(255./len(self.symmetrized_data)*self.symmetrized_data.index(data))
                if data.rho_xx_up is not None and data.rho_xx_down is not None:
                    resistivity_tmr_up=go.Scatter(x=np.concatenate((data.field,np.flip(data.field))),y=np.concatenate((data.rho_xx_up,np.flip(data.rho_xx_down))), name=data.title.split("at")[1].strip("."), marker_color='rgb({},0,255)'.format(color),showlegend=True)
                    figure1.add_trace(resistivity_tmr_up, row=1, col=1)
                if data.mr_up is not None and data.mr_down is not None:
                    resistivity_mr_up=go.Scatter(x=np.concatenate((data.field,np.flip(data.field))),y=np.concatenate((data.mr_up,np.flip(data.mr_down))), name=data.title.split("at")[1].strip("."), marker_color='rgb({},0,255)'.format(color),showlegend=True)
                    figure2.add_trace(resistivity_mr_up, row=1, col=1)
                if data.rho_xy_up is not None:
                    resistivity_hall_up=go.Scatter(x=np.concatenate((data.field,np.flip(data.field))),y=np.concatenate((data.rho_xy_up,np.flip(data.rho_xy_down))), name=data.title.split("at")[1].strip("."), marker_color='rgb({},0,255)'.format(color),showlegend=True)
                    figure3.add_trace(resistivity_hall_up, row=1, col=1)
            figure1.update_layout(height=400, width=716,showlegend=True)
            figure2.update_layout(height=400, width=716,showlegend=True)
            figure3.update_layout(height=400, width=716,showlegend=True)
            self.figures.append(PlotlyFigure(label="TMR", figure=figure1.to_plotly_json()))
            self.figures.append(PlotlyFigure(label="MR", figure=figure2.to_plotly_json()))
            self.figures.append(PlotlyFigure(label="Hall", figure=figure3.to_plotly_json()))

            #Analyzed plots
            figure1 = make_subplots(rows=1, cols=1, subplot_titles=(["OHR"]))
            figure2 = make_subplots(rows=1, cols=1, subplot_titles=(["AHR"]))
            figure3 = make_subplots(rows=1, cols=1, subplot_titles=(["AHC"]))
            for data in self.analyzed_data:
                color=int(255./len(self.analyzed_data)*self.analyzed_data.index(data))
                if data.rho_ohe_up is not None and data.rho_ohe_down is not None:
                    resistivity_tmr_up=go.Scatter(x=np.concatenate((data.field,np.flip(data.field))),y=np.concatenate((data.rho_ohe_up,np.flip(data.rho_ohe_down))), name=data.title.split("at")[1].strip("."), marker_color='rgb({},0,255)'.format(color),showlegend=True)
                    figure1.add_trace(resistivity_tmr_up, row=1, col=1)
                if data.rho_ahe_up is not None and data.rho_ahe_down is not None:
                    resistivity_mr_up=go.Scatter(x=np.concatenate((data.field,np.flip(data.field))),y=np.concatenate((data.rho_ahe_up,np.flip(data.rho_ahe_down))), name=data.title.split("at")[1].strip("."), marker_color='rgb({},0,255)'.format(color),showlegend=True)
                    figure2.add_trace(resistivity_mr_up, row=1, col=1)
                if data.sigma_ahe_up is not None and data.sigma_ahe_down is not None:
                    resistivity_hall_up=go.Scatter(x=np.concatenate((data.field,np.flip(data.field))),y=np.concatenate((data.sigma_ahe_up,np.flip(data.sigma_ahe_down))), name=data.title.split("at")[1].strip("."), marker_color='rgb({},0,255)'.format(color),showlegend=True)
                    figure3.add_trace(resistivity_hall_up, row=1, col=1)
            figure1.update_layout(height=400, width=716,showlegend=True)
            figure2.update_layout(height=400, width=716,showlegend=True)
            figure3.update_layout(height=400, width=716,showlegend=True)
            self.figures.append(PlotlyFigure(label="OHR", figure=figure1.to_plotly_json()))
            self.figures.append(PlotlyFigure(label="AHR", figure=figure2.to_plotly_json()))
            self.figures.append(PlotlyFigure(label="AHC", figure=figure3.to_plotly_json()))





m_package.__init_metainfo__()