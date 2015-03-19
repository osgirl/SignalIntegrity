import SignalIntegrity as si

sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device D 4','device Z 2',
    'port 1 D 1 2 D 3 3 D 2',
    'connect D 2 Z 2','connect Z 1 D 4'])
ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True)
ssps.AssignSParameters('D',si.sy.ShuntZFourPort('Z'))
ssps.AssignSParameters('Z',si.sy.SeriesZ('\\varepsilon'))
ssps.LaTeXSolution(size='biggest').Emit()
