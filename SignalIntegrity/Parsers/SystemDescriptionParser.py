from SignalIntegrity.SystemDescriptions import SystemDescription
from Devices.DeviceParser import DeviceParser
from ParserFile import ParserFile
from ParserArgs import ParserArgs

class SystemDescriptionParser(ParserFile,ParserArgs):
    def __init__(self,f=None,args=None):
        self.m_sd = None
        self.m_f=f
        self.m_lines=[]
        self.m_addThru = False
        self.AssignArguments(args)
    def SystemDescription(self):
        if self.m_sd is None:
            self._ProcessLines()
        return self.m_sd
    def SetFrequencies(self,f):
        self.m_sd = None
        self.m_f=f
    def AddLine(self,line):
        self.m_sd = None
        if len(line) == 0:
            return
        self.m_lines.append(line)
    def AddLines(self,lines):
        self.m_sd = None
        for line in lines:
            self.AddLine(line)
        return self
    def _ProcessLine(self,line):
        lineList=self.ReplaceArgs(line.split())
        if len(lineList) == 0:
            return
        if self.ProcessVariables(lineList):
            pass
        elif lineList[0] == 'device':
            dev=DeviceParser(self.m_f,int(lineList[2]),[lineList[i]
                for i in range(3,len(lineList))])
            self.m_sd.AddDevice(lineList[1],int(lineList[2]),dev.m_sp)
            if not dev.m_spf is None:
                self.m_spc.append((lineList[1],dev.m_spf))
        elif lineList[0] == 'connect':
            for i in range(3,len(lineList),2):
                self.m_sd.ConnectDevicePort(lineList[1],int(lineList[2]),
                    lineList[i],int(lineList[i+1]))
        elif lineList[0] == 'port':
            for i in range((len(lineList)-1)/3):
                self.m_sd.AddPort(lineList[i*3+2],int(lineList[i*3+3]),
                    int(lineList[i*3+1]),self.m_addThru)
        else:
            self.m_ul.append(line)
    def _ProcessLines(self):
        self.m_sd=SystemDescription()
        self.m_spc=[]
        self.m_ul=[]
        for line in self.m_lines:
            print 'processing line: '+line
            self._ProcessLine(line)
        return self