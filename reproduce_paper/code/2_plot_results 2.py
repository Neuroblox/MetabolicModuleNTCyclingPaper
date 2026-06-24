"""

@author: Botond B. Antal

June 2026

This script plots the simulated results.

"""

# %%

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import h5py

# %%
# ===================================================================
# Setup
# ===================================================================

# Directories
OUTDIR = "" + "results/"   #TODO: insert your filepath here before results/

# rcParams
plt.rcParams.update({'font.size': 10})

# Experiment data
t_meas = 67
t_meas_error = 4.1
exp_means = {"GLU": -10.6, "GABA": -36.9}
exp_errors = {"GLU": 1.2*1.96, "GABA": 4.2*1.96}  # 95% CI!
exp_scaling = {"GLU": 11, "GABA": 0.83}

# %%
# ===================================================================
# Load simulation results with replicates
# ===================================================================

# Initialize dataframe
df_list_params = []
df_list_conc = []
df_list_conc_norm = []
df_list_flux = []
df_list_flux_norm = []
df_list_u0 = []

# Open conc data and make long format dataframe for each run
with h5py.File(OUTDIR + "model_multirun.h5", "r") as f:

    # Concentration group
    grp_conc = f["concentrations"]

    # Get run names
    run_names = list(grp_conc.keys())

    # Iterate over runs
    for run in run_names:
        
        # Extract data
        t = grp_conc[run]["t"][:]
        var_names = [item.decode() for item in grp_conc[run]["var_names"]]
        Y = grp_conc[run]["concs"][:]

        # Create dataframe for this run
        df_run = pd.DataFrame(Y, columns=var_names)
        df_run["timestamp"] = t
        df_run["run"] = run

        # Append to list
        df_list_conc.append(df_run)

        # Normalize with first timepoint and convert to percent change
        df_run_norm = df_run.copy()
        for var in var_names:
            df_run_norm[var] = 100 * (df_run[var] - df_run[var][0]) / df_run[var][0]
            df_run_norm["timestamp"] = t

        # Add combined columns
        # Glutamate
        cols = ["GLU_e", "GLU_i", "GLU_a"]
        df_run_norm["GLU_tot"] = 100 * (df_run[cols].sum(axis=1) - df_run[cols].sum(axis=1)[0]) / \
            df_run[cols].sum(axis=1)[0]

        # GABA
        cols = ["GABA_i", "GABA_v"]
        df_run_norm["GABA_tot"] = 100 * (df_run[cols].sum(axis=1) - df_run[cols].sum(axis=1)[0]) / \
             df_run[cols].sum(axis=1)[0]

        # Append normalized dataframe to list
        df_list_conc_norm.append(df_run_norm)

    # Flux group
    grp_flux = f["fluxes"]

    # Run names
    run_names = list(grp_flux.keys())

    for run in run_names:

        # Extract data
        t = grp_flux[run]["t"][:]
        reaction_names = [item.decode() for item in grp_flux[run]["reaction_names"]]
        Y = grp_flux[run]["rates"][:]   # (reactions, time)

        # Create dataframe for this run
        df_run = pd.DataFrame(Y.T, columns=reaction_names)
        df_run["timestamp"] = t
        df_run["run"] = run

        # Append to list
        df_list_flux.append(df_run)

        # Normalize with first timepoint and convert to percent change
        df_run_norm = df_run.copy()
        for reaction in reaction_names:
            df_run_norm[reaction] = 100 * (df_run[reaction] - df_run[reaction][0]) / df_run[reaction][0]
            df_run_norm["timestamp"] = t

        # Append normalized dataframe to list
        df_list_flux_norm.append(df_run_norm)

    # Parameter group
    grp_params = f["parameters"]

    # Run names
    run_names = list(grp_params.keys())

    # Iterate over runs
    for run in run_names:
        
        # Extract data
        par_names = [item.decode() for item in grp_params[run]["par_names"]]
        values = grp_params[run]["pars"][:]

        # Create dataframe for this run
        df_run = pd.DataFrame(values[:, None].T, columns=par_names)
        df_run["run"] = run

        # Append to list
        df_list_params.append(df_run)

    # Initial conditions group
    grp_u0 = f["u0"]

    # Run names
    run_names = list(grp_u0.keys())

    # Iterate over runs
    for run in run_names:
        
        # Extract data
        var_names = [item.decode() for item in grp_u0[run]["var_names"]]
        values = grp_u0[run]["u0"][:]

        # Create dataframe for this run
        df_run = pd.DataFrame(values[:, None].T, columns=var_names)
        df_run["run"] = run

        # Append to list
        df_list_u0.append(df_run)

# Concat dataframes
df_params = pd.concat(df_list_params, ignore_index=True)
df_conc = pd.concat(df_list_conc, ignore_index=True)
df_conc_norm = pd.concat(df_list_conc_norm, ignore_index=True)
df_flux = pd.concat(df_list_flux, ignore_index=True)
df_flux_norm = pd.concat(df_list_flux_norm, ignore_index=True)
df_u0 = pd.concat(df_list_u0, ignore_index=True)

