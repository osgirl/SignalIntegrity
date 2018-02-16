"""
Converts impedance parameters to s-parameters
"""
# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
#
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.
from numpy import matrix
from numpy import identity

from Z0KHelper import Z0KHelper

## Converts Z-parameters to s-parameters
# @param Z0 (optional, defaults to None) the reference impedance
# @param K (optional, defaults to None) scaling factor
#
# Converts Z-parameters to s-parameters
#
# @see Z0KHelper to see how the reference impedance
# and scaling factor are determined.
def Z2S(Z,Z0=None,K=None):
    (Z0,K)=Z0KHelper((Z0,K),len(Z))
    Z=matrix(Z)
    return (K.getI()*(Z-Z0)*(Z+Z0).getI()*K).tolist()

