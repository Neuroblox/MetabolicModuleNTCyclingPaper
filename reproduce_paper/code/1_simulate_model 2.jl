"""

@author: Botond B. Antal

June 2026

This script runs the simulations and stores the results.

"""

using Catalyst
using OrdinaryDiffEq
using Printf
using DataFrames
using CSV
using Random
using HDF5
using CairoMakie

# Filepaths
OUTDIR =  "" * "results/"; #TODO: insert your filepath here before results/

##
# Model
# -------------------------

# Burn-in time for simulations to ensure steady-state
burnin = 10000;

# Custom rate functions
mm_reversible(S1P, S1B, Vmax, Km) = Vmax * (S1P - S1B) / (Km + S1P + S1B);
CMRglc(V_ATP, KET_b, k_ket, ATPglc, ATPket) = ((V_ATP - ATPket*KET_b*k_ket)/ATPglc)/0.91
Vpmas_e(cmrglc) = (cmrglc*0.91*0.75*0.83 - 0.077)/0.812;
Vpmas_i(cmrglc) = (cmrglc*0.91*0.75*0.17 - 0.011)/0.763;

# Ketone input time-series
# KET_p(t) = 10.4*(exp(-(t-burnin)/89.2) - exp(-(t-burnin)/27.2))*1/(1+exp(-1e5* (t-burnin)))  # For timecourse simulation
KET_p(t) = 0.0  # For MCA only

# Create model
model = @reaction_network begin
    
    # Ketone metabolism
    mm_reversible(KET_p(t), KET_b, Tmax_ket, KT_ket), 0 => KET_b, [description="Ketone transport"]
    k_ket*KET_b, KET_b => 0, [description="Ketone utilization"]

    # Glutamatergic neuron
    Vpmas_e(CMRglc(V_ATP, KET_b, k_ket, ATPglc, ATPket))*c_vpmas, GLN_e => GLU_e, [description="PMAS in e"]
    k_syn_e * GLU_e, GLU_e => GLU_a, [description="GLU synaptic flux"]

    # GABAergic neuron
    Vpmas_i(CMRglc(V_ATP, KET_b, k_ket, ATPglc, ATPket))*c_vpmas, GLN_i => GLU_i, [description="PMAS in i"]
    mm(GLU_i, Vmax_GAD67, KM_GAD67), GLU_i => GABA_i, [description="GAD67"]
    mm(GLU_i, Vmax_GAD65, KM_GAD65), GLU_i => GABA_v, [description="GAD65"]
    mm(GABA_i, Vmax_GT, KM_GT), GABA_i => GLU_i, [description="GT"]
    k_syn_i * GABA_v, GABA_v => GLU_a, [description="GABA synaptic flux"]

    # Astrocyte
    V_anapl, 0 => GLU_a, [description="Anaplerosis"]
    Vmax_GDH * (GLU_a/KM_GDH)^h_GDH / (1 + (GLU_a/KM_GDH)^h_GDH), GLU_a => 0, [description="GDH"]
    Vmax_GS * GLU_a / (KM_GS*(1 + GLN_a/KI_GS) + GLU_a), GLU_a => GLN_a, [description="GS"]
    Vpmas_e(CMRglc(V_ATP, KET_b, k_ket, ATPglc, ATPket))*c_vpmas, GLN_a => GLN_e, [description="GLN uptake in e"]
    Vpmas_i(CMRglc(V_ATP, KET_b, k_ket, ATPglc, ATPket))*c_vpmas, GLN_a => GLN_i, [description="GLN uptake in i"]
    V_out0 + mm_reversible(GLN_a*GLN_ratio, GLN_p, Tmax_gln, KT_gln), GLN_a => 0, [description="GLN efflux"]

    # Monitoring only (dummy reactions)
    CMRglc(V_ATP, KET_b, k_ket, ATPglc, ATPket), KET_b => KET_b, [description="CMRglc"]
    CMRglc(V_ATP, KET_b, k_ket, ATPglc, ATPket)*0.91*0.75, KET_b => KET_b, [description="CMRglc(ox)N"]
    Vpmas_e(CMRglc(V_ATP, KET_b, k_ket, ATPglc, ATPket))*c_vpmas + 
    Vpmas_i(CMRglc(V_ATP, KET_b, k_ket, ATPglc, ATPket))*c_vpmas,
        KET_b => KET_b, [description="VPMAS"]