# %%
# ===================================================================
# Describe the results
# ===================================================================

# Take the mean across runs for each timepoint
df_flux_mean = df_flux.drop("run", axis=1).groupby("timestamp").mean().reset_index()
df_conc_mean = df_conc.drop("run", axis=1).groupby("timestamp").mean().reset_index()
df_conc_norm_mean = df_conc_norm.drop("run", axis=1).groupby("timestamp").mean().reset_index()

# Relative concentrations at t_meas
y_tmeas = df_conc_norm_mean.iloc[df_conc_norm_mean['timestamp'].sub(t_meas).abs().idxmin()]

# Print values
print(f"CMRglc starts from {df_flux_mean['CMRglc'][0]:.3f} mM/min "
      f"and is lowest at {df_flux_mean['CMRglc'].min():.3f} mM/min "
      f"which occurs at t={df_flux_mean['timestamp'][df_flux_mean['CMRglc'].idxmin()]:.2f}) min")
print(f"CMRket starts from {df_flux_mean['Ketone utilization'][0]:.3f} mM/min "
      f"and is highest at {df_flux_mean['Ketone utilization'].max():.3f} mM/min "
      f"which occurs at t={df_flux_mean['timestamp'][df_flux_mean['Ketone utilization'].idxmax()]:.2f} min")
print(f"PMAS_e starts from {df_flux_mean['PMAS in e'][0]:.3f} mM/min "
      f"and is lowest at {df_flux_mean['PMAS in e'].min():.3f} mM/min "
      f"which occurs at t={df_flux_mean['timestamp'][df_flux_mean['PMAS in e'].idxmin()]:.2f} min")
print(f"PMAS_i starts from {df_flux_mean['PMAS in i'][0]:.3f} mM/min "
      f"and is lowest at {df_flux_mean['PMAS in i'].min():.3f} mM/min "
      f"which occurs at t={df_flux_mean['timestamp'][df_flux_mean['PMAS in i'].idxmin()]:.2f} min")
print(f"VGDH starts from {df_flux_mean['GDH'][0]:.3f} mM/min "
      f"and is lowest at {df_flux_mean['GDH'].min():.3f} mM/min "
      f"which occurs at t={df_flux_mean['timestamp'][df_flux_mean['GDH'].idxmin()]:.2f} min")
print(f"VGS starts from {df_flux_mean['GS'][0]:.3f} mM/min "
      f"and is lowest at {df_flux_mean['GS'].min():.3f} mM/min "
      f"which occurs at t={df_flux_mean['timestamp'][df_flux_mean['GS'].idxmin()]:.2f} min")
print(f"VGAD65 starts from {df_flux_mean['GAD65'][0]:.3f} mM/min "
      f"and is lowest at {df_flux_mean['GAD65'].min():.3f} mM/min "
      f"which occurs at t={df_flux_mean['timestamp'][df_flux_mean['GAD65'].idxmin()]:.2f} min")
print(f"VGAD67 starts from {df_flux_mean['GAD67'][0]:.3f} mM/min "
      f"and is lowest at {df_flux_mean['GAD67'].min():.3f} mM/min "
      f"which occurs at t={df_flux_mean['timestamp'][df_flux_mean['GAD67'].idxmin()]:.2f} min")
print(f"VGT starts from {df_flux_mean['GT'][0]:.3f} mM/min "
      f"and is lowest at {df_flux_mean['GT'].min():.3f} mM/min "
      f"which occurs at t={df_flux_mean['timestamp'][df_flux_mean['GT'].idxmin()]:.2f} min")

print("\n####\n")     
# Print values
print(f"GLU_e starts from {df_conc_mean['GLU_e'][0]:.3f} mM "
      f"and is lowest at {df_conc_mean['GLU_e'].min():.3f} mM "
      f"(-{100 * (df_conc_mean['GLU_e'][0] - df_conc_mean['GLU_e'].min()) / df_conc_mean['GLU_e'][0]:.1f}%) "
      f"which occurs at t={df_conc_mean['timestamp'][df_conc_mean['GLU_e'].idxmin()]:.2f} min")
print(f"GLU_a starts from {df_conc_mean['GLU_a'][0]:.3f} mM "
      f"and is lowest at {df_conc_mean['GLU_a'].min():.3f} mM "
      f"(-{100 * (df_conc_mean['GLU_a'][0] - df_conc_mean['GLU_a'].min()) / df_conc_mean['GLU_a'][0]:.1f}%) "
      f"which occurs at t={df_conc_mean['timestamp'][df_conc_mean['GLU_a'].idxmin()]:.2f} min")
print(f"GLU_a starts from {df_conc_mean['GLU_a'][0]:.3f} mM "
      f"and is highest at {df_conc_mean['GLU_a'].max():.3f} mM "
      f"(-{100 * (df_conc_mean['GLU_a'][0] - df_conc_mean['GLU_a'].max()) / df_conc_mean['GLU_a'][0]:.1f}%) "
      f"which occurs at t={df_conc_mean['timestamp'][df_conc_mean['GLU_a'].idxmax()]:.2f} min")
