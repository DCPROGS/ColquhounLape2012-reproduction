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

Of the 28 quantities compared, about half agree bit for bit and the rest differ
in their last digits. **The largest disagreement on any quantity the notebook
reports is under 1 × 10⁻⁶ relative** — on two runs here it was 5.8 × 10⁻⁷ and
6.6 × 10⁻⁷, both on the `A2F*` peak during the pulse. `p(A3F)` at 12 ms differs
by around 1.5 × 10⁻⁷ and is 0.0498 either way. No value printed anywhere in the
notebook changes at the precision shown.

Do not expect the exact figures to reproduce. The residuals are round-off, so
they shift with the numpy and scipy build, and so does the count of quantities
that differ. The claim worth checking is the bound — better than one part in
10⁶ on everything reported — not any particular digit.

The cause is not the two APIs, which describe the same pulse and hand it to
`scipy.odeint` with the same `atol` and `rtol`. The equilibrium occupancies that
seed the integration differ by a few parts in 10⁹ between versions, and
integrating amplifies that.

Two lines of the comparison look alarming and are not.

`MR |f_ij - f_ji| max` can differ by around 10⁻⁵ relative, but it compares two
numbers near 3.4 × 10⁻⁸ — round-off residuals from the microscopic-reversibility
check. The relative difference between two quantities that are both
indistinguishable from zero carries no meaning.

The weighted relaxation time constants may print as complex on the pinned
release, as `(0.8373957876+0j)`, while the later one prints a real number. That
is the numpy 2.5 change to `linalg.eig`, which returns `complex128` for a real
matrix whose eigenvalues are all real; later SCALCS releases defend against it
and v0.5.1 predates the fix. It does not affect the notebook, which computes the
transition probabilities and frequencies directly from the Q matrix rather than
through the library — one of the reasons it does so.

## A note on how these are run

Given a directory, `check_retarget.py` imports `scalcs` from it and pins the
namespace package's `__path__`. That precaution is not decorative: `scalcs` is a
namespace package, and an editable install elsewhere on the machine will
otherwise merge itself into it. During this work that leak once made a check
report success while it was exercising a different version of the code than the
one it named.
