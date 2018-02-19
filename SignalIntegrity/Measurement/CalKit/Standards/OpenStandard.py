"""
Open Standard
"""
# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
# 
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

from SignalIntegrity.SystemDescriptions.SystemSParametersNumeric import SystemSParametersNumeric
from SignalIntegrity.Measurement.CalKit.Standards.TerminationPolynomial import TerminationCPolynomial
from SignalIntegrity.Measurement.CalKit.Standards.Offset import Offset
from SignalIntegrity.SParameters.SParameters import SParameters

## OpenStandard
#
# class providing the s-parameters of an open standard as commonly defined
# for a calibration kit.
#
class OpenStandard(SParameters):
    ## Constructor
    #
    # @param f list of frequencies
    # @param offsetDelay (optional) float electrical length of offset in s (defaults to 0 s)
    # @param offsetZ0 (optional) float real characteristic impedance of offset (defaults to 50 Ohms)
    # @param offsetLoss (optional) float loss due to skin-effect defined in GOhms/s at 1 GHz (defaults to 0).
    # @param C0 (optional) float polynomial coefficient for capacitance of open termination
    # @param C1 (optional) float polynomial coefficient for capacitance of open termination
    # @param C2 (optional) float polynomial coefficient for capacitance of open termination
    # @param C3 (optional) float polynomial coefficient for capacitance of open termination
    #
    # The result is that the class becomes the base-class SParameters with the s-parameters
    # of a open standard.
    #
    # Termination capacitance polynomial is C0+f*(C1+f*(C2+f*C3)).
    #
    def __init__(self,f,offsetDelay=0.0,offsetZ0=50.0,offsetLoss=0.0,
                 C0=0.0,C1=0.0,C2=0.0,C3=0.0):
        # pragma: silent exclude
        from SignalIntegrity.Parsers.SystemDescriptionParser import SystemDescriptionParser
        # pragma: include
        sspn=SystemSParametersNumeric(SystemDescriptionParser().AddLines(
            ['device offset 2','device C 1','port 1 offset 1','connect offset 2 C 1']
            ).SystemDescription())
        offsetSParameters=Offset(f,offsetDelay,offsetZ0,offsetLoss)
        terminationSParameters=TerminationCPolynomial(f,C0,C1,C2,C3)
        sp=[]
        for n in range(len(f)):
            sspn.AssignSParameters('offset',offsetSParameters[n])
            sspn.AssignSParameters('C',terminationSParameters[n])
            sp.append(sspn.SParameters())
        SParameters.__init__(self,f,sp)
