"""
 pseudo-random bit patterns
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
import math
from SignalIntegrity.Lib.TimeDomain.Waveform.Waveform import Waveform
from SignalIntegrity.Lib.TimeDomain.Waveform.TimeDescriptor import TimeDescriptor

class PseudoRandomBitPattern(object):
    rtvsT=0.5903445
    """generates pseudo-random bit sequences"""
    def __init__(self,polynomial):
        """constructor
        @param list of integer (1 or 0) constituting the polynomial
        
        for a P+1 element polynomial a with p in 0..P, note that a[0] is always a 1, and the polynomial
        is a[0] + a[1]*x + a[2]*x^2, etc.
        """
        self.polynomial = polynomial
    def Pattern(self):
        """generate a list of bits according to the polynomial
        @return returns a list of integer (1 or 0)

        for an order P polynomial, he list of bits is 2^P-1 elements long
        """
        order = len(self.polynomial)-1
        length = 2**order-1
        pattern = [1 if k < order else 0 for k in range(length)]
        for i in range(order): pattern[i]=1
        for i in range(order,length):
            pattern[i]=sum([self.polynomial[p]*pattern[i-(order-p)] for p in range(order)])%2
        pattern = [(b+1)%2 for b in pattern]
        return pattern
    @staticmethod
    def Prbs7Polynomial():
        """the prbs 7 polynomial
        @return The prbs7 polynomial 1 + x^6 + x^7
        """
        return [1,1,0,0,0,0,0,1]
    @staticmethod
    def Prbs9Polynomial():
        return [1,0,0,0,1,0,0,0,0,1]
    @staticmethod
    def Prbs11Polynomial():
        return [1,0,1,0,0,0,0,0,0,0,0,1]
    @staticmethod
    def Prbs15Polynomial():
        return [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1]
    @staticmethod
    def Prbs20Polynomial():
        return [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1]
    @staticmethod
    def Prbs23Polynomial():
        return [1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1]
    @staticmethod
    def Prbs31Polynomial():
        return [1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1]
    @staticmethod
    def RaisedCosine(t,T):
        """raised cosine
        @return the value of a raised cosine edge that is zero for t<0 and 1 for t>T.
        @remark the risetime of this edge is 59% of the value of T
        """
        if t < 0:
            return 0.
        elif t > T:
            return 1.
        else:
            return 1./2-1./2*math.cos(math.pi*t/T)
    def UnitPulse(self,t,risetime,unitInterval):
        T=risetime/self.rtvsT
        return self.RaisedCosine(t-T/2,T)-self.RaisedCosine(t-T/2-unitInterval,T)
    def UnitPulseWaveform(self,td,risetime,unitInterval):
        return Waveform(td,[self.UnitPulse(t,risetime,unitInterval) for t in td])
    def TimeDescriptor(self,bitRate,sampleRate):
        bits=2**(len(self.polynomial)-1)-1
        timeLength=bits/bitRate
        numPoints=int(math.floor(timeLength*sampleRate+0.5))
        return TimeDescriptor(0.,numPoints,sampleRate)
    def PseudoRandomWaveformFull(self,risetime,unitInterval,samplesPerUI):
        pattern=self.Pattern()
        numPoints=len(pattern)*samplesPerUI
        sampleRate=samplesPerUI/unitInterval
        td=TimeDescriptor(0.,numPoints,sampleRate)
        timeLength=numPoints/sampleRate
        return Waveform(td,[sum([(self.UnitPulse((td[k]-(i-1)*unitInterval)%timeLength,risetime,unitInterval)-0.5)*pattern[i]
            for i in range(len(pattern))]) for k in range(len(td))])+sum(pattern)/2
    def PseudoRandomWaveform(self,td,risetime,bitRate):
        pattern=self.Pattern()
        sampleRate=td.Fs
        patternTimeLength=len(pattern)/bitRate
        unitInterval=1./bitRate
        return Waveform(td,[sum([(self.UnitPulse((td[k]-(i-1)*unitInterval)%patternTimeLength,risetime,unitInterval)-0.5)*pattern[i]
            for i in range(len(pattern))]) for k in range(len(td))])+sum(pattern)/2
        
