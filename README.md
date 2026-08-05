# Reproduction of the calculations in Colquhoun & Lape (2012)

[![run notebook](https://github.com/DCPROGS/ColquhounLape2012-reproduction/actions/workflows/run-notebook.yml/badge.svg)](https://github.com/DCPROGS/ColquhounLape2012-reproduction/actions/workflows/run-notebook.yml)

Colquhoun, D., and R. Lape. 2012. Allosteric coupling in ligand-gated ion
channels. *J. Gen. Physiol.* 140:599–612.
doi:[10.1085/jgp.201210844](https://doi.org/10.1085/jgp.201210844)

This repository accompanies a corrigendum to that paper. It contains a single
Jupyter notebook that recomputes, from the published rate constants, every
number and every calculated figure in the paper: **Figs. 6, 7, and 8**,
**Table 1**, and the quantities quoted in the running text (equilibrium
occupancies, mean lifetimes, transition probabilities and frequencies, and
route probabilities).

The notebook is executed on every push by GitHub Actions, against a pinned
release of SCALCS, so the numbers below are checked rather than asserted.

## What the corrigendum corrects

**1. Two traces in Fig. 6 B are interchanged.** The trace labelled `AF` is in
fact `A3F`, and vice versa. The line styles are swapped with the labels, so the
0.05 plateau during the pulse is drawn dash-dot although the legend assigns
solid lines to triliganded states.

At 1 mM glycine the identification is not marginal. Twelve milliseconds into
the pulse the notebook gives

| state | occupancy at *t* = 12 ms |
|-------|-------------------------|
| `A3F` | 0.0498 |
| `A2F` | 0.0010 |
| `AF`  | 0.0000077 |

The plateau visible at about 0.05 can only be `A3F`; `AF` is some 6,500 times
smaller and lies far below the bottom of the panel. Table 1 of the paper agrees,
giving `A3F` = 4.99 % and `AF` = 0.0007 % at equilibrium at 1 mM.

**2. Fig. 6, Figs. 7 and 8, and Table 1 were computed from a single dataset,**
not from the averaged rate constants shown in Fig. 3. The dataset is the one
held in `bgtv2a.mec`.

With those rate constants all twelve published quantities the notebook checks
are reproduced to within **0.13 %** — residuals consistent with the paper having
rounded to 3–4 significant figures, rather than with any difference in the
calculation. With the Fig. 3 averages they are not: that set is 11–18 % out on
the smaller occupancies and up to 26 % out on the route probabilities, and it
misorders the two outside routes at 1 mM. The notebook computes both and
tabulates the difference side by side, so the size of the effect is visible.

**3. Two published numbers appear to be misprints.** Neither affects any
conclusion.

*Table 1, `AF*` at 1 mM.* Given as 0.0015 %; the rate constants give 0.001154 %,
which would print as 0.0012, and the Fig. 3 averages give 0.001196 %. Nineteen
of the twenty entries in Table 1 match to the precision printed; this is the
exception.

*The clockwise route probability at 10 µM.* The paper gives it as 2.8 × 10⁻⁵. The rate constants used for
everything else give 2.385 × 10⁻⁵, which would print as 2.4 × 10⁻⁵. The same
expression reproduces the 1 mM value exactly (0.05727 against a published
0.0573), and the paper's own following sentence — that the other two routes are
"about 30 times more likely than the clockwise route" — holds for 2.4 × 10⁻⁵
(ratios 30.7 and 32.1) but not for 2.8 × 10⁻⁵ (26.1 and 27.5). No conclusion
depends on it.

The two sets differ in a second way that matters. The single dataset obeys
microscopic reversibility to within float32 round-off (`max |f_ij − f_ji|`
relative error 2.1e-09 at 10 µM), whereas the averaged set violates it by 3–4 %,
because averaging rate constants over experiments does not preserve the cycle
constraints.

## The mechanism

The flip mechanism of Burzomato et al. (2004) for the heteromeric α1β glycine
receptor: ten states, three of them open.

The rate constants are **embedded in the notebook itself**, exactly as stored in
`bgtv2a.mec` — the values are written out as the 32-bit floats the file holds
(for instance 3690.69189453125), so no `.mec` file and no file-reading code is
needed to run this. The notebook checks the embedded matrix against the original
file when that file happens to be present, and reports
`max |Q_file − Q_embedded| = 0.000e+00`.

Note that the paper's state numbering and the SCALCS state ordering differ:
states 4 and 6 are interchanged. The notebook indexes everything by state
*name*, so the ordering never has to be tracked by hand.

## Running it

The notebook is pinned to SCALCS **v0.5.1-cl2012** on
[DCPROGS/SCALCS](https://github.com/DCPROGS/SCALCS). That tag is immutable;
later SCALCS releases may change results.

### conda

```bash
conda env create -f environment.yml
conda activate cl2012
jupyter lab ColquhounLape2012_reproduction.ipynb
```

### pip

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
jupyter lab ColquhounLape2012_reproduction.ipynb
```

### Non-interactively

```bash
jupyter nbconvert --to notebook --execute ColquhounLape2012_reproduction.ipynb --output executed.ipynb
```

Runtime is a couple of minutes; nothing needs a GPU or a large machine.

> **Windows note.** If `pip install` fails while unpacking JupyterLab with
> `OSError: [Errno 2] No such file or directory`, the cause is the 260-character
> path limit, not this package: JupyterLab ships some deeply nested files.
> Install into a short path such as `C:\cl2012`, or enable long-path support.

## How the numbers are checked

The notebook's last cell is a verification cell. It asserts

* all twelve published quantities, against the values printed in the paper,
  to a tolerance of 0.25 % (largest residual actually observed: 0.129 %);
* the Fig. 6 B identification — that at 12 ms `A3F` exceeds `AF` by more than
  three orders of magnitude (observed ratio 6,445);
* microscopic reversibility of the embedded rate constants at both
  concentrations (2.1e-09 relative at 10 µM, 5.3e-12 at 1 mM);
* that the embedded matrix is a proper Q matrix — rows summing to zero and
  equilibrium occupancies summing to one.

It raises on any failure, so executing the notebook is a regression test on the
paper's numbers rather than a check that the code merely runs. This is what the
CI badge above reports.

## Verified environment

The notebook has been executed end to end, with no cell errors, in a clean
virtual environment containing nothing but the pinned SCALCS and its
dependencies:

| | |
|---|---|
| SCALCS | 0.5.1 (tag `v0.5.1-cl2012`) |
| Python | 3.13 |
| NumPy | 2.5.1 |
| SciPy | 1.18.0 |
| pandas | 3.0.5 |
| matplotlib | 3.11.1 |

Provenance was checked inside the executing kernel: all eleven imported SCALCS
modules resolved to the installed package, not to a development checkout.

## Contents

| file | |
|---|---|
| `ColquhounLape2012_reproduction.ipynb` | the reproduction; 57 cells, 3 figures, stored with its outputs so it can be read on GitHub without running anything |
| `environment.yml` | conda specification |
| `requirements.txt` | pip specification |
| `.github/workflows/run-notebook.yml` | CI that executes the notebook and checks the verification cell passed |
| `CITATION.cff` | citation metadata |

The paper itself is not redistributed here; follow the DOI above.

## Licence

The notebook and supporting files are released under the GNU General Public
Licence version 2, matching SCALCS.
