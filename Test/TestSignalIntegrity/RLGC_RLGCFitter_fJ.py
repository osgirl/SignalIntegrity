class RLGCFitter(LevMar):
...
    def fJ(self,a,Fa=None):
        if self.m_Fa is None: self.m_Fa=self.fF(a)
        (R,L,G,C,Rse,df)=(a[0][0],a[1][0],a[2][0],a[3][0],a[4][0],a[5][0])
        dZ=[self.dZdR,self.dZdL,self.dZdG,self.dZdC,self.dZdRse,self.dZddf]
        dYdC=[p2f*(1j+df) for p2f in self.p2f]
        dYddf=[p2f*C for p2f in self.p2f]
        dY=[self.dYdR,self.dYdL,self.dYdG,dYdC,self.dYdRse,dYddf]
        dgamma=[[1./(2.*cmath.sqrt(z*y))*(dz*y+z*dy)
                for (z,y,dz,dy) in zip(self.Z,self.Y,dZ[i],dY[i])]
                    for i in range(6)]
        dZc=[[-1./2*(-dz*y+z*dy)/(y*y*cmath.sqrt(z/y))
                for (z,y,dz,dy) in zip(self.Z,self.Y,dZ[i],dY[i])]
                    for i in range(6)]
        drho=[[2.*dzc*self.Z0/((zc+self.Z0)*(zc+self.Z0))
                for (zc,dzc) in zip(self.Zc,dZc[i])]
                    for i in range(6)]
        e3g=[egx*egx*egx for egx in self.eg]
        e4g=[egx*egx*egx*egx for egx in self.eg]
        rho3=[r*r*r for r in self.rho]
        rho4=[r*r*r*r for r in self.rho]
        dS11=[[(2*r*e2-2.*r3*e2)/((r2*e2-1)*(r2*e2-1))*dg+
            (-e2-r2*e4+1.+r2*e2)/((r2*e2-1)*(r2*e2-1))*dr
                for (r,r2,r3,r4,e,e2,e3,e4,dg,dr) in
                    zip(self.rho,self.rho2,rho3,rho4,self.eg,
                        self.e2g,e3g,e4g,dgammadx,drhodx)]
                            for (dgammadx,drhodx) in zip(dgamma,drho)]
        dS12=[[(e3*r4-e-e3*r2+e*r2)/((r2*e2-1)*(r2*e2-1))*dg+
            (-2.*e*r+2.*e3*r)/((r2*e2-1)*(r2*e2-1))*dr
                for (r,r2,r3,r4,e,e2,e3,e4,dg,dr) in
                    zip(self.rho,self.rho2,rho3,rho4,self.eg,
                        self.e2g,e3g,e4g,dgammadx,drhodx)]
                            for (dgammadx,drhodx) in zip(dgamma,drho)]
        dS=[[[[dS11[i][n],dS12[i][n]],[dS12[i][n],dS11[i][n]]]
                for n in range(len(self.f))]
                    for i in range(6)]
        vdS=[self.VectorizeSp(ds) for ds in dS]
        return [[vdS[m][r][0] for m in range(len(a))] for r in range(len(Fa))]
...