print(f"GLN_a starts from {df_conc_mean['GLN_a'][0]:.3f} mM "
      f"and is highest at {df_conc_mean['GLN_a'].max():.3f} mM "
      f"(-{100 * (df_conc_mean['GLN_a'][0] - df_conc_mean['GLN_a'].max()) / df_conc_mean['GLN_a'][0]:.1f}%) "
      f"which occurs at t={df_conc_mean['timestamp'][df_conc_mean['GLN_a'].idxmax()]:.2f} min")
print(f"GABA_i starts from {df_conc_mean['GABA_i'][0]:.3f} mM "
      f"and is lowest at {df_conc_mean['GABA_i'].min():.3f} mM "
      f"(-{100 * (df_conc_mean['GABA_i'][0] - df_conc_mean['GABA_i'].min()) / df_conc_mean['GABA_i'][0]:.1f}%) "
      f"which occurs at t={df_conc_mean['timestamp'][df_conc_mean['GABA_i'].idxmin()]:.2f} min")
print(f"GABA_v starts from {df_conc_mean['GABA_v'][0]:.3f} mM "
      f"and is lowest at {df_conc_mean['GABA_v'].min():.3f} mM "
      f"(-{100 * (df_conc_mean['GABA_v'][0] - df_conc_mean['GABA_v'].min()) / df_conc_mean['GABA_v'][0]:.1f}%) "
      f"which occurs at t={df_conc_mean['timestamp'][df_conc_mean['GABA_v'].idxmin()]:.2f} min")
print(f"KET_b starts from {df_conc_mean['KET_b'][0]:.3f} mM "
      f"and is highest at {df_conc_mean['KET_b'].max():.3f} mM "
      f"(-{100 * (df_conc_mean['KET_b'][0] - df_conc_mean['KET_b'].max()) / df_conc_mean['KET_b'][0]:.1f}%) "
      f"which occurs at t={df_conc_mean['timestamp'][df_conc_mean['KET_b'].idxmax()]:.2f} min")

# Print total (relative) changes at t_meas
print(f"Glutamate: {y_tmeas['GLU_tot']:.1f}%")
print(f"GABA: {y_tmeas['GABA_tot']:.1f}%")

# %%
# ===================================================================
# Figure 2: ketone metabolism
# ===================================================================

# Load data
data_bloodbhb_datapoints = pd.read_csv(OUTDIR + "martin-arrowsmith_etal_blood_bhb_timecourse.csv")
data_bloodbhb_timeseries = pd.read_csv(OUTDIR + f"model_blood_bhb_input_timeseries.csv")
data_brainbhb_datapoints = pd.read_csv(OUTDIR + "mujica-parodi_etal_brain_bhb_timeseries.csv")

# Take the max of the mean ketone time-course across runs
ket_b_max = df_conc.groupby("timestamp")["KET_b"].mean().max()

# Figure
plt.figure(figsize=(8.25, 3.3))

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
    lw=1.5, label='Fitted (double\nexponential)',
    color='crimson', zorder=3)
plt.xlabel('Time after bolus (min)')
plt.ylabel(r'Blood D-$\beta$HB concentration (mM)')
# plt.title(r"Blood D-$\beta$HB")
plt.axhline(0, color='gray', lw=1, ls='-')
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
sns.lineplot(data=df_conc, x="timestamp", y="KET_b",
    errorbar=('sd'), label='Simulated', lw=1.5, color='dodgerblue')
plt.xlabel('Time after bolus (min)')
plt.ylabel(r'Brain D-$\beta$HB concentration (mM)')
# plt.title(r"Brain D-$\beta$HB")
plt.axhline(0, color='gray', lw=1, ls='-')
plt.xlim(0, 220)
plt.xticks([0, 50, 100, 150, 200])
plt.legend(framealpha=1, fontsize=8, edgecolor="black")
plt.grid(alpha=0.4, zorder=1)

# Subplot 3
plt.subplot(1, 3, 3)
plt.plot(
    data_bloodbhb_timeseries['time'],
    data_bloodbhb_timeseries['concentration']/data_bloodbhb_timeseries['concentration'].max(),
    lw=1.5, label='Blood (input)', color='crimson', zorder=2)
sns.lineplot(x=df_conc["timestamp"], y=df_conc["KET_b"]/ket_b_max,
    errorbar=('sd'), label='Brain (simulated)', lw=1.5, color='dodgerblue')
plt.xlabel('Time after bolus (min)')
plt.ylabel('Concentration (relative)')
# plt.title("Normalized\n" + r'Blood & Brain D-$\beta$HB')
plt.axhline(0, color='gray', lw=1, ls='-')
plt.xlim([0, 100])
plt.ylim([plt.gca().get_ylim()[0], 1.12])
plt.legend(framealpha=1, fontsize=8, edgecolor="black")
plt.grid(alpha=0.4, zorder=0)

