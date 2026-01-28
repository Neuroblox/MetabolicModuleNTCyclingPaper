"""

@author: Botond B. Antal

January 2026

This script plots the simulated results.

"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Directories
OUTDIR = "" + "results/"   #TODO: insert your filepath here before results/

# rcParams
plt.rcParams.update({'font.size': 10})

# %%
# ===================================================================
# Figure 1: ketones
# ===================================================================

# Load data
data_bloodbhb_datapoints = pd.read_csv(OUTDIR + "martin-arrowsmith_etal_blood_bhb_timecourse.csv")
data_bloodbhb_timeseries = pd.read_csv(OUTDIR + f"model_blood_bhb_input_timeseries.csv")
data_brainbhb_datapoints = pd.read_csv(OUTDIR + "mujica-parodi_etal_brain_bhb_timeseries.csv")
data_brainbhb_timeseries = pd.read_csv(OUTDIR + f"model_timeseries.csv")[["timestamp", "KET_b"]].set_axis(["time", "concentration"], axis=1)

# Figure
plt.figure(figsize=(8.25, 3.5))

# Subplot 1
plt.subplot(1, 3, 1)
plt.scatter(
    data_bloodbhb_datapoints['time'],
    data_bloodbhb_datapoints['concentration'],
    label='Measured\n(Martin-\nArrowsmith\net al.)',
    color='black', s=80, zorder=2)
plt.plot(
    data_bloodbhb_timeseries['time'],
    data_bloodbhb_timeseries['concentration'],
    linewidth=2, label='Fitted (double\nexponential)',
    color='crimson', zorder=3)
plt.xlabel('Time after bolus (min)')
plt.ylabel('Concentration (mM)')
plt.title(r"Blood D-$\beta$HB")
plt.xlim(0, 220)
plt.xticks([0, 50, 100, 150, 200])
leg = plt.legend(framealpha=1, fontsize=8, bbox_to_anchor=(0.08, 0.2),
           edgecolor="black", loc="center left")
plt.grid(alpha=0.4, zorder=1)
leg.set_in_layout(False)

# Subplot 2
plt.subplot(1, 3, 2)
plt.scatter(
    data_brainbhb_datapoints['x'],
    data_brainbhb_datapoints['y']/12,
    label='Measured and rescaled\n(Mujica-Parodi et al.)',
    color='black', s=80, zorder=2)
plt.plot(
    data_brainbhb_timeseries['time'],
    data_brainbhb_timeseries['concentration'],
    linewidth=2, label='Simulated', color='dodgerblue', zorder=3)
plt.xlabel('Time after bolus (min)')
plt.ylabel('Concentration (mM)')
plt.title(r"Brain D-$\beta$HB")
plt.xlim(0, 220)
plt.xticks([0, 50, 100, 150, 200])
plt.legend(framealpha=1, fontsize=8, edgecolor="black")
plt.grid(alpha=0.4, zorder=1)

# Subplot 3
plt.subplot(1, 3, 3)
plt.plot(
    data_bloodbhb_timeseries['time'],
    data_bloodbhb_timeseries['concentration']/data_bloodbhb_timeseries['concentration'].max(),
    linewidth=2, label='Blood', color='crimson', zorder=2)
plt.plot(
    data_brainbhb_timeseries['time'],
    data_brainbhb_timeseries['concentration']/data_brainbhb_timeseries['concentration'].max(),
    linewidth=2, label='Brain', color='dodgerblue', zorder=3)
plt.xlabel('Time after bolus (min)')
plt.ylabel('Concentration (relative)')
plt.title("Normalized\n" + r'Blood & Brain D-$\beta$HB')
plt.xlim(0, 100)
plt.legend(framealpha=1, fontsize=8, edgecolor="black")
plt.grid(alpha=0.4, zorder=0)

# Save
plt.tight_layout()
plt.savefig(OUTDIR + f"fig_ketone_pk.pdf",
            dpi=300, transparent=True)

# %%
# ===================================================================
# Figure 2: time-series and validation
# ===================================================================

# Load simulation results
data_concs = pd.read_csv(OUTDIR + f"model_timeseries.csv")
data_fluxes = pd.read_csv(OUTDIR + f"model_fluxes.csv")

# Experiment data
exp_means = {"GLU": -10.6, "GABA": -36.9}
exp_errors = {"GLU": 1.2*1.96, "GABA": 4.2*1.96}  # 95% CI!

# Figure
plt.figure(figsize=(8.25, 3.3))

# Fluxes
# --------------

# Subplot
plt.subplot(1, 3, 1)

# Plot
plt.plot(data_fluxes["timestamp"], data_fluxes["CMRglc"],
         label='CMR$_{glc}$', lw=2, color="#000000")
plt.plot(data_fluxes["timestamp"], data_fluxes["GS"],
         label='V$_{GS}$', lw=2, linestyle='-', color="#44AB42F7")
plt.plot(data_fluxes["timestamp"], data_fluxes["PMAS in e"],
         label='V$_{PMAS}^e$', lw=2, color='#0066FF')
plt.plot(data_fluxes["timestamp"], data_fluxes["PMAS in i"],
         label='V$_{PMAS}^i$', lw=2, color="#D60000F7")
plt.plot(data_fluxes["timestamp"], data_fluxes["Ketone utilization"],
         label='CMR$_{Ket}$', lw=2, linestyle='--', color="#686868")
# plt.plot(data_fluxes["timestamp"], data_fluxes["GAD65"],
#          label='V$_{GAD65}$', lw=2, color="orange")
# plt.plot(data_fluxes["timestamp"], data_fluxes["GAD67"],
#          label='V$_{GAD67}$', lw=2, color="indianred")
# plt.plot(data_fluxes["timestamp"], data_fluxes["GT"],
#          label='V$_{GT}$', lw=2, linestyle='--', color="#B51861F7")

# Format
plt.xlabel('Time after bolus (min)')
plt.ylabel('Flux (mM/min)')
plt.xticks([0, 50, 100, 150, 200])
plt.xlim(0, 220)
plt.grid(alpha=0.4)
plt.title("Fluxes")
leg = plt.legend(framealpha=1, fontsize=7, edgecolor="black",
           bbox_to_anchor=(0.52, 0.48), loc="center left")
leg.set_in_layout

# Print values
print(f"CMRglc starts from {data_fluxes['CMRglc'][0]:.3f} mM/min "
      f"and is lowest at {data_fluxes['CMRglc'].min():.3f} mM/min "
      f"which occurs at t={data_fluxes['timestamp'][data_fluxes['CMRglc'].idxmin()]:.2f}) min")
print(f"CMRket starts from {data_fluxes['Ketone utilization'][0]:.3f} mM/min "
      f"and is highest at {data_fluxes['Ketone utilization'].max():.3f} mM/min "
      f"which occurs at t={data_fluxes['timestamp'][data_fluxes['Ketone utilization'].idxmax()]:.2f} min")
print(f"PMAS_e starts from {data_fluxes['PMAS in e'][0]:.3f} mM/min "
      f"and is lowest at {data_fluxes['PMAS in e'].min():.3f} mM/min "
      f"which occurs at t={data_fluxes['timestamp'][data_fluxes['PMAS in e'].idxmin()]:.2f} min")
print(f"PMAS_i starts from {data_fluxes['PMAS in i'][0]:.3f} mM/min "
      f"and is lowest at {data_fluxes['PMAS in i'].min():.3f} mM/min "
      f"which occurs at t={data_fluxes['timestamp'][data_fluxes['PMAS in i'].idxmin()]:.2f} min")
print(f"VGDH starts from {data_fluxes['GDH'][0]:.3f} mM/min "
      f"and is lowest at {data_fluxes['GDH'].min():.3f} mM/min "
      f"which occurs at t={data_fluxes['timestamp'][data_fluxes['GDH'].idxmin()]:.2f} min")
print(f"VGS starts from {data_fluxes['GS'][0]:.3f} mM/min "
      f"and is lowest at {data_fluxes['GS'].min():.3f} mM/min "
      f"which occurs at t={data_fluxes['timestamp'][data_fluxes['GS'].idxmin()]:.2f} min")
print(f"VGAD65 starts from {data_fluxes['GAD65'][0]:.3f} mM/min "
      f"and is lowest at {data_fluxes['GAD65'].min():.3f} mM/min "
      f"which occurs at t={data_fluxes['timestamp'][data_fluxes['GAD65'].idxmin()]:.2f} min")
print(f"VGAD67 starts from {data_fluxes['GAD67'][0]:.3f} mM/min "
      f"and is lowest at {data_fluxes['GAD67'].min():.3f} mM/min "
      f"which occurs at t={data_fluxes['timestamp'][data_fluxes['GAD67'].idxmin()]:.2f} min")
print(f"VGT starts from {data_fluxes['GT'][0]:.3f} mM/min "
      f"and is lowest at {data_fluxes['GT'].min():.3f} mM/min "
      f"which occurs at t={data_fluxes['timestamp'][data_fluxes['GT'].idxmin()]:.2f} min")

# Compartmental concentrations
# --------------

# Subplot
plt.subplot(1, 3, 2)

# Plot
plt.plot(data_concs["timestamp"], data_concs["GLU_e"],
         label='[Glu]$_{e}$', lw=2, color='#0066FF')
plt.plot(data_concs["timestamp"], data_concs["GLN_a"],
         label='[Gln]$_{a}$', lw=2, color="#44AB42F7")
plt.plot(data_concs["timestamp"], data_concs["GLU_a"],
         label='[Glu]$_{a}$', lw=2, color="dimgray")
plt.plot(data_concs["timestamp"], data_concs["GABA_i"],
         label='[GABA]$_{i}^c$', lw=2, color='orangered')
plt.plot(data_concs["timestamp"], data_concs["GABA_v"],
         label='[GABA]$_{i}^v$', lw=2, color='maroon')

# Format
plt.xlabel('Time after bolus (min)')
plt.ylabel('Concentration (mM)')
plt.xlim(0, 220)
plt.xticks([0, 50, 100, 150, 200])
leg = plt.legend(framealpha=1, fontsize=7, edgecolor="black",
           bbox_to_anchor=(0.56, 0.62), loc="center left")
plt.title("Pool concentrations (abs.)   ")
plt.grid(alpha=0.4, zorder=1)
leg.set_in_layout(False)

# Print values
print(f"GLU_e starts from {data_concs['GLU_e'][0]:.3f} mM "
      f"and is lowest at {data_concs['GLU_e'].min():.3f} mM "
      f"(-{100 * (data_concs['GLU_e'][0] - data_concs['GLU_e'].min()) / data_concs['GLU_e'][0]:.1f}%) "
      f"which occurs at t={data_concs['timestamp'][data_concs['GLU_e'].idxmin()]:.2f} min")
print(f"GLU_a starts from {data_concs['GLU_a'][0]:.3f} mM "
      f"and is lowest at {data_concs['GLU_a'].min():.3f} mM "
      f"(-{100 * (data_concs['GLU_a'][0] - data_concs['GLU_a'].min()) / data_concs['GLU_a'][0]:.1f}%) "
      f"which occurs at t={data_concs['timestamp'][data_concs['GLU_a'].idxmin()]:.2f} min")
print(f"GLU_a starts from {data_concs['GLU_a'][0]:.3f} mM "
      f"and is highest at {data_concs['GLU_a'].max():.3f} mM "
      f"(-{100 * (data_concs['GLU_a'][0] - data_concs['GLU_a'].max()) / data_concs['GLU_a'][0]:.1f}%) "
      f"which occurs at t={data_concs['timestamp'][data_concs['GLU_a'].idxmax()]:.2f} min")
print(f"GLN_a starts from {data_concs['GLN_a'][0]:.3f} mM "
      f"and is highest at {data_concs['GLN_a'].max():.3f} mM "
      f"(-{100 * (data_concs['GLN_a'][0] - data_concs['GLN_a'].max()) / data_concs['GLN_a'][0]:.1f}%) "
      f"which occurs at t={data_concs['timestamp'][data_concs['GLN_a'].idxmax()]:.2f} min")
print(f"GABA_i starts from {data_concs['GABA_i'][0]:.3f} mM "
      f"and is lowest at {data_concs['GABA_i'].min():.3f} mM "
      f"(-{100 * (data_concs['GABA_i'][0] - data_concs['GABA_i'].min()) / data_concs['GABA_i'][0]:.1f}%) "
      f"which occurs at t={data_concs['timestamp'][data_concs['GABA_i'].idxmin()]:.2f} min")
print(f"GABA_v starts from {data_concs['GABA_v'][0]:.3f} mM "
      f"and is lowest at {data_concs['GABA_v'].min():.3f} mM "
      f"(-{100 * (data_concs['GABA_v'][0] - data_concs['GABA_v'].min()) / data_concs['GABA_v'][0]:.1f}%) "
      f"which occurs at t={data_concs['timestamp'][data_concs['GABA_v'].idxmin()]:.2f} min")


# Validation with total concentrations
# --------------

# Subplot
plt.subplot(1, 3, 3)

# Glutamate
cols = ["GLU_e", "GLU_i", "GLU_a"]
x = data_concs["timestamp"]
y = 100 * data_concs[cols].sum(axis=1) / \
    data_concs.loc[0, cols].sum() - 100
plt.plot(x, y, label='[Glu]$_{tot}$ (sim.)', lw=2, color='#0066FF')
y_60_glu = y[(data_concs['timestamp'] - 60).abs().idxmin()]

# GABA
cols = ["GABA_i", "GABA_v"]
x = data_concs["timestamp"]
y = 100 * data_concs[cols].sum(axis=1) / \
    data_concs.loc[0, cols].sum() - 100
plt.plot(x, y, label="[GABA]$_{tot}$ (sim.)", lw=2, color='orangered')
y_60_gaba = y[(data_concs['timestamp'] - 60).abs().idxmin()]

# Add experimental data
plt.errorbar(60, exp_means['GLU'], yerr=exp_errors["GLU"],
             label="[Glu]$_{tot}$ (meas.)", fmt='o', lw=2, color="#001AFF",
             capsize=5, capthick=2)
plt.errorbar(60, exp_means['GABA'], yerr=exp_errors["GABA"],
             label="[GABA]$_{tot}$ (meas.)", fmt='o', lw=2, color="#BF0000",
             capsize=5, capthick=2)
plt.axvline(60, color='black', lw=1.5, ls='--', zorder=-1)

# Formatting
plt.axhline(0, color='black', lw=1, ls='--')
plt.xlabel('Time after bolus (min)')
plt.ylabel(r"$\Delta$%" + ' concentration (%)')
plt.xticks([0, 50, 100, 150, 200])
plt.xlim(0, 220)
plt.ylim(-100, 13)
leg = plt.legend(framealpha=1, edgecolor="black", fontsize=7,
                 bbox_to_anchor=(0.01, 0.19), loc="center left")
plt.grid(alpha=0.4)
plt.title("Total concentrations (" + r'$\Delta$%)')
leg.set_in_layout(False)

# Save
# plt.subplots_adjust(wspace=0.9)
plt.tight_layout(w_pad=1)
plt.savefig(OUTDIR + f"fig_timecourses.pdf",
            dpi=300, transparent=True)

# Print values
print(f"Glutamate: {y_60_glu:.1f}%")
print(f"GABA: {y_60_gaba:.1f}%")

# %%
# ===================================================================
# SI figure: time-series
# ===================================================================

# Load simulation results
data_concs = pd.read_csv(OUTDIR + f"model_timeseries.csv")
data_fluxes = pd.read_csv(OUTDIR + f"model_fluxes.csv")

# Figure
plt.figure(figsize=(8.25, 3.3))

# Fluxes
# -----------

# Subplot
plt.subplot(1, 3, 1)

# Plot all fluxes
plt.plot(data_fluxes["timestamp"], (data_fluxes["CMRglc"]),
         label='CMR$_{glc}$', lw=2, color="#424447")
plt.plot(data_fluxes["timestamp"], data_fluxes["Ketone utilization"],
         label='CMR$_{Ket}$', lw=2, color="#A22727")
plt.plot(data_fluxes["timestamp"], data_fluxes["PMAS in e"],
         label='PMAS$_e$', lw=2, color='#001DD6F7')
plt.plot(data_fluxes["timestamp"], data_fluxes["PMAS in i"],
         label='PMAS$_i$', lw=2, color="#D60000F7")
plt.plot(data_fluxes["timestamp"], data_fluxes["GLU cycling"],
         label='V$_{syn}^e$', lw=2, color="#00BFFF")
plt.plot(data_fluxes["timestamp"], data_fluxes["GABA cycling"],
         label='V$_{syn}^i$', lw=2, color="#FF00F7")
plt.plot(data_fluxes["timestamp"], data_fluxes["GDH"],
         label='V$_{GDH}$', lw=2, color="#006B26FF")
plt.plot(data_fluxes["timestamp"], data_fluxes["GS"],
         label='V$_{GS}$', lw=2, color='#44AB42F7')
plt.plot(data_fluxes["timestamp"], data_fluxes["GAD65"],
         label='V$_{GAD65}$', lw=2, color="#DA6D85F7")
plt.plot(data_fluxes["timestamp"], data_fluxes["GAD67"],
         label='V$_{GAD67}$', lw=2, color="#D66DDAF7")
plt.plot(data_fluxes["timestamp"], data_fluxes["GT"],
         label='V$_{GT}$', lw=2, color="#4286ABF7")


# Format
plt.xlabel('Time after bolus (min)')
plt.ylabel('Flux (mM/min)')
plt.xlim(0, 400)
plt.grid(alpha=0.4)
plt.title("Fluxes")
leg = plt.legend(framealpha=1, fontsize=7, edgecolor="black",
           bbox_to_anchor=(1.02, 0.42), loc="center left")
leg.set_in_layout(False)

# Concentrations
# -----------

# Subplot
plt.subplot(1, 3, 2)

# Plot all concentrations
plt.plot(data_concs["timestamp"], data_concs["GLU_e"],
         label='[Glu]$_{e}$', lw=2, color='#0066FF')
plt.plot(data_concs["timestamp"], data_concs["GLN_a"],
         label='[Gln]$_{a}$', lw=2, color="#44AB42F7")
plt.plot(data_concs["timestamp"], data_concs["GABA_i"],
         label='[GABA]$_{i}$', lw=2, color='orangered')
plt.plot(data_concs["timestamp"], data_concs["GABA_v"],
         label='[GABA]$_{v}$', lw=2, color='maroon')
plt.plot(data_concs["timestamp"], data_concs["GLU_a"],
         label='[Glu]$_{a}$', lw=2, color='deepskyblue')
plt.plot(data_concs["timestamp"], data_concs["GLU_i"],
         label='[Glu]$_{i}$', lw=2, color='dodgerblue')
plt.plot(data_concs["timestamp"], data_concs["GLN_e"],
         label='[Gln]$_{e}$', lw=2, color='yellowgreen')
plt.plot(data_concs["timestamp"], data_concs["GLN_i"],
         label='[Gln]$_{i}$', lw=2, color='lightcoral')
# plt.plot(data_concs["timestamp"], data_concs["GLU_im"],
#          label='[Glu]$_{im}$', lw=2, color='blueviolet')
plt.plot(data_concs["timestamp"], data_concs["KET_b"],
         label='[KetB]$_{e}$', lw=2, color='darkorange')

# Format
plt.xlabel('Time after bolus (min)')
plt.ylabel('Concentration (mM)')
plt.xlim(0, 400)
# plt.xticks([0, 50, 100, 150, 200])
leg = plt.legend(framealpha=1, fontsize=7, edgecolor="black",
           bbox_to_anchor=(1.02, 0.42), loc="center left")
plt.title("Pool concentrations")
plt.grid(alpha=0.4, zorder=1)
leg.set_in_layout(False)


# Subplot
plt.subplot(1, 3, 3)

# Plot all concentrations
plt.plot(data_concs["timestamp"], data_concs["GABA_i"],
         label='[GABA]$_{i}$', lw=2, color='orangered')
plt.plot(data_concs["timestamp"], data_concs["GLU_a"],
         label='[Glu]$_{a}$', lw=2, color='deepskyblue')
plt.plot(data_concs["timestamp"], data_concs["GLN_i"],
         label='[Gln]$_{i}$', lw=2, color='lightcoral')
plt.plot(data_concs["timestamp"], data_concs["GLU_i"],
         label='[Glu]$_{i}$', lw=2, color='dodgerblue')
plt.plot(data_concs["timestamp"], data_concs["GABA_v"],
         label='[GABA]$_{v}$', lw=2, color='maroon')
plt.plot(data_concs["timestamp"], data_concs["KET_b"],
         label='[KET]$_{b}$', lw=2, color='darkorange')

# Format
plt.xlabel('Time after bolus (min)')
plt.ylabel('Concentration (mM)')
plt.xlim(0, 400)
# plt.xticks([0, 50, 100, 150, 200])
leg = plt.legend(framealpha=1, fontsize=7, edgecolor="black",
           bbox_to_anchor=(0.59, 0.72), loc="center left")
plt.title("(Small) pool concentrations     ")
plt.grid(alpha=0.4, zorder=1)
leg.set_in_layout(False)

# Save
plt.tight_layout(w_pad=5.5)
plt.savefig(OUTDIR + f"SI_fig_timecourses_all.pdf", dpi=300, transparent=True)


# %%
# ===================================================================
# Figure 3: MCA
# ===================================================================

# Open MCA results
data_mca_conc_ctrl = pd.read_csv(OUTDIR + f"model_mca_concentration.csv");

# Figure
plt.figure(figsize=(8.25, 3.8))

# Concentration control
# ----------

# Transform
data_mca_conc_ctrl.set_index("state", inplace=True) # Set indexes
data_mca_conc_ctrl = data_mca_conc_ctrl \
    .loc[:, ["c_vpmas", "k_syn_e", "k_syn_i", "Vmax_GAD65", "Vmax_GAD67", "Vmax_GT", "Vmax_GDH", "Vmax_GS", "KM_GAD65", "KM_GAD67", "KM_GT", "KM_GDH", "KM_GS", "KI_GS"]] # Keep only relevant columns
data_mca_conc_ctrl = data_mca_conc_ctrl \
    .loc[["GLU_e(t)", "GLU_i(t)", "GLU_a(t)", "GLN_e(t)", "GLN_i(t)","GLN_a(t)", "GABA_i(t)", "GABA_v(t)"], :]  # Keep only relevant rows

# Subplot
# plt.subplot(1, 2, 1)

# Annot data
annot_ctrl = np.where(~np.isclose(data_mca_conc_ctrl, 0, atol=2e-1), data_mca_conc_ctrl.round(1).astype(str), "")

# Plot heatmap
sns.heatmap(data_mca_conc_ctrl, annot=annot_ctrl, fmt="", cmap="seismic", square=True,
            vmin=-25, vmax=25, annot_kws={"size": 8},
            cbar_kws={"label": "Concentration control coefficient", "shrink": 1})

# Format
xticks = ["V$_{PMAS}$", "k$_{syn}^{e}$", "k$_{syn}^{i}$", "V$_{max}^{GAD65}$", "V$_{max}^{GAD67}$",
          "V$_{max}^{GT}$", "V$_{max}^{GDH}$", "V$_{max}^{GS}$", "K$_M^{GAD65}$", "K$_M^{GAD67}$", "K$_M^{GT}$",
          "K$_M^{GDH}$", "K$_M^{GS}$", "K$_I^{GS}$", ]
yticks = ["\n\nGLU$_{e}$", "\n\nGLU$_{i}$", "\n\nGLU$_{a}$", "\n\nGLN$_{e}$",
          "\n\nGLN$_{i}$","\n\nGLN$_{a}$", "\n\nGABA$_{i}^{c}$", "\n\nGABA$_{i}^{v}$"]
# plt.title("Concentration control")
plt.xticks(np.arange(len(xticks)), xticks, rotation=60, ha="left")
plt.yticks(np.arange(len(yticks)), yticks, rotation=0, va="center")

plt.xlabel("Parameter")
# plt.ylabel("Metabolite pool")
plt.ylabel("Metabolite pool")
plt.grid(alpha=0.5)

for spine in plt.gca().spines.values():
    spine.set_visible(True)     # make sure they're visible
    spine.set_linewidth(0.5)
    spine.set_color("black")

# Save
plt.tight_layout(rect=[0, -0.01, 1, 1.05])
plt.savefig(OUTDIR + f"fig_mca_concentration.pdf", dpi=300, transparent=True)
