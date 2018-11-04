"""
Simulator.py
"""
# Copyright (c) 2018 Teledyne LeCroy, Inc.
# All rights reserved worldwide.
#
# This file is part of SignalIntegrity.
#
# SignalIntegrity is free software: You can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>

import sys
if sys.version_info.major < 3:
    from Tkinter import Toplevel,Frame,PhotoImage,Menu,Button
    from Tkinter import TOP,NO,RAISED,LEFT,X,NONE,BOTH
    import tkMessageBox
else:
    from tkinter import Toplevel,Frame,PhotoImage,Menu,Button
    from tkinter import TOP,NO,RAISED,LEFT,X,NONE,BOTH
    from tkinter import messagebox

from SignalIntegrity.App.PartProperty import PartPropertyPartName,PartPropertyReferenceDesignator,PartPropertyVoltageOffset
from SignalIntegrity.App.PartProperty import PartPropertyTransresistance,PartPropertyVoltageGain,PartPropertyDelay
from SignalIntegrity.App.SParameterViewerWindow import SParametersDialog
from SignalIntegrity.App.MenuSystemHelpers import Doer
from SignalIntegrity.App.ProgressDialog import ProgressDialog
from SignalIntegrity.App.FilePicker import AskSaveAsFilename
from SignalIntegrity.App.ToSI import FromSI,ToSI

import matplotlib

import sys
import os


if not 'matplotlib.backends' in sys.modules:
    matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import platform
if platform.system() == 'Linux':
    if sys.version_info.major < 3:
        from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
    else:
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
else:
    from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

from matplotlib.figure import Figure