end;

# Initial conditions
u0 = [
    :GLN_e => 0.28,  # mM
    :GLN_i => 0.07,  # mM
    :GLU_e => 10.0,  # mM
    :GLU_i => 0.13,  # mM
    :GABA_i => 0.73,  # mM
    :GABA_v => 0.1,  # mM
    :GLN_a => 3.8,  # mM
    :GLU_a => 0.8,  # mM
    :KET_b => 0.0,  # mM
    ];  # [X] = mM

# Parameters
ps = Dict([

    # Neurotranstmitter cycling
    :k_syn_e => 0.0191,
    :k_syn_i => 0.4793, 
    :Vmax_GAD67 => 0.0959,
    :KM_GAD67 => 0.13,
    :Vmax_GT => 0.0582,
    :KM_GT => 0.1563,
    :Vmax_GAD65 => 0.0516,
    :KM_GAD65 => 0.01,
    :Vmax_GDH => 0.096,
    :KM_GDH => 0.8,
    :h_GDH => 4.0,
    :Vmax_GS => 0.753,
    :KM_GS => 0.8,
    :KI_GS => 3.8,
    :V_anapl => 0.06,
    :GLN_p => 0.5,
    :GLN_ratio => 1/8,
    :V_out0 => 0.012,
    :Tmax_gln => 0.018,
    :KT_gln => 0.25,

    # Energy metabolism
    :V_ATP => 11.94,  # mM/min
    :ATPglc => 32.0,

    # Ketone metabolism
    :Tmax_ket => 0.462,  # mM/min
    :KT_ket => 27.5,  # mM
    :k_ket => 0.162,  # 1/min
    :ATPket => 21.5,

    # MCA only    
    :c_vpmas => 1.0,  # For MCA purposes only, must be set to 1.

    ]);# [V] = mM/min, [KM] = mM, [X] = mM

# Time span
tmax = burnin + 500;
tspan = (0., tmax);

# ODE problem
prob = ODEProblem(model, u0, tspan, ps);

# Simulate
sol_raw = solve(prob, Vern7());
sol = sol_raw[findall(sol_raw.t .>= burnin)];  # Cut off burn-in time

##
# Single run of the model for testing
# ------------------------------------

# Make dataframe
df = DataFrame(sol);
rename!(df, [replace(item, "(t)" => "") for item in names(df)]);
df[!, :timestamp] = sol.t .- burnin;

# Plot
inch=96; pt=4/3;
fig = Figure(size=(4.825inch, 3inch), fontsize=12pt)
ax = Axis(fig[1, 1]);
[lines!(ax, df[:, "timestamp"], df[:, label], label=label, linewidth=2)
    for label in names(df)[2:end]]; 

CairoMakie.ylims!(0, 11.)
ax.xlabel = "Time";
ax.ylabel = "Concentration";
vlines!([60], color=:black, linestyle=:dash, linewidth=1);
Legend(fig[1, 2], ax, labelsize=8pt);
display(fig)

# Print concentration changes
println("\nConcentrations:");
for i in range(1, stop=length(unknowns(model)))
    println(@sprintf("%s: %.4g -> %.4g", unknowns(model)[i], sol.u[1][i], sol.u[end][i]))
end;

# Print reaction rates in steady state
println("\nReaction rates:");
for i in range(1, stop=length(reactions(model)))
    func_sym = reactionrates(model)[i];
    func = eval(build_function(func_sym, [p[1] for p in ps]..., :t, unknowns(model)...));
    rate = func([p[2] for p in ps]..., tmax, [sol[state][end] for state in unknowns(model)]...);
    println(@sprintf("r=%.3g; ", rate) * Catalyst.getdescription(reactions(model)[i]))
end;

# Compute fluxes for intermediate timepoints
items = [];
for i in range(1, stop=length(reactions(model)))
    func_sym = reactionrates(model)[i];
    func = eval(build_function(func_sym, [p[1] for p in ps]..., :t, unknowns(model)...));
    reaction_name = Catalyst.getdescription(reactions(model)[i]);
    rates = [func([p[2] for p in ps]..., tmax, [sol[state][j] for state in unknowns(model)]...) for j in 1:size(sol, 2)];
    push!(items, (Symbol(reaction_name) => rates))
