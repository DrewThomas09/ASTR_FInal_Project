"""Fixed Nov 25 synthetic centroid test; no real mission observations.
Run: python nov25_controlled_pointing_simulation.py
"""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent
N = 1000
N_IN, N_OUT = 12, 24
F_T, F_N, SEP, DEPTH = 1., .25, 1., .001
SCIENCE_SD = .001
JITTER = [0., .0005, .002, .008]
REF_SD = [.0005, .002, .006]
SEED = 1260025

# All simulated events have identical fractional total-light loss.
loss = DEPTH * (F_T + F_N)
x0 = F_N * SEP / (F_T + F_N)
true_target = F_N * SEP / (F_T + F_N - loss) - x0
true_neighbor = (F_N - loss) * SEP / (F_T + F_N - loss) - x0
is_target = np.arange(2*N) < N
truth = np.where(is_target, true_target, true_neighbor)
rng = np.random.default_rng(SEED)
# Exact Gaussian distribution of difference between two independent window means.
scale = np.sqrt(1/N_IN + 1/N_OUT)
z_jitter, z_science, z_ref = rng.standard_normal((3, 2*N))
rows = []
for jitter in JITTER:
    raw = truth + jitter*z_jitter + SCIENCE_SD*scale*z_science
    for ref_sd in REF_SD:
        reference = jitter*z_jitter + ref_sd*scale*z_ref
        corrected = raw - reference
        raw_ok = (raw > 0) == is_target
        corr_ok = (corrected > 0) == is_target
        rmse = lambda x: float(np.sqrt(np.mean((x-truth)**2)))
        delta = corr_ok.astype(float)-raw_ok.astype(float)
        rows.append(dict(jitter_sd_px=jitter, reference_per_cadence_sd_px=ref_sd,
            n_target=N, n_neighbor=N, raw_target_correct=int(raw_ok[:N].sum()),
            raw_neighbor_correct=int(raw_ok[N:].sum()), corrected_target_correct=int(corr_ok[:N].sum()),
            corrected_neighbor_correct=int(corr_ok[N:].sum()), raw_accuracy=float(raw_ok.mean()),
            corrected_accuracy=float(corr_ok.mean()), accuracy_change=float(delta.mean()),
            corrected_only=int((corr_ok & ~raw_ok).sum()), raw_only=int((raw_ok & ~corr_ok).sum()),
            paired_mc_se=float(delta.std(ddof=1)/np.sqrt(2*N)), raw_rmse_px=rmse(raw), corrected_rmse_px=rmse(corrected)))
        assert np.allclose(corrected, truth+SCIENCE_SD*scale*z_science-ref_sd*scale*z_ref)
        assert abs(delta.mean() - (corr_ok.mean()-raw_ok.mean())) < 1e-12

with (OUT/'nov25_pointing_results.csv').open('w', newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
print(f'True centroid shifts: target {true_target:+.9f} px, neighbor {true_neighbor:+.9f} px')
print('Jitter (px) | Ref noise (px/cadence) | Raw % | Corrected % | gain pp | raw RMSE (px) | corrected RMSE (px)')
for r in rows:
    print(f"{r['jitter_sd_px']:.4f} | {r['reference_per_cadence_sd_px']:.4f} | {r['raw_accuracy']*100:5.1f} | {r['corrected_accuracy']*100:5.1f} | {r['accuracy_change']*100:+5.1f} | {r['raw_rmse_px']:.6f} | {r['corrected_rmse_px']:.6f}")

# Plot all conditions: raw is invariant to the reference measurement noise.
fig, ax=plt.subplots(figsize=(9,4.8), layout='constrained')
x=np.arange(len(JITTER)); base=[100*next(r['raw_accuracy'] for r in rows if r['jitter_sd_px']==j) for j in JITTER]
ax.plot(x,base,'o-',color='#343434',lw=2.2,label='Uncorrected')
for ref, color in zip(REF_SD,['#800000','#246a91','#a06b24']):
    vals=[100*next(r['corrected_accuracy'] for r in rows if r['jitter_sd_px']==j and r['reference_per_cadence_sd_px']==ref) for j in JITTER]
    ax.plot(x,vals,'s--',lw=1.8,color=color,label=f'Corrected: ref. noise {ref:g} px/cadence')
ax.set_xticks(x,[f'{j:g}' for j in JITTER]);ax.set_ylim(45,95)
ax.axhline(50,color='#999999',lw=1,ls=':');ax.set_xlabel('Common in/out pointing displacement SD (pixels)');ax.set_ylabel('Correct source direction (%)')
ax.set_title('Simulated reference-star correction: benefit depends on noise',loc='left',fontsize=12,weight='bold')
ax.legend(loc='upper right',fontsize=9,frameon=False);ax.grid(axis='y',alpha=.2);ax.spines[['top','right']].set_visible(False)
fig.savefig(OUT/'nov25_pointing_simulation.png',dpi=200);fig.savefig(OUT/'nov25_pointing_simulation.svg')
