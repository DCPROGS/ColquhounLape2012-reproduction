"""Run the whole Colquhoun & Lape (2012) calculation set against one SCALCS
version and print every quantity the notebook reports.

Run it twice, against two different SCALCS versions, then diff the two outputs
with compare_retarget.py. That is what substantiates the statement in section
2.2 of the notebook: that the two concentration-jump APIs - the procedural
solve_jump/pulse_square of the pinned v0.5.1-cl2012, and the solve/SquarePulse
of later releases - agree to better than one part in 10^6 on everything
reported here.

Usage:  python check_retarget.py [<path-to-a-scalcs-checkout>]

With no argument it uses whichever scalcs is importable. Given a directory, it
imports scalcs from there instead, pinning the namespace package's __path__ so
that an editable install elsewhere cannot leak in - a precaution that matters,
because that leak once made a check report success while exercising the wrong
code.
"""
import os
import sys

TARGET = sys.argv[1] if len(sys.argv) > 1 else None

if TARGET:
    sys.meta_path = [f for f in sys.meta_path
                     if 'editable' not in type(f).__module__.lower()]
    for m in [m for m in sys.modules if m.split('.')[0] == 'scalcs']:
        del sys.modules[m]
    sys.path.insert(0, os.path.abspath(TARGET))

import scalcs                                                     # noqa: E402

if TARGET:
    # scalcs is a namespace package - pin __path__ or the editable install leaks in
    scalcs.__path__ = [os.path.join(os.path.abspath(TARGET), 'scalcs')]
    for m in [m for m in sys.modules if m.startswith('scalcs.')]:
        del sys.modules[m]

import numpy as np                                                # noqa: E402
from scalcs import mechanism, qmatlib as qml, cjumps, popen       # noqa: E402

print('scalcs from : %s' % scalcs.__path__[0])

# =====================================================================
# Compatibility layer - exactly what will go into the notebook
# =====================================================================
NEW_JUMP_API = hasattr(cjumps, 'SquarePulse')
print('cjumps API  : %s' % ('dataclass (solve/SquarePulse)' if NEW_JUMP_API
                            else 'procedural (solve_jump/pulse_square)'))


def transition_probability(Q):
    """Eq. 2: pi_ij = q_ij / sum_{j!=i} q_ij = -q_ij / q_ii."""
    Q = np.asarray(Q, dtype=float)
    pi = Q / -np.diag(Q)[:, None]
    np.fill_diagonal(pi, 0.0)
    return pi


def transition_frequency(Q, p):
    """Eq. 3: f_ij = p_i * q_ij."""
    Q = np.asarray(Q, dtype=float)
    f = np.asarray(p, dtype=float)[:, None] * Q
    np.fill_diagonal(f, 0.0)
    return f


def square_pulse_jump(mec, cmax, width, prepulse, reclen, step, cb=0.0):
    """Concentration-jump response; returns (t, c, Popen, P)."""
    if NEW_JUMP_API:
        pulse = cjumps.SquarePulse(cmax=cmax, width=width,
                                   prepulse=prepulse, cb=cb)
        r = cjumps.solve(mec, pulse, reclen=reclen, step=step, method='ode')
        return r.t, r.c, r.Popen, r.P
    cargs = (cmax, cb, prepulse, width)
    return cjumps.solve_jump(mec, reclen, step, cjumps.pulse_square, cargs)


def relaxation_taus(mec, cmax, width):
    """Returns (tau_on_weighted, tau_off_weighted, tau_on, tau_off).

    The per-component arrays are None on versions that do not expose them.
    """
    if hasattr(cjumps, 'relaxation_taus'):
        pulse = cjumps.SquarePulse(cmax=cmax, width=width)
        rel = cjumps.relaxation_taus(mec, pulse)
        return (rel.tau_on_weighted, rel.tau_off_weighted,
                rel.tau_on, rel.tau_off)
    on, off = cjumps.weighted_taus(mec, cmax, width)
    return on, off, None, None


def equilibrium_dose_response(mec, concs=None):
    """Equilibrium Popen curve and its maximum, EC50 and Hill slope.

    Computed straight from p(inf), so it needs nothing beyond qmatlib.pinf and
    works on every SCALCS version. This is the *ideal* (zero dead-time) curve;
    the resolution-corrected version lives in scalcs.popen, which needs the HJC
    machinery.
    """
    if concs is None:
        concs = np.logspace(-9, -1, 400)
    pop = []
    for c in concs:
        mec.set_eff('c', c)
        p = qml.pinf(mec.Q)
        pop.append(p[:mec.kA].sum())
    pop = np.array(pop)

    pmax = pop[-1]
    half = pmax / 2.0
    k = int(np.argmax(pop >= half))                 # first point at/above half
    lo, hi = k - 1, k
    lc = np.interp(half, [pop[lo], pop[hi]],
                   [np.log10(concs[lo]), np.log10(concs[hi])])
    ec50 = 10 ** lc

    # Hill slope = d log[P/(Pmax-P)] / d log c, evaluated at EC50
    m = (pop > 0.05 * pmax) & (pop < 0.95 * pmax)
    y = np.log10(pop[m] / (pmax - pop[m]))
    x = np.log10(concs[m])
    nh = np.polyfit(x, y, 1)[0]
    return concs, pop, pmax, ec50, nh


# =====================================================================
from _bgtv2a_factory_generated import GlyR_flip_bgtv2a             # noqa: E402

mec = GlyR_flip_bgtv2a()
IDX = {s.name: i for i, s in enumerate(mec.States)}
C_LOW, C_HIGH = 10e-6, 1e-3
print('mechanism   : %s  (k=%d, kA=%d, %d rates)'
      % (mec.rtitle.strip(), mec.k, mec.kA, len(mec.Rates)))
print()


def Q_at(c):
    mec.set_eff('c', c)
    return mec.Q.copy()


res = {}

QH = Q_at(C_HIGH)
QL = Q_at(C_LOW)
pH, pL = qml.pinf(QH), qml.pinf(QL)
PI_H = transition_probability(QH)
PI_L = transition_probability(QL)
F_H = transition_frequency(QH, pH)

res['pinf sums to 1 (1 mM)'] = pH.sum()
res['Table 1 A3F* 1mM (%)'] = 100 * pH[IDX['A3F*']]
res['Table 1 R 10uM (%)'] = 100 * pL[IDX['R']]
res['Table 1 A3F 1mM (%)'] = 100 * pH[IDX['A3F']]
res['Table 1 A2F* 1mM (%)'] = 100 * pH[IDX['A2F*']]
res['pi row-sum max dev'] = float(np.abs(PI_H.sum(axis=1) - 1).max())
res['f43 (s^-1)'] = F_H[IDX['A3F'], IDX['A3F*']]
res['f10,9 (s^-1)'] = F_H[IDX['R'], IDX['AR']]
res['MR |f_ij - f_ji| max'] = float(np.abs(F_H - F_H.T).max())
res['initial binding (s^-1)'] = QH[IDX['R'], IDX['AR']]
res['lifetime of R (ms)'] = -1e3 / QH[IDX['R'], IDX['R']]

ROUTES = {
    'route via 8,5': [('AR','A2R'), ('A2R','A2F'), ('A2F','A3F'), ('A3F','A3F*')],
    'route clockwise': [('AR','A2R'), ('A2R','A3R'), ('A3R','A3F'), ('A3F','A3F*')],
    'route anticlock': [('AR','AF'), ('AF','A2F'), ('A2F','A3F'), ('A3F','A3F*')],
}
for nm, steps in ROUTES.items():
    res[nm + ' @1mM'] = float(np.prod([PI_H[IDX[a], IDX[b]] for a, b in steps]))
    res[nm + ' @10uM'] = float(np.prod([PI_L[IDX[a], IDX[b]] for a, b in steps]))

# Figure 6
t, c, Popen, P = square_pulse_jump(mec, 1e-3, 10e-3, 5e-3, 50e-3, 5e-6)
t_ms = t * 1e3
on = (t > 5e-3) & (t <= 15e-3)
off = t > 15e-3
res['occupancy sum min'] = float(P.sum(axis=0).min())
res['A2F* peak in pulse (%)'] = 100 * P[IDX['A2F*']][on].max()
res['A2F* peak in offset (%)'] = 100 * P[IDX['A2F*']][off].max()
res['Popen plateau'] = float(Popen[on].max())
res['p(A3F) at 12 ms'] = float(P[IDX['A3F']][int(np.searchsorted(t_ms, 12.0))])

ton, toff, ton_all, toff_all = relaxation_taus(mec, 1e-3, 10e-3)
res['tau_on weighted (ms)'] = ton * 1e3
res['tau_off weighted (ms)'] = toff * 1e3
res['per-component taus available'] = ton_all is not None

_c, _p, pmax, ec50, nh = equilibrium_dose_response(mec)
res['equilibrium maxPopen'] = pmax
res['equilibrium EC50 (M)'] = ec50
res['equilibrium Hill slope'] = nh

# the resolution-corrected values need the HJC machinery, which is broken on
# DCPROGS master (hjclib calls qmatlib.GXY, which does not exist there)
try:
    res['HJC maxPopen (tres=30us)'] = popen.maxPopen(mec, 30e-6)[0]
    res['HJC EC50 (tres=30us)'] = popen.EC50(mec, 30e-6)
    fn = getattr(popen, 'nH', None) or getattr(popen, 'Hill_slope', None)
    res['HJC Hill slope (tres=30us)'] = fn(mec, 30e-6)
except Exception as exc:                                          # noqa: BLE001
    res['HJC values'] = 'unavailable (%s: %s)' % (type(exc).__name__, exc)

print('=' * 62)
print('RESULTS')
print('=' * 62)
for k, v in res.items():
    if isinstance(v, bool):
        print('%-30s %s' % (k, v))
    elif isinstance(v, float):
        print('%-30s %.10g' % (k, v))
    else:
        print('%-30s %s' % (k, v))