end;

# Convert fluxes to dataframe
df_flux = DataFrame(items);
df_flux[!, :timestamp] = df.timestamp;

# Save as CSV
CSV.write(OUTDIR * "model_timeseries.csv", df);
CSV.write(OUTDIR * "model_fluxes.csv", df_flux);

##
# Full run with 1000 replicates
# ------------------------------------

# Set random seed for reproducibility
Random.seed!(1234);

# Time span
tmax = burnin + 500;
tspan = (0., tmax);  # [time] = min
save_t = range(0., stop=tmax, length=tmax+1);

# Reference data
ref_start_glu = 10.93;
ref_start_gaba = 0.83;
ref_stdev_glu = 0.65 * ref_start_glu/6.89;
ref_stdev_gaba = 0.27 * ref_start_gaba/0.96;

# Randomization settings
n_runs = 1000;  # Number of replicates
frac = 0.10;  # Fraction of variation for parameters (+/- %)

# Open HDF5 file for writing
h5file = h5open(OUTDIR * "model_multirun.h5", "w");

# Try
try

    # Counter for successful runs
    cnt_total = 0;
    cnt_success = 0;
    
    # Create groups for pars, concs and fluxes
    grp_info = create_group(h5file, "info")
    grp_conc = create_group(h5file, "concentrations")
    grp_flux = create_group(h5file, "fluxes")
    grp_u0 = create_group(h5file, "u0")
    grp_pars = create_group(h5file, "parameters")

    # Iterate through runs
    while cnt_success < n_runs

        # Record attempt
        cnt_total += 1;

        # Print status
        print("\nRunning simulation #$cnt_total. Progress: ($(cnt_success)/$n_runs)")

        # Run simulation
        # ----------

        # Create new parameter set with random variations
        ps_new = Dict(
                k => v * (1 + frac * (2 * rand() - 1)) for (k, v) in ps);

        # Create a new set of initial concentrations
        u0_new = Dict(
            k => v * (1 + frac * (2 * rand() - 1)) for (k, v) in u0);

        # Fix parameters related to activation state (out-of-scope for model)
        ps_new[:c_vpmas] = ps[:c_vpmas]

        # Remake problem
        prob = remake(prob; u0=u0_new, p=ps_new, tspan=tspan);

        # Simulate
        sol_raw = solve(prob, Vern7(), saveat=save_t);

        # Check simulation results
        # ------------------

        # Check for steady state
        mask = abs.(sol_raw(burnin-10, Val{1})) .> 1e-4;
        if sum(mask) > 0
            print(" // Not in steady-state: ($(sum(mask))) ",
                join(unknowns(model)[mask], ", "));
            continue
        end
        
        # Get starting state once steady-state is reached
        start_state = sol_raw(burnin);
        start_glu = start_state[3] + start_state[4] + start_state[6]
        start_gaba = start_state[7] + start_state[8]

        # Check if starting state is within reference range
        mask = [
            abs(start_glu - ref_start_glu) > ref_stdev_glu,
            abs(start_gaba - ref_start_gaba) > ref_stdev_gaba
            ]
        if sum(mask) > 0
            print(" // Starting state outside reference range: ",
                join(["GLU", "GABA"][mask], ", "));
            continue
        end

        # Cut off burn-in time
        sol = sol_raw[findall(save_t .>= burnin)];

        # Extract and refine varnames
        var_names = replace.(string.(unknowns(model)), "(t)" => "")

        # Parameters
        # ---------------
        grp = create_group(grp_pars, "run_$(cnt_success+1)")
        grp["par_names"] = [string(k) for k in keys(ps_new)]
        grp["pars"] = [v for v in values(ps_new)]

        # Concentrations
        # --------------

        # Save
        grp = create_group(grp_conc, "run_$(cnt_success+1)")
        grp["var_names"] = var_names
        grp["t"] = sol.t .- burnin
        grp["concs"] = Array(sol)

        # u0
        # ----------

        # Save
        grp = create_group(grp_u0, "run_$(cnt_success+1)")
        grp["var_names"] = var_names
        grp["u0_names"] = [string(k) for k in keys(u0_new)]
        grp["u0"] = [v for v in values(u0_new)]

        # Fluxes
        # -------------

        # Initialize collection for columns of rates
        items = [];

        # Iterate through reactions and extract the reaction description and rates
        for i in range(1, stop=length(reactions(model)))
            func_sym = reactionrates(model)[i];
            func = eval(build_function(func_sym, [p[1] for p in ps]..., :t, unknowns(model)...));
            reaction_name = Catalyst.getdescription(reactions(model)[i]);
            rates = [func([p[2] for p in ps]..., tmax, [sol[state][j] for state in unknowns(model)]...) for j in 1:size(sol, 2)];
            push!(items, (Symbol(reaction_name) => rates))
        end;

        # Save
        grp = create_group(grp_flux, "run_$(cnt_success+1)")
        grp["reaction_names"] = [string(item[1]) for item in items]
        grp["t"] = sol.t .- burnin
        grp["rates"] = hcat([item[2] for item in items]...)  # Convert to matrix

        # Mark run as successful
        print(" // Successful run.")
        cnt_success += 1;

    end

    # Count successful runs
    println("\nSuccessful runs:  $cnt_success out of $cnt_total.")

