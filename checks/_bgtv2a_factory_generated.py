from scalcs import mechanism


def GlyR_flip_bgtv2a():
    """The single Burzomato et al. (2004) dataset "bgtv2a".

    These are the rate constants from which Colquhoun & Lape (2012) computed
    Table 1 and Figures 6, 7 and 8, and every number quoted in the text.
    Figure 3 of that paper shows something different: the mean of fits to
    three datasets (that average is `scalcs.samples.samples.GlyR_flip`).

    Values are transcribed from bgtv2a.mec, which stores them as 32-bit
    floats; the decimal expansions below are therefore exact, and six
    significant figures would be ample (see the precision check below).
    """
    mectitle = 'flip, Burzomato2004'
    ratetitle = 'bgtv2a - the single dataset used in Colquhoun & Lape (2012)'

    AFS   = mechanism.State('A', 'AF*', 4e-11)
    A2FS  = mechanism.State('A', 'A2F*', 4e-11)
    A3FS  = mechanism.State('A', 'A3F*', 4e-11)
    AF    = mechanism.State('B', 'AF', 0)
    A2F   = mechanism.State('B', 'A2F', 0)
    A3F   = mechanism.State('B', 'A3F', 0)
    A3R   = mechanism.State('B', 'A3R', 0)
    A2R   = mechanism.State('B', 'A2R', 0)
    AR    = mechanism.State('B', 'AR', 0)
    R     = mechanism.State('C', 'R', 0)

    RateList = [
        mechanism.Rate(3690.69189453125, AFS, AF, name='alpha1',
                       limits=[1e-15, 1e+7]),
        mechanism.Rate(6059.1357421875, AF, AFS, name='beta1',
                       limits=[1e-15, 1e+7]),
        mechanism.Rate(2472.840576171875, A2FS, A2F, name='alpha2',
                       limits=[1e-15, 1e+7]),
        mechanism.Rate(32815.8515625, A2F, A2FS, name='beta2',
                       limits=[1e-15, 1e+7]),
        mechanism.Rate(6975.74609375, A3FS, A3F, name='alpha3',
                       limits=[1e-15, 1e+7]),
        mechanism.Rate(129611.671875, A3F, A3FS, name='beta3',
                       limits=[1e-15, 1e+7]),
        mechanism.Rate(1064.94287109375, A3F, A3R, name='gamma3',
                       limits=[1e-15, 1e+7]),
        mechanism.Rate(21028.595703125, A3R, A3F, name='delta3',
                       limits=[1e-15, 1e+7]),
        mechanism.Rate(3417.26611328125, A3F, A2F, name='3kf(-3)',
                       limits=[1e-15, 1e+7]),
        mechanism.Rate(166282256.0, A2F, A3F, name='kf(+3)', eff='c',
                       limits=[1e-15, 1e+10]),
        mechanism.Rate(20826.802734375, A2F, A2R, name='gamma2',
                       limits=[1e-15, 1e+7]),
        mechanism.Rate(6304.60302734375, A2R, A2F, name='delta2',
                       limits=[1e-15, 1e+7]),
        mechanism.Rate(2278.177490234375, A2F, AF, name='2kf(-2)',
                       limits=[1e-15, 1e+7]),
        mechanism.Rate(332564512.0, AF, A2F, name='2kf(+2)', eff='c',
                       limits=[1e-15, 1e+10]),
        mechanism.Rate(31142.638671875, AF, AR, name='gamma1',
                       limits=[1e-15, 1e+7]),
        mechanism.Rate(144.52456665039062, AR, AF, name='delta1',
                       limits=[1e-15, 1e+7]),
        mechanism.Rate(826.9252319335938, A3R, A2R, name='3k(-3)',
                       limits=[1e-15, 1e+7]),
        mechanism.Rate(616857.0625, A2R, A3R, name='k(+3)', eff='c',
                       limits=[1e-15, 1e+10]),
        mechanism.Rate(551.2835083007812, A2R, AR, name='2k(-2)',
                       limits=[1e-15, 1e+7]),
        mechanism.Rate(1233714.125, AR, A2R, name='2k(+2)', eff='c',
                       limits=[1e-15, 1e+10]),
        mechanism.Rate(275.6417541503906, AR, R, name='k(-1)',
                       limits=[1e-15, 1e+7]),
        mechanism.Rate(1850571.125, R, AR, name='3k(+1)', eff='c',
                       limits=[1e-15, 1e+10]),
        ]

    CycleList = [mechanism.Cycle(['A2F', 'AF', 'AR', 'A2R']),
                 mechanism.Cycle(['A3F', 'A2F', 'A2R', 'A3R'])]

    return mechanism.Mechanism(RateList, CycleList,
                               mtitle=mectitle, rtitle=ratetitle)