class SimulatorDialog(Toplevel):
    def __init__(self, parent):
        Toplevel.__init__(self, parent.parent)
        self.parent=parent
        self.withdraw()
        self.title('Simulation')
        img = PhotoImage(file=self.parent.parent.installdir+'/icons/png/AppIcon2.gif')
        self.tk.call('wm', 'iconphoto', self._w, img)
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        # the Doers - the holder of the commands, menu elements, toolbar elements, and key bindings
        self.WaveformSaveDoer = Doer(self.onWriteSimulatorToFile).AddHelpElement(self.parent.parent.helpSystemKeys['Control-Help:Save-Waveforms'])
        # TODO: someday allow waveform reading
        self.WaveformReadDoer = Doer(self.onReadSimulatorFromFile).AddHelpElement(self.parent.parent.helpSystemKeys['Control-Help:Read-Waveforms']).Activate(False)
        self.Matplotlib2tikzDoer = Doer(self.onMatplotlib2TikZ).AddHelpElement(self.parent.parent.helpSystemKeys['Control-Help:Output-to-LaTeX'])
        # ------
        self.CalculationPropertiesDoer = Doer(self.onCalculationProperties).AddHelpElement(self.parent.parent.helpSystemKeys['Control-Help:Calculation-Properties'])
        self.ExamineTransferMatricesDoer = Doer(self.onExamineTransferMatrices).AddHelpElement(self.parent.parent.helpSystemKeys['Control-Help:View-Transfer-Parameters'])
        self.SimulateDoer = Doer(self.parent.parent.onCalculate).AddHelpElement(self.parent.parent.helpSystemKeys['Control-Help:Recalculate'])
        # ------
        self.HelpDoer = Doer(self.onHelp).AddHelpElement(self.parent.parent.helpSystemKeys['Control-Help:Open-Help-File'])
        self.ControlHelpDoer = Doer(self.onControlHelp).AddHelpElement(self.parent.parent.helpSystemKeys['Control-Help:Control-Help'])
        # ------
        self.EscapeDoer = Doer(self.onEscape).AddKeyBindElement(self,'<Escape>').DisableHelp()

        # The menu system
        TheMenu=Menu(self)
        self.config(menu=TheMenu)
        FileMenu=Menu(self)
        TheMenu.add_cascade(label='File',menu=FileMenu,underline=0)
        self.WaveformSaveDoer.AddMenuElement(FileMenu,label="Save Waveforms",underline=0)
        self.WaveformReadDoer.AddMenuElement(FileMenu,label="Read Waveforms",underline=0)
        FileMenu.add_separator()
        self.Matplotlib2tikzDoer.AddMenuElement(FileMenu,label='Output to LaTeX (TikZ)',underline=10)
        # ------
        CalcMenu=Menu(self)
        TheMenu.add_cascade(label='Calculate',menu=CalcMenu,underline=0)
        self.CalculationPropertiesDoer.AddMenuElement(CalcMenu,label='Calculation Properties',underline=12)
        self.ExamineTransferMatricesDoer.AddMenuElement(CalcMenu,label='View Transfer Parameters',underline=0)
        CalcMenu.add_separator()
        self.SimulateDoer.AddMenuElement(CalcMenu,label='Recalculate',underline=0)
        # ------
        HelpMenu=Menu(self)
        TheMenu.add_cascade(label='Help',menu=HelpMenu,underline=0)
        self.HelpDoer.AddMenuElement(HelpMenu,label='Open Help File',underline=0)
        self.ControlHelpDoer.AddMenuElement(HelpMenu,label='Control Help',underline=0)

        # The Toolbar
        ToolBarFrame = Frame(self)
        ToolBarFrame.pack(side=TOP,fill=X,expand=NO)
        self.WaveformReadDoer.AddToolBarElement(ToolBarFrame,iconfile=self.parent.parent.installdir+'/icons/png/16x16/actions/document-open-2.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        self.WaveformSaveDoer.AddToolBarElement(ToolBarFrame,iconfile=self.parent.parent.installdir+'/icons/png/16x16/actions/document-save-2.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        Frame(self,height=2,bd=2,relief=RAISED).pack(side=LEFT,fill=X,padx=5,pady=5)
        self.CalculationPropertiesDoer.AddToolBarElement(ToolBarFrame,iconfile=self.parent.parent.installdir+'/icons/png/16x16/actions/tooloptions.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        self.SimulateDoer.AddToolBarElement(ToolBarFrame,iconfile=self.parent.parent.installdir+'/icons/png/16x16/actions/system-run-3.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        Frame(ToolBarFrame,height=2,bd=2,relief=RAISED).pack(side=LEFT,fill=X,padx=5,pady=5)
        self.HelpDoer.AddToolBarElement(ToolBarFrame,iconfile=self.parent.parent.installdir+'/icons/png/16x16/actions/help-contents-5.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        self.ControlHelpDoer.AddToolBarElement(ToolBarFrame,iconfile=self.parent.parent.installdir+'/icons/png/16x16/actions/help-3.gif').Pack(side=LEFT,fill=NONE,expand=NO)

        self.f = Figure(figsize=(6,4), dpi=100)
        self.plt = self.f.add_subplot(111)
        self.plt.set_xlabel('time (ns)')
        self.plt.set_ylabel('amplitude')

        self.waveformList=None
        self.waveformNamesList=None
        self.canvas = FigureCanvasTkAgg(self.f, master=self)
        #canvas.show()
        self.canvas.get_tk_widget().pack(side=TOP, fill=X, expand=1)

        if platform.system() == 'Linux':
            if sys.version_info.major < 3:
                toolbar = NavigationToolbar2TkAgg( self.canvas, self )
            else:
                toolbar = NavigationToolbar2Tk( self.canvas, self )
        else:
            toolbar = NavigationToolbar2Tk( self.canvas, self )

        toolbar.update()
        self.canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

        controlsFrame = Frame(self)
        Button(controlsFrame,text='autoscale',command=self.onAutoscale).pack(side=LEFT,expand=NO,fill=X)
        controlsFrame.pack(side=TOP,fill=X,expand=NO)

        try:
            from matplotlib2tikz import save as tikz_save
        except:
            self.Matplotlib2tikzDoer.Activate(False)

        self.ExamineTransferMatricesDoer.Activate(False)
        self.SimulateDoer.Activate(False)

        self.geometry("%+d%+d" % (self.parent.parent.root.winfo_x()+self.parent.parent.root.winfo_width()/2-self.winfo_width()/2,
            self.parent.parent.root.winfo_y()+self.parent.parent.root.winfo_height()/2-self.winfo_height()/2))

    def onAutoscale(self):
        self.plt.autoscale(True)
        self.f.canvas.draw()

    def UpdateWaveforms(self,waveformList, waveformNamesList):
        self.lift(self.parent.parent)
        self.plt.cla()
        self.plt.set_ylabel('amplitude',fontsize=10)

        if not self.waveformList == None:
            self.plt.autoscale(False)

        self.waveformList=waveformList
        self.waveformNamesList=waveformNamesList

        mint=None
        maxt=None
        for wfi in range(len(self.waveformList)):
            wf=self.waveformList[wfi]
            wfTimes=wf.Times()
            if len(wfTimes)==0:
                continue
            wfValues=wf.Values()
            wfName=str(self.waveformNamesList[wfi])
            mint=wfTimes[0] if mint is None else max(mint,wfTimes[0])
            maxt=wfTimes[-1] if maxt is None else min(maxt,wfTimes[-1])

        timeLabel='s'
        timeLabelDivisor=1.
        if not self.waveformList is None:
            if (not mint is None) and (not maxt is None):
                durLabelTime=(maxt-mint)
                timeLabel=ToSI(durLabelTime,'s')[-2:]
                timeLabelDivisor=FromSI('1. '+timeLabel,'s')
                mint=mint/timeLabelDivisor
                maxt=maxt/timeLabelDivisor
            if not mint is None:
                self.plt.set_xlim(xmin=mint)
            if not maxt is None:
                self.plt.set_xlim(xmax=maxt)

        for wfi in range(len(self.waveformList)):
            wf=self.waveformList[wfi]
            wfTimes=wf.Times(timeLabelDivisor)
            if len(wfTimes)==0:
                continue
            wfValues=wf.Values()
            wfName=str(self.waveformNamesList[wfi])
            self.plt.plot(wfTimes,wfValues,label=wfName)

        self.plt.set_xlabel('time ('+timeLabel+')',fontsize=10)
        self.plt.legend(loc='upper right',labelspacing=0.1)
        self.f.canvas.draw()
        return self

    def onWriteSimulatorToFile(self):
        for wfi in range(len(self.waveformNamesList)):
            outputWaveformName=self.waveformNamesList[wfi]
            outputWaveform=self.waveformList[wfi]
            if self.parent.parent.fileparts.filename=='':
                filename=outputWaveformName
            else:
                filename=self.parent.parent.fileparts.filename+'_'+outputWaveformName
            filename=AskSaveAsFilename(parent=self,filetypes=[('waveform', '.txt')],
                            defaultextension='.txt',
                            initialdir=self.parent.parent.fileparts.AbsoluteFilePath(),
                            initialfile=filename+'.txt')
            if filename is None:
                continue
            outputWaveform.WriteToFile(filename)

    def onReadSimulatorFromFile(self):
        pass
    def onCalculationProperties(self):
        self.parent.parent.onCalculationProperties()
        #self.parent.parent.calculationProperties.CalculationPropertiesDialog().lift(self)

    def onExamineTransferMatrices(self):
        buttonLabelList=[[out+' due to '+inp for inp in self.parent.sourceNames] for out in self.parent.outputWaveformLabels]
        maxLength=len(max([item for sublist in buttonLabelList for item in sublist],key=len))
        buttonLabelList=[[item.ljust(maxLength) for item in sublist] for sublist in buttonLabelList]
        sp=self.parent.transferMatrices.SParameters()
        SParametersDialog(self.parent.parent,sp,
                          self.parent.parent.fileparts.FullFilePathExtension('s'+str(sp.m_P)+'p'),
                          'Transfer Parameters',buttonLabelList)

    def onMatplotlib2TikZ(self):
        filename=AskSaveAsFilename(parent=self,filetypes=[('tex', '.tex')],
                                   defaultextension='.tex',
                                   initialdir=self.parent.parent.fileparts.AbsoluteFilePath(),
                                   initialfile=self.parent.parent.fileparts.filename+'Waveforms.tex')
        if filename is None:
            return
        try:
            from matplotlib2tikz import save as tikz_save
            tikz_save(filename,figure=self.f,show_info=False,float_format='%.6g')
            texfile=open(filename,'rU')
            lines=[]
            for line in texfile:
                line=line.replace('\xe2\x88\x92','-')
                lines.append(str(line))
            texfile.close()
            texfile=open(filename,'w')
            for line in lines:
                texfile.write(line)
            texfile.close()
        except:
            if sys.version_info.major < 3:
                tkMessageBox.showerror('Export LaTeX','LaTeX could not be generated or written ')
            else:
                messagebox.showerror('Export LaTeX','LaTeX could not be generated or written ')
    def onHelp(self):
        import webbrowser
        helpfile=self.parent.parent.helpSystemKeys['sec:Simulator-Dialog']
        if helpfile is None:
            if sys.version_info.major < 3:
                tkMessageBox.showerror('Help System','Cannot find or open this help element')
            else:
                messagebox.showerror('Help System','Cannot find or open this help element')            
            return
        if self.parent.parent.preferences.GetValue('OnlineHelp.UseOnlineHelp'):
            helpdir=self.parent.parent.preferences.GetValue('OnlineHelp.URL')
        else:
            helpdir=self.parent.parent.installdir
        url=helpdir+'/Help/Help.html.LyXconv/'+helpfile
        webbrowser.open(url)

    def onControlHelp(self):
        Doer.inHelp=True
        self.config(cursor='question_arrow')

    def onEscape(self):
        Doer.inHelp=False
        self.config(cursor='left_ptr')
    
class Simulator(object):
    def __init__(self,parent):
        self.parent=parent
    def SimulatorDialog(self):
        if not hasattr(self,'simulatorDialog'):
            self.simulatorDialog=SimulatorDialog(self)
        if self.simulatorDialog == None:
            self.simulatorDialog=SimulatorDialog(self)
        else:
            if not self.simulatorDialog.winfo_exists():
                self.simulatorDialog=SimulatorDialog(self)
        return self.simulatorDialog
    def UpdateWaveforms(self,outputWaveformList,outputWaveformLabels):
        self.SimulatorDialog().UpdateWaveforms(outputWaveformList,outputWaveformLabels).state('normal')
    def _ProcessWaveforms(self,callback=None):
        return self.transferMatriceProcessor.ProcessWaveforms(self.inputWaveformList)
    def Simulate(self):
        netList=self.parent.Drawing.schematic.NetList()
        netListText=netList.Text()
        import SignalIntegrity.Lib as si
        fd=si.fd.EvenlySpacedFrequencyList(
            self.parent.calculationProperties.endFrequency,
            self.parent.calculationProperties.frequencyPoints)
        cacheFileName=None
        if self.parent.preferences.GetValue('Cache.CacheResults'):
            cacheFileName=self.parent.fileparts.FileNameTitle()
        snp=si.p.SimulatorNumericParser(fd,cacheFileName=cacheFileName)
        snp.AddLines(netListText)
        progressDialog=ProgressDialog(self.parent,self.parent.installdir,"Transfer Parameters",snp,snp.TransferMatrices, granularity=10.0)
        try:
            self.transferMatrices=progressDialog.GetResult()
        except si.SignalIntegrityException as e:
            if sys.version_info.major < 3:
                tkMessageBox.showerror('Simulator',e.parameter+': '+e.message)
            else:
                messagebox.showerror('Simulator',e.parameter+': '+e.message)
            return

        #self.transferMatrices.SParameters().WriteToFile('xfer.sXp')

        self.outputWaveformLabels=netList.OutputNames()

        try:
            self.inputWaveformList=self.parent.Drawing.schematic.InputWaveforms()
            self.sourceNames=netList.SourceNames()
        except si.SignalIntegrityException as e:
            if sys.version_info.major < 3:
                tkMessageBox.showerror('Simulator',e.parameter+': '+e.message)
            else:
                messagebox.showerror('Simulator',e.parameter+': '+e.message)
            return

        diresp=si.fd.Differentiator(fd).Response()

        for r in range(len(self.outputWaveformLabels)):
            for c in range(len(self.inputWaveformList)):
                if self.outputWaveformLabels[r][:3]=='di/' or self.outputWaveformLabels[r][:2]=='d/':
                    #print 'differentiate: '+self.outputWaveformLabels[r]
                    for n in range(len(self.transferMatrices.Matrices)):
                        self.transferMatrices.Matrices[n][r][c]=self.transferMatrices.Matrices[n][r][c]*diresp[n]

        self.transferMatriceProcessor=si.td.f.TransferMatricesProcessor(self.transferMatrices)
        si.td.wf.Waveform.adaptionStrategy='Linear'

        progressDialog=ProgressDialog(self.parent,self.parent.installdir,"Waveform Processing",self.transferMatriceProcessor,self._ProcessWaveforms)
        try:
            outputWaveformList = progressDialog.GetResult()
        except si.SignalIntegrityException as e:
            if sys.version_info.major < 3:
                tkMessageBox.showerror('Simulator',e.parameter+': '+e.message)
            else:
                messagebox.showerror('Simulator',e.parameter+': '+e.message)
            return

        for r in range(len(outputWaveformList)):
            if self.outputWaveformLabels[r][:3]=='di/' or self.outputWaveformLabels[r][:2]=='i/':
                #print 'integrate: '+self.outputWaveformLabels[r]
                outputWaveformList[r]=outputWaveformList[r].Integral()

        for outputWaveformIndex in range(len(outputWaveformList)):
            outputWaveform=outputWaveformList[outputWaveformIndex]
            outputWaveformLabel = self.outputWaveformLabels[outputWaveformIndex]
            for device in self.parent.Drawing.schematic.deviceList:
                if device[PartPropertyPartName().propertyName].GetValue() in ['Output','DifferentialVoltageOutput','CurrentOutput']:
                    if device[PartPropertyReferenceDesignator().propertyName].GetValue() == outputWaveformLabel:
                        # probes may have different kinds of gain specified
                        gainProperty = device[PartPropertyVoltageGain().propertyName]
                        if gainProperty is None:
                            gainProperty = device[PartPropertyTransresistance().propertyName]
                        gain=gainProperty.GetValue()
                        offset=device[PartPropertyVoltageOffset().propertyName].GetValue()
                        delay=device[PartPropertyDelay().propertyName].GetValue()
                        if gain != 1.0 or offset != 0.0 or delay != 0.0:
                            outputWaveform = outputWaveform.DelayBy(delay)*gain+offset
                        outputWaveformList[outputWaveformIndex]=outputWaveform
                        break
        outputWaveformList = [wf.Adapt(
            si.td.wf.TimeDescriptor(wf.td.H,wf.td.K,self.parent.calculationProperties.userSampleRate))
                for wf in outputWaveformList]
        self.SimulatorDialog().title('Sim: '+self.parent.fileparts.FileNameTitle())
        self.SimulatorDialog().ExamineTransferMatricesDoer.Activate(True)
        self.SimulatorDialog().SimulateDoer.Activate(True)
        self.UpdateWaveforms(outputWaveformList, self.outputWaveformLabels)

    def VirtualProbe(self):
        netList=self.parent.Drawing.schematic.NetList()
        netListText=netList.Text()
        import SignalIntegrity.Lib as si
        cacheFileName=None
        if self.parent.preferences.GetValue('Cache.CacheResults'):
            cacheFileName=self.parent.fileparts.FileNameTitle()
        snp=si.p.VirtualProbeNumericParser(
            si.fd.EvenlySpacedFrequencyList(
                self.parent.calculationProperties.endFrequency,
                self.parent.calculationProperties.frequencyPoints),
            cacheFileName=cacheFileName)
        snp.AddLines(netListText)
        progressDialog=ProgressDialog(self.parent,self.parent.installdir,"Transfer Parameters",snp,snp.TransferMatrices, granularity=10.0)
        try:
            self.transferMatrices=progressDialog.GetResult()
        except si.SignalIntegrityException as e:
            if sys.version_info.major < 3:
                tkMessageBox.showerror('Virtual Probe',e.parameter+': '+e.message)
            else:
                messagebox.showerror('Virtual Probe',e.parameter+': '+e.message)
            return

        self.transferMatriceProcessor=si.td.f.TransferMatricesProcessor(self.transferMatrices)
        si.td.wf.Waveform.adaptionStrategy='Linear'

        try:
            self.inputWaveformList=self.parent.Drawing.schematic.InputWaveforms()
            self.sourceNames=netList.MeasureNames()
        except si.SignalIntegrityException as e:
            if sys.version_info.major < 3:
                tkMessageBox.showerror('Virtual Probe',e.parameter+': '+e.message)
            else:
                messagebox.showerror('Virtual Probe',e.parameter+': '+e.message)
            return

        progressDialog=ProgressDialog(self.parent,self.parent.installdir,"Waveform Processing",self.transferMatriceProcessor,self._ProcessWaveforms)
        try:
            outputWaveformList = progressDialog.GetResult()
        except si.SignalIntegrityException as e:
            if sys.version_info.major < 3:
                tkMessageBox.showerror('Virtual Probe',e.parameter+': '+e.message)
            else:
                messagebox.showerror('Virtual Probe',e.parameter+': '+e.message)
            return

        self.outputWaveformLabels=netList.OutputNames()

        for outputWaveformIndex in range(len(outputWaveformList)):
            outputWaveform=outputWaveformList[outputWaveformIndex]
            outputWaveformLabel = self.outputWaveformLabels[outputWaveformIndex]
            for device in self.parent.Drawing.schematic.deviceList:
                if device[PartPropertyPartName().propertyName].GetValue() in ['Output','DifferentialVoltageOutput','CurrentOutput']:
                    if device[PartPropertyReferenceDesignator().propertyName].GetValue() == outputWaveformLabel:
                        # probes may have different kinds of gain specified
                        gainProperty = device[PartPropertyVoltageGain().propertyName]
                        if gainProperty is None:
                            gainProperty = device[PartPropertyTransresistance().propertyName]
                        gain=gainProperty.GetValue()
                        offset=device[PartPropertyVoltageOffset().propertyName].GetValue()
                        delay=device[PartPropertyDelay().propertyName].GetValue()
                        if gain != 1.0 or offset != 0.0 or delay != 0.0:
                            outputWaveform = outputWaveform.DelayBy(delay)*gain+offset
                        outputWaveformList[outputWaveformIndex]=outputWaveform
                        break
        outputWaveformList = [wf.Adapt(
            si.td.wf.TimeDescriptor(wf.td.H,wf.td.K,self.parent.calculationProperties.userSampleRate))
                for wf in outputWaveformList]
        self.SimulatorDialog().title('Virtual Probe: '+self.parent.fileparts.FileNameTitle())
        self.SimulatorDialog().ExamineTransferMatricesDoer.Activate(True)
        self.SimulatorDialog().SimulateDoer.Activate(True)
        self.UpdateWaveforms(outputWaveformList, self.outputWaveformLabels)