finally

    # Close h5 files
    close(h5file)

end

##
# MCA - concentration control
# -------------------------

"""
Rerun the model definition with "KET_p(t) = 0.0" before running this section!
"""

# Setup
C_rows = []  # Collection for control coefficients
ϵ = 0.01  # Extent of perturbation
tspan = (0., burnin);  # Longer time span to reach steady state

# Iterate through the parameters
for par in keys(ps)

    # Reset the parameter set
    ps_test = copy(ps)

    # Center
    ps_test[par] = ps[par];
    prob = remake(prob; u0=u0, p=ps_test, tspan=tspan);
    sol = solve(prob, Vern7());
    S0 = [sol[state][end] for state in unknowns(model)]

    # Increment 1
    ps_test[par] = ps[par] * (1 - ϵ);
    prob = remake(prob; u0=u0, p=ps_test, tspan=tspan);
    sol = solve(prob, Vern7());
    S1 = [sol[state][end] for state in unknowns(model)]

    # Increment 2
    ps_test[par] = ps[par] * (1 + ϵ);
    prob = remake(prob; u0=u0, p=ps_test, tspan=tspan);
    sol = solve(prob, Vern7());
    S2 = [sol[state][end] for state in unknowns(model)]

    # Compute the control coefficient based on central differences
    C = (S2 .- S1) ./ (S0 .* 2ϵ)
    push!(C_rows, C)

end

# Compile results into dataframe
df = DataFrame(C_rows, :auto)
rename!(df, String.(keys(ps)))

# Add state names
df[!, :state] = string.(unknowns(model));

# Save as CSV
CSV.write(OUTDIR * "model_mca_concentration.csv", df);

# Create heatmap
mat = Matrix(df[!, 1:end-1])'
fig = Figure(size=(5.5inch, 4.5inch), fontsize=12pt) #, backgroundcolor=:transparent);
ax = Axis(fig[1, 1],
    aspect=DataAspect(),
    title="Concentration control coefficients",
    xticks = (1:size(df, 2)-1, names(df)[1:end-1]), 
    yticks = (1:size(df, 1), df[!, :state]),
    xticklabelrotation = pi / 2.,
    xgridvisible = false,
    ygridvisible = false)
hm = heatmap!(ax, mat, colormap=:seismic, colorrange =(-30, +30),)
Colorbar(fig[1, 2], hm)

# Add text labels to the heatmap
for i in 1:size(mat, 1), j in 1:size(mat, 2)
    text!(ax, i, j, text=@sprintf("%.1f", mat[i, j]),
    align=(:center, :center), color=:black, fontsize=8pt)
end

# Add grid lines manually
for x in 1:size(mat, 1)
    lines!(ax, [x-0.5, x-0.5], [0, size(mat, 2)+0.5], color=:black, linewidth=0.5)
end
for y in 1:size(mat, 2)
    lines!(ax, [0, size(mat, 1)+0.5], [y-0.5, y-0.5], color=:black, linewidth=0.5)
end

display(fig)