# Save
plt.tight_layout()
plt.savefig(OUTDIR + f"figs/fig_ketone_pk.pdf", dpi=300, transparent=True)

# %%
# ===================================================================
# Figure 3: neurotransmitter metabolism
# ==================================================================

# Figure
plt.figure(figsize=(8.25, 3.3))

# Fluxes (A)
# --------------

# Subplot
plt.subplot(1, 4, 1)

# Plot
sns.lineplot(data=df_flux, x="timestamp", y="CMRglc", errorbar=('sd'),
             label='CMR$_{glc}$', lw=1.5, color="#000000")
sns.lineplot(data=df_flux, x="timestamp", y="Ketone utilization", errorbar=('sd'),
             label='CMR$_{Ket}$', lw=1.5, color="mediumvioletred")
sns.lineplot(data=df_flux, x="timestamp", y="GS", errorbar=('sd'),
             label='V$_{GS}$', lw=1.5, linestyle='-', color="#44AB42F7")
sns.lineplot(data=df_flux, x="timestamp", y="PMAS in e", errorbar=('sd'),
             label='V$_{PMAS}^e$', lw=1.5, color='#0066FF')
sns.lineplot(data=df_flux, x="timestamp", y="PMAS in i", errorbar=('sd'),
             label='V$_{PMAS}^i$', lw=1.5, color="#D60000F7")


# Format
plt.axhline(0, color='gray', lw=1, ls='-')
plt.xlabel('Time after bolus (min)')
plt.ylabel('Flux (mM/min)', labelpad=1)
plt.xticks([0, 50, 100, 150, 200])
plt.xlim(0, 220)
plt.ylim([-0.02, 0.55])
plt.grid(alpha=0.4)
# plt.title("Fluxes", fontsize=10)
leg = plt.legend(framealpha=1, fontsize=7, edgecolor="black",
           bbox_to_anchor=(0.08, 0.86), loc="center left",
           ncol=2, columnspacing=0.3, handlelength=1)
leg.set_in_layout(False)

# Compartmental concentrations (B)
# --------------

# Subplot
plt.subplot(1, 4, 2)

# Plot
sns.lineplot(data=df_conc, x="timestamp", y="GLU_e",
    errorbar=('sd'), label='[Glu]$_{e}$', lw=1.5, color='#0066FF')
sns.lineplot(data=df_conc, x="timestamp", y="GLN_a",
    errorbar=('sd'), label='[Gln]$_{a}$', lw=1.5, color="#44AB42F7")
sns.lineplot(data=df_conc, x="timestamp", y="GLU_a",
    errorbar=('sd'), label='[Glu]$_{a}$', lw=1.5, color="dimgray")
sns.lineplot(data=df_conc, x="timestamp", y="GABA_i",
    errorbar=('sd'), label='[GABA]$_{i}^c$', lw=1.5, color='orangered')

# Format
plt.axhline(0, color='gray', lw=1, ls='-')
plt.xlabel('Time after bolus (min)')
plt.ylabel('Concentration (mM)', labelpad=3)
plt.xlim(0, 220)
plt.ylim([-0.5, 13])
plt.xticks([0, 50, 100, 150, 200])
leg = plt.legend(framealpha=1, fontsize=7, edgecolor="black",
           bbox_to_anchor=(0.08, 0.9), loc="center left",
           ncol=2, columnspacing=0.3, handlelength=1)
# plt.title("Pool concentrations (abs.)   ", fontsize=10)
plt.grid(alpha=0.4, zorder=1)
leg.set_in_layout(False)

# Validation with relative total concentrations (C)
# --------------

# Subplot
plt.subplot(1, 4, 3)

# Glutamate
x = df_conc_norm["timestamp"]
y = df_conc_norm["GLU_tot"]
sns.lineplot(x=x, y=y,
        errorbar=('sd'), label='[Glu]$_{tot}$ (sim.)', lw=1.5, color='#0066FF')

# GABA
x = df_conc_norm["timestamp"]
y = df_conc_norm["GABA_tot"]
sns.lineplot(x=x, y=y,
        errorbar=('sd'), label="[GABA]$_{tot}$ (sim.)", lw=1.5, color='orangered')


# Add experimental data
plt.errorbar(t_meas, exp_means['GLU'], xerr=t_meas_error, yerr=exp_errors["GLU"],
             label="[Glu]$_{tot}$ (MRS)", fmt='o', lw=1.5, color="#001AFF",
             capsize=2.5, capthick=1.5, markersize=2)
plt.errorbar(t_meas, exp_means['GABA'], xerr=t_meas_error, yerr=exp_errors["GABA"],
             label="[GABA]$_{tot}$ (MRS)", fmt='o', lw=1.5, color="#BF0000",
             capsize=2.5, capthick=1.5, markersize=2)
plt.axvline(t_meas, color='gray', lw=1, ls='--', zorder=-1)

# Formatting
plt.axhline(0, color='gray', lw=1, ls='-')
plt.xlabel('Time after bolus (min)')
plt.ylabel(r"$\Delta$" + 'concentration (%)', labelpad=-5)
plt.xticks([0, 50, 100, 150, 200])
plt.xlim(0, 220)
plt.ylim([-110, 13])
leg = plt.legend(framealpha=1, edgecolor="black", fontsize=7,
                 bbox_to_anchor=(0.01, 0.16), loc="center left")
plt.grid(alpha=0.4)
leg.set_in_layout(False)

# Relative fluxes (D)
# --------------

# Subplot
plt.subplot(1, 4, 4)

# Plot
sns.lineplot(data=df_flux_norm, x="timestamp", y="GLU synaptic flux", errorbar=('sd'),
             label='V$_{syn}^e$', lw=1.5, color="#0066FF")
sns.lineplot(data=df_flux_norm, x="timestamp", y="GABA synaptic flux", errorbar=('sd'),
             label='V$_{syn}^i$', lw=1.5, color="#D60000F7")


# Format
plt.axhline(0, color='gray', lw=1, ls='-')
plt.xlabel('Time after bolus (min)')
plt.ylabel(r"$\Delta$" +'flux (%)', labelpad=-5)
plt.xticks([0, 50, 100, 150, 200])
plt.xlim(0, 220)
plt.ylim([-15, 1.5])
plt.grid(alpha=0.4)
leg = plt.legend(framealpha=1, fontsize=7, edgecolor="black",
           bbox_to_anchor=(0.15, 0.07), loc="center left",
           ncol=2, columnspacing=0.3, handlelength=1)
leg.set_in_layout(False)

# Save
plt.tight_layout(w_pad=0.2)
plt.savefig(OUTDIR + f"figs/fig_timecourses_conf.pdf",
            dpi=300, transparent=True)

# %%
# ===================================================================
# SI figure: time-series
# ===================================================================

# Figure
plt.figure(figsize=(8.25, 3.3))

# Fluxes
# -----------

# Subplot
plt.subplot(1, 3, 1)

# Plot all fluxes
sns.lineplot(data=df_flux, x="timestamp", y="CMRglc", errorbar=('sd'),
                label='CMR$_{glc}$', lw=1.5, color="#000000")
sns.lineplot(data=df_flux, x="timestamp", y="Ketone utilization", errorbar=('sd'),
                label='CMR$_{Ket}$', lw=1.5, color="mediumvioletred")
sns.lineplot(data=df_flux, x="timestamp", y="PMAS in e", errorbar=('sd'),
                label='PMAS$_e$', lw=1.5, color='navy')
sns.lineplot(data=df_flux, x="timestamp", y="PMAS in i", errorbar=('sd'),
                label='PMAS$_i$', lw=1.5, color="maroon")
sns.lineplot(data=df_flux, x="timestamp", y="GLU synaptic flux", errorbar=('sd'),
                label='V$_{syn}^e$', lw=1.5, color="#0066FF")
sns.lineplot(data=df_flux, x="timestamp", y="GABA synaptic flux", errorbar=('sd'),
                label='V$_{syn}^i$', lw=1.5, color="#D60000F7")
sns.lineplot(data=df_flux, x="timestamp", y="GDH", errorbar=('sd'),
                label='V$_{GDH}$', lw=1.5, color="#006B26FF")
sns.lineplot(data=df_flux, x="timestamp", y="GS", errorbar=('sd'),
                label='V$_{GS}$', lw=1.5, color='#44AB42F7')
sns.lineplot(data=df_flux, x="timestamp", y="GAD65", errorbar=('sd'),
                label='V$_{GAD65}$', lw=1.5, color="#DA6D85F7")
sns.lineplot(data=df_flux, x="timestamp", y="GAD67", errorbar=('sd'),
                label='V$_{GAD67}$', lw=1.5, color="#D66DDAF7")
sns.lineplot(data=df_flux, x="timestamp", y="GT", errorbar=('sd'),
                label='V$_{GT}$', lw=1.5, color="#4286ABF7")


# Format
plt.axhline(0, color='gray', lw=1, ls='-')
plt.xlabel('Time after bolus (min)')
plt.ylabel('Flux (mM/min)')
plt.xlim(0, 400)
plt.xticks([0, 100, 200, 300, 400])
plt.grid(alpha=0.4)
leg = plt.legend(framealpha=1, fontsize=7, edgecolor="black",
           bbox_to_anchor=(1.02, 0.42), loc="center left")
leg.set_in_layout(False)

# Concentrations
# -----------

# Subplot
plt.subplot(1, 3, 2)

# Plot all concentrations
sns.lineplot(data=df_conc, x="timestamp", y="GLU_e",
    errorbar=('sd'), label='[Glu]$_{e}$', lw=1.5, color='#0066FF')
sns.lineplot(data=df_conc, x="timestamp", y="GLN_a",
    errorbar=('sd'), label='[Gln]$_{a}$', lw=1.5, color="#44AB42F7")
sns.lineplot(data=df_conc, x="timestamp", y="GLU_a",
    errorbar=('sd'), label='[Glu]$_{a}$', lw=1.5, color='dimgray')
sns.lineplot(data=df_conc, x="timestamp", y="GABA_i",
    errorbar=('sd'), label='[GABA]$_{i}^c$', lw=1.5, color='orangered')
sns.lineplot(data=df_conc, x="timestamp", y="GABA_v",
    errorbar=('sd'), label='[GABA]$_{i}^v$', lw=1.5, color='maroon')
sns.lineplot(data=df_conc, x="timestamp", y="GLU_i",
    errorbar=('sd'), label='[Glu]$_{i}$', lw=1.5, color='dodgerblue')
sns.lineplot(data=df_conc, x="timestamp", y="GLN_e",
    errorbar=('sd'), label='[Gln]$_{e}$', lw=1.5, color='yellowgreen')
sns.lineplot(data=df_conc, x="timestamp", y="GLN_i",
    errorbar=('sd'), label='[Gln]$_{i}$', lw=1.5, color='lightcoral')
sns.lineplot(data=df_conc, x="timestamp", y="KET_b",
    errorbar=('sd'), label='[KetB]$_{e}$', lw=1.5, color='darkorange')


# Format
plt.axhline(0, color='gray', lw=1, ls='-')
plt.xlabel('Time after bolus (min)')
plt.ylabel('Concentration (mM)')
plt.xlim(0, 400)
plt.xticks([0, 100, 200, 300, 400])
leg = plt.legend(framealpha=1, fontsize=7, edgecolor="black",
           bbox_to_anchor=(1.02, 0.42), loc="center left")
plt.grid(alpha=0.4, zorder=1)
leg.set_in_layout(False)

# Subplot
plt.subplot(1, 3, 3)

# Plot all concentrations
sns.lineplot(data=df_conc, x="timestamp", y="GABA_i",
    errorbar=('sd'), label='[GABA]$_{i}^c$', lw=1.5, color='orangered')
sns.lineplot(data=df_conc, x="timestamp", y="GABA_v",
    errorbar=('sd'), label='[GABA]$_{i}^v$', lw=1.5, color='maroon')
sns.lineplot(data=df_conc, x="timestamp", y="GLU_a",
    errorbar=('sd'), label='[Glu]$_{a}$', lw=1.5, color='dimgray')
sns.lineplot(data=df_conc, x="timestamp", y="GLU_i",
    errorbar=('sd'), label='[Glu]$_{i}$', lw=1.5, color='dodgerblue')
sns.lineplot(data=df_conc, x="timestamp", y="GLN_e",
    errorbar=('sd'), label='[Gln]$_{e}$', lw=1.5, color='yellowgreen')
sns.lineplot(data=df_conc, x="timestamp", y="GLN_i",
    errorbar=('sd'), label='[Gln]$_{i}$', lw=1.5, color='lightcoral')
sns.lineplot(data=df_conc, x="timestamp", y="KET_b",
    errorbar=('sd'), label='[KetB]$_{e}$', lw=1.5, color='darkorange')

# Format
plt.axhline(0, color='gray', lw=1, ls='-')
plt.xlabel('Time after bolus (min)')
plt.ylabel('Concentration (mM)')
plt.xlim(0, 400)
plt.xticks([0, 100, 200, 300, 400])
leg = plt.legend(framealpha=1, fontsize=7, edgecolor="black",
           bbox_to_anchor=(0.42, 0.72), loc="center left")
plt.grid(alpha=0.4, zorder=1)
leg.set_in_layout(False)

# Save
plt.tight_layout(w_pad=5.5)
plt.savefig(OUTDIR + f"figs/SI_fig_timecourses_all.pdf", dpi=300, transparent=True)


# %%
# ===================================================================
# SI figure: times-series (scaled to compartmental concentrations)
# ===================================================================

# Scaling factors
vol_e = 0.56
vol_i = 0.14
vol_a = 0.2

# Figure
plt.figure(figsize=(8.25, 3.3))

# Fluxes
# -----------

# Subplot
plt.subplot(1, 3, 1)

# Plot all fluxes
sns.lineplot(x=df_flux["timestamp"], y=df_flux["CMRglc"], errorbar=('sd'),
                label='CMR$_{glc}$', lw=1.5, color="#000000")
sns.lineplot(x=df_flux["timestamp"], y=df_flux["Ketone utilization"], errorbar=('sd'),
                label='CMR$_{Ket}$', lw=1.5, color="mediumvioletred")
sns.lineplot(x=df_flux["timestamp"], y=df_flux["PMAS in e"]/vol_e, errorbar=('sd'),
                label='PMAS$_e$', lw=1.5, color='navy')
sns.lineplot(x=df_flux["timestamp"], y=df_flux["PMAS in i"]/vol_i, errorbar=('sd'),
                label='PMAS$_i$', lw=1.5, color="maroon")
sns.lineplot(x=df_flux["timestamp"], y=df_flux["GLU synaptic flux"]/vol_e, errorbar=('sd'),
                label='V$_{syn}^e$', lw=1.5, color="#0066FF")
sns.lineplot(x=df_flux["timestamp"], y=df_flux["GABA synaptic flux"]/vol_i, errorbar=('sd'),
                label='V$_{syn}^i$', lw=1.5, color="#D60000F7")
sns.lineplot(x=df_flux["timestamp"], y=df_flux["GDH"]/vol_a, errorbar=('sd'),
                label='V$_{GDH}$', lw=1.5, color="#006B26FF")
sns.lineplot(x=df_flux["timestamp"], y=df_flux["GS"]/vol_a, errorbar=('sd'),
                label='V$_{GS}$', lw=1.5, color='#44AB42F7')
sns.lineplot(x=df_flux["timestamp"], y=df_flux["GAD65"]/vol_i, errorbar=('sd'),
                label='V$_{GAD65}$', lw=1.5, color="#DA6D85F7")
sns.lineplot(x=df_flux["timestamp"], y=df_flux["GAD67"]/vol_i, errorbar=('sd'),
                label='V$_{GAD67}$', lw=1.5, color="#D66DDAF7")
sns.lineplot(x=df_flux["timestamp"], y=df_flux["GT"]/vol_i, errorbar=('sd'),
                label='V$_{GT}$', lw=1.5, color="#4286ABF7")


# Format
plt.axhline(0, color='gray', lw=1, ls='-')
plt.xlabel('Time after bolus (min)')
plt.ylabel('Flux (mM/min)')
plt.xlim(0, 400)
plt.xticks([0, 100, 200, 300, 400])
plt.grid(alpha=0.4)
leg = plt.legend(framealpha=1, fontsize=7, edgecolor="black",
           bbox_to_anchor=(1.02, 0.42), loc="center left")
leg.set_in_layout(False)

# Concentrations
# -----------

# Subplot
plt.subplot(1, 3, 2)

# Plot all concentrations
sns.lineplot(x=df_conc["timestamp"], y=df_conc["GLU_e"]/vol_e,
    errorbar=('sd'), label='[Glu]$_{e}$', lw=1.5, color='#0066FF')
sns.lineplot(x=df_conc["timestamp"], y=df_conc["GLN_a"]/vol_a,
    errorbar=('sd'), label='[Gln]$_{a}$', lw=1.5, color="#44AB42F7")
sns.lineplot(x=df_conc["timestamp"], y=df_conc["GLU_a"]/vol_a,
    errorbar=('sd'), label='[Glu]$_{a}$', lw=1.5, color='dimgray')
sns.lineplot(x=df_conc["timestamp"], y=df_conc["GABA_i"]/vol_i,
    errorbar=('sd'), label='[GABA]$_{i}^c$', lw=1.5, color='orangered')
sns.lineplot(data=df_conc, x="timestamp", y="GABA_v",
    errorbar=('sd'), label='[GABA]$_{i}^v$', lw=1.5, color='maroon')
sns.lineplot(x=df_conc["timestamp"], y=df_conc["GLU_i"]/vol_i,
    errorbar=('sd'), label='[Glu]$_{i}$', lw=1.5, color='dodgerblue')
sns.lineplot(x=df_conc["timestamp"], y=df_conc["GLN_e"]/vol_e,
    errorbar=('sd'), label='[Gln]$_{e}$', lw=1.5, color='yellowgreen')
sns.lineplot(x=df_conc["timestamp"], y=df_conc["GLN_i"]/vol_i,
    errorbar=('sd'), label='[Gln]$_{i}$', lw=1.5, color='lightcoral')
sns.lineplot(x=df_conc["timestamp"], y=df_conc["KET_b"],
    errorbar=('sd'), label='[KetB]$_{e}$', lw=1.5, color='darkorange')

# Format
plt.axhline(0, color='gray', lw=1, ls='-')
plt.xlabel('Time after bolus (min)')
plt.ylabel('Concentration (mM)')
plt.xlim(0, 400)
plt.xticks([0, 100, 200, 300, 400])
leg = plt.legend(framealpha=1, fontsize=7, edgecolor="black",
           bbox_to_anchor=(1.02, 0.42), loc="center left")
plt.grid(alpha=0.4, zorder=1)
leg.set_in_layout(False)

# Subplot
plt.subplot(1, 3, 3)

# Plot all concentrations
sns.lineplot(x=df_conc["timestamp"], y=df_conc["GABA_i"]/vol_i,
    errorbar=('sd'), label='[GABA]$_{i}^c$', lw=1.5, color='orangered')
sns.lineplot(data=df_conc, x="timestamp", y="GABA_v",
    errorbar=('sd'), label='[GABA]$_{i}^v$', lw=1.5, color='maroon')
sns.lineplot(x=df_conc["timestamp"], y=df_conc["GLU_a"]/vol_a,
    errorbar=('sd'), label='[Glu]$_{a}$', lw=1.5, color='dimgray')
sns.lineplot(x=df_conc["timestamp"], y=df_conc["GLU_i"]/vol_i,
    errorbar=('sd'), label='[Glu]$_{i}$', lw=1.5, color='dodgerblue')
sns.lineplot(x=df_conc["timestamp"], y=df_conc["GLN_e"]/vol_e,
    errorbar=('sd'), label='[Gln]$_{e}$', lw=1.5, color='yellowgreen')
sns.lineplot(x=df_conc["timestamp"], y=df_conc["GLN_i"]/vol_i,
    errorbar=('sd'), label='[Gln]$_{i}$', lw=1.5, color='lightcoral')
sns.lineplot(x=df_conc["timestamp"], y=df_conc["KET_b"],
    errorbar=('sd'), label='[KetB]$_{e}$', lw=1.5, color='darkorange')

# Format
plt.axhline(0, color='gray', lw=1, ls='-')
plt.xlabel('Time after bolus (min)')
plt.ylabel('Concentration (mM)')
plt.xlim(0, 400)
plt.xticks([0, 100, 200, 300, 400])
leg = plt.legend(framealpha=1, fontsize=7, edgecolor="black",
           bbox_to_anchor=(0.42, 0.72), loc="center left")
plt.grid(alpha=0.4, zorder=1)
leg.set_in_layout(False)

# Save
plt.tight_layout(w_pad=5.5)
plt.savefig(OUTDIR + f"figs/SI_fig_timecourses_all_compartmental.pdf",
      dpi=300, transparent=True)

# %%
# ===================================================================
# Figure 4: MCA
# ===================================================================

# Open MCA results
data_mca_conc_ctrl = pd.read_csv(OUTDIR + f"model_mca_concentration.csv");

# Settings
vmin = -10.1
vmax = 10.1

# Figure
plt.figure(figsize=(8.25, 4.))

# Transform data for plotting
df_plot = data_mca_conc_ctrl \
    .set_index("state") \
    .loc[
        ["GLU_e(t)", "GLU_i(t)", "GLU_a(t)", "GLN_e(t)",
        "GLN_i(t)","GLN_a(t)", "GABA_i(t)", "GABA_v(t)"],
        ["c_vpmas",
        "Vmax_GAD65", "Vmax_GAD67", "Vmax_GT", "Vmax_GDH", "Vmax_GS", "KM_GAD65",
        "KM_GAD67", "KM_GT", "KM_GDH", "h_GDH", "KM_GS", "KI_GS",  "k_syn_e", "k_syn_i"]
        ]

# Annot data
annot_ctrl = np.where(~np.isclose(df_plot, 0, atol=2e-1), df_plot.round(1).astype(str), "")

# Plot heatmap
sns.heatmap(df_plot, annot=annot_ctrl, fmt="", cmap="seismic", square=True,
            vmin=vmin, vmax=vmax, annot_kws={"size": 7},
            cbar_kws={"label": "Concentration control coefficient", "shrink": 1,
                "ticks": np.arange(vmin+0.1, vmax+0.9, 5)})

# Format
xticks = ["V$_{PMAS}$", "V$_{max}^{GAD65}$", "V$_{max}^{GAD67}$",
          "V$_{max}^{GT}$", "V$_{max}^{GDH}$", "V$_{max}^{GS}$", "K$_M^{GAD65}$", "K$_M^{GAD67}$", "K$_M^{GT}$",
          "K$_M^{GDH}$", "h$_{GDH}$", "K$_M^{GS}$", "K$_I^{GS}$",
          "k$_{syn}^{e}$", "k$_{syn}^{i}$"]
yticks = ["\n\nGLU$_{e}$", "\n\nGLU$_{i}$", "\n\nGLU$_{a}$", "\n\nGLN$_{e}$",
          "\n\nGLN$_{i}$","\n\nGLN$_{a}$", "\n\nGABA$_{i}^{c}$", "\n\nGABA$_{i}^{v}$"]

# plt.title("Concentration control")
plt.xticks(np.arange(len(xticks) + 1), xticks + [None], rotation=60, ha="left")
plt.yticks(np.arange(len(yticks) + 1), yticks + [None], rotation=0, va="center")

plt.xlabel("Parameter")
plt.ylabel("Metabolite pool")
plt.grid(alpha=0.5)

for spine in plt.gca().spines.values():
    spine.set_visible(True)
    spine.set_linewidth(0.5)
    spine.set_color("black")

for spine in plt.gca().spines.values():
    spine.set_visible(True)
    spine.set_linewidth(0.5)
    spine.set_color("black")

# Save
plt.tight_layout(rect=[0.01, -0.0, 1.02, 1.0], w_pad=-20)
plt.savefig(OUTDIR + f"figs/fig_mca_concentration.pdf", dpi=300, transparent=True)
