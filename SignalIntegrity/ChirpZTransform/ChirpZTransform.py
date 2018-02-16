'''
    Provides M+1 points from fs to fe of the chirp z transform of the vector x
'''
#
#  Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
#  Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
#  All Rights Reserved.
#
#  Explicit license in accompanying README.txt file.  If you don't have that file
#  or do not agree to the terms in that file, then you are not licensed to use
#  this material whatsoever.

from numpy import fft
import cmath
import math
from numpy import empty
## Computes the chirp-z transform
#
# @param x an input vector (list) of real time-domain samples
# @param Fs the sample rate of the the data samples in x
# @param fs the start frequency for the result
# @param fe the end frequency for the result
# @param M the number of points in the result (-1)
# @param highSpeed (optional, defaults to True) whether to use the high-speed,
# but unreadable version.  The readable, low-speed version is the definition
# is used for testing.
#
# Technically, the chirp-z transform can evaluate the z-transform at equi-angularly
# spaced points on a somewhat arbitrary arc, but here, we use it to compute equi-angularly
# spaced points on the rim of the unit circle, and as such, it is used simply to resample
# data.  Usually, we set fs=0 and the result is an M+1 point DFT of the waveform from 0 to
# fs, without the same limitations imposed as the standard DFT.
#
# The equation for the czt is:
#
# \f$m\in 0 \ldots M\f$
#
# \f$X\left[m\right]=\sum_{k=0}^{K-1}x\left[k\right]\cdot e^{-j\cdot2\pi\cdot\frac{k\cdot m}
# {M}\cdot F_{e}}\f$
#
def CZT(x,Fs,fs,fe,M,highSpeed=True):
    M=int(M); K=len(x); fs=float(fs); Fs=float(Fs); fe=float(fe)
    theta0=fs/Fs; phi0=(fe-fs)/Fs*1./M; A0=1.; W0=1.
    A=A0*cmath.exp(1j*2.*math.pi*theta0)
    W=W0*cmath.exp(1j*2.*math.pi*phi0)
    if highSpeed:
        L=pow(2,int(math.ceil(math.log(float(M+K),2.))))*2
        v=[0 for l in range(L)]
        for k in range(M+1): v[k]=pow(W,float(k*k)/2.)
        for k in range(M+1,L-K+1): v[k]=0.
        for k in range(L-K+1,L): v[k]=pow(W,(L-k)*(L-k)/2.)
        V=fft.fft(v)
        y = [0 for l in range(L)]
        for k in range(K): y[k]=x[k]*pow(A,-k)*pow(W,-(k*k)/2.)
        for k in range(K,L): y[k]=0
        Y=fft.fft(y)
        P=[Y[l]*V[l] for l in range(L)]
        P=fft.ifft(P)
        X = [P[m]/v[m] for m in range(M+1)]
    else:
        Zeta=[A*pow(W,m) for m in range(M+1)]
        X=[]
        for m in range(M+1):
            Xm=0.
            for k in range(K): Xm=Xm+x[k]*pow(Zeta[m],-k)
            X.append(Xm)
    return X