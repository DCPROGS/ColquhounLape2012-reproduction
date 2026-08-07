# Cross-version checks

The notebook is pinned to SCALCS **v0.5.1-cl2012**, and says in section 2.2 that
the two concentration-jump APIs — the procedural `solve_jump`/`pulse_square` of
that release, and the `solve`/`SquarePulse` of later ones — agree to better than
one part in 10⁶ on everything the notebook reports.

These two scripts are how that claim is checked, so that it does not have to be
taken on trust any more than the numbers in the notebook do.

| file | |
|---|---|
| `check_retarget.py` | runs the whole calculation set against one SCALCS version and prints every quantity |
| `compare_retarget.py` | diffs two of those outputs and reports the worst disagreement |
| `_bgtv2a_factory_generated.py` | builds the mechanism from the same embedded rate constants the notebook uses, so both runs start from identical inputs |

## Running it

Get two SCALCS versions side by side — git worktrees are the least intrusive way:

```bash
git clone https://github.com/DCPROGS/SCALCS.git
git -C SCALCS worktree add --detach ../scalcs-pinned v0.5.1-cl2012
git -C SCALCS worktree add --detach ../scalcs-latest master
```

Then run the calculation set against each and diff the two:

```bash
python check_retarget.py ../scalcs-pinned > pinned.txt
```

```bash
python check_retarget.py ../scalcs-latest > latest.txt
```

```bash
python compare_retarget.py pinned.txt latest.txt v0.5.1-cl2012 latest
```

## What you should see

Of the 28 quantities compared, 13 agree bit for bit and 15 differ. The largest
disagreement on any reported quantity is about **5.8 × 10⁻⁷** relative, on the
`A2F*` peak during the pulse; `p(A3F)` at 12 ms differs by 1.4 × 10⁻⁷ and is
0.0498 either way. No value printed anywhere in the notebook changes at the
precision shown.

The cause is not the two APIs, which describe the same pulse and hand it to
`scipy.odeint` with the same `atol` and `rtol`. The equilibrium occupancies that
seed the integration differ by about 3 × 10⁻⁹ between versions, and integrating
amplifies that.

One line of the comparison looks alarming and is not. `MR |f_ij - f_ji| max`
differs by 1.3 × 10⁻⁵ relative, but that compares 3.407262 × 10⁻⁸ against
3.407218 × 10⁻⁸ — two round-off residuals from the microscopic-reversibility
check. The relative difference between two quantities that are both
indistinguishable from zero carries no meaning.

## A note on how these are run

Given a directory, `check_retarget.py` imports `scalcs` from it and pins the
namespace package's `__path__`. That precaution is not decorative: `scalcs` is a
namespace package, and an editable install elsewhere on the machine will
otherwise merge itself into it. During this work that leak once made a check
report success while it was exercising a different version of the code than the
one it named.
