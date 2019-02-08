"""
 pseudo-random polynomial
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

class PseudoRandomPolynomial(list):
    def __init__(self,polynomial):
        list.__init__(self,polynomial)
    def Order(self):
        return len(self)-1
    def Pattern(self):
        """generate a list of bits according to the polynomial
        @return returns a list of integer (1 or 0)

        for an order P polynomial, the list of bits is 2^P-1 elements long
        """
        order = len(self)-1
        length = 2**order-1
        pattern = [1 if k < order else 0 for k in range(length)]
        for i in range(order): pattern[i]=1
        for i in range(order,length):
            pattern[i]=sum([self[p]*pattern[i-(order-p)] for p in range(order)])%2
        pattern = [(b+1)%2 for b in pattern]
        return pattern

class Prbs7Polynomial(PseudoRandomPolynomial):
    """the prbs 7 polynomial
    The prbs7 polynomial 1 + x^6 + x^7
    """
    def __init__(self):
        PseudoRandomPolynomial.__init__(self,[1,1,0,0,0,0,0,1])

class Prbs9Polynomial(PseudoRandomPolynomial):
    """the prbs 9 polynomial
    The prbs9 polynomial 1 + x^5 + x^9
    """
    def __init__(self):
        PseudoRandomPolynomial.__init__(self,[1,0,0,0,1,0,0,0,0,1])
        
class Prbs11Polynomial(PseudoRandomPolynomial):
    """the prbs 11 polynomial
    The prbs11 polynomial 1 + x^9 + x^11
    """
    def __init__(self):
        PseudoRandomPolynomial.__init__(self,[1,0,1,0,0,0,0,0,0,0,0,1])

class Prbs15Polynomial(PseudoRandomPolynomial):
    """the prbs 15 polynomial
    The prbs15 polynomial 1 + x^14 + x^15
    """
    def __init__(self):
        PseudoRandomPolynomial.__init__(self,[1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1])


class Prbs20Polynomial(PseudoRandomPolynomial):
    """the prbs 20 polynomial
    The prbs20 polynomial 1 + x^3 + x^20
    """
    def __init__(self):
        PseudoRandomPolynomial.__init__(self,[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1])

class Prbs23Polynomial(PseudoRandomPolynomial):
    """the prbs 23 polynomial
    The prbs23 polynomial 1 + x^18 + x^23
    """
    def __init__(self):
        PseudoRandomPolynomial.__init__(self,[1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1])

class Prbs31Polynomial(PseudoRandomPolynomial):
    """the prbs 31 polynomial
    The prbs23 polynomial 1 + x^28 + x^31
    """
    def __init__(self):
        PseudoRandomPolynomial.__init__(self,[1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1])
