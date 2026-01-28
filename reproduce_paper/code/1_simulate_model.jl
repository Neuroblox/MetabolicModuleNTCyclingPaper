"""

@author: Botond B. Antal

January 2026

This script runs the simulations and saves the results.

"""

using Catalyst
using OrdinaryDiffEq
using Printf
using DataFrames
using CSV
using CairoMakie

OUTDIR =  "" * "results/"; #TODO: insert your filepath here before results/

##
# Model
# -------------------------

# Custom rate functions
mm_reversible(S1P, S1B, Vmax, Km1) = 
    Vmax / Km1 * (S1P - S1B) / (1 + S1P/Km1 + S1B/Km1);
CMRglc(V_ATP, KET_b, k_ket, ATPglc, ATPket) = ((V_ATP - ATPket*KET_b*k_ket)/ATPglc)/0.91
Vpmas_e(cmrglc, c_vpmas) = c_vpmas*(cmrglc*0.91*0.75*0.83 - 0.077)/0.812;
Vpmas_i(cmrglc, c_vpmas) = c_vpmas*(cmrglc*0.91*0.75*0.17 - 0.011)/0.763;

# Ketone input time-series
KET_p(t) = 10.4*(exp(-(t)/89.2) - exp(-t/27.2))  # For comparison with test dataset
# KET_p(t) = 0.0  # For MCA

# Create model
model = @reaction_network begin
    
    # Ketone transport
    mm_reversible(KET_p(t), KET_b, Tmax_ket, KT_ket), 0 => KET_b, [description="Ketone transport"]

    # Ketone utilization
    k_ket*KET_b, KET_b => 0, [description="Ketone utilization"]

    # Glutamatergic neuron
    Vpmas_e(CMRglc(V_ATP, KET_b, k_ket, ATPglc, ATPket), c_vpmas), GLN_e => GLU_e, [description="PMAS in e"]
    k_syn_e * GLU_e, GLU_e => GLU_a, [description="GLU cycling"]

    # GABAergic neuron
    Vpmas_i(CMRglc(V_ATP, KET_b, k_ket, ATPglc, ATPket), c_vpmas), GLN_i => GLU_i, [description="PMAS in i"]
    mm(GLU_i, Vmax_GAD67, KM_GAD67), GLU_i => GABA_i, [description="GAD67"]
    mm(GLU_i, Vmax_GAD65, KM_GAD65), GLU_i => GABA_v, [description="GAD65"]
    mm(GABA_i, Vmax_GT, KM_GT), GABA_i => GLU_i, [description="GT"]
    k_syn_i * GABA_v, GABA_v => GLU_a, [description="GABA cycling"]

    # Astrocyte
    k_ox * k_syn_e * GLU_e + V_out, 0 => GLU_a, [description="Anaplerosis"]
    Vmax_GDH * (GLU_a/KM_GDH)^h_GDH / (1 + (GLU_a/KM_GDH)^h_GDH), GLU_a => 0, [description="GDH"]
    Vmax_GS * GLU_a / (KM_GS*(1 + (GLN_a/KI_GS)^h_GS) + GLU_a), GLU_a => GLN_a, [description="GS"]
    Vpmas_e(CMRglc(V_ATP, KET_b, k_ket, ATPglc, ATPket), c_vpmas), GLN_a => GLN_e, [description="GLN uptake in e"]
    Vpmas_i(CMRglc(V_ATP, KET_b, k_ket, ATPglc, ATPket), c_vpmas), GLN_a => GLN_i, [description="GLN uptake in i"]
    V_out, GLN_a => 0, [description="GLN efflux"]

    # Monitoring
    CMRglc(V_ATP, KET_b, k_ket, ATPglc, ATPket), KET_b => KET_b, [description="CMRglc"]
    CMRglc(V_ATP, KET_b, k_ket, ATPglc, ATPket)*0.91*0.75, KET_b => KET_b, [description="CMRglc(ox)N"]
    Vpmas_e(CMRglc(V_ATP, KET_b, k_ket, ATPglc, ATPket), c_vpmas) + 
    Vpmas_i(CMRglc(V_ATP, KET_b, k_ket, ATPglc, ATPket), c_vpmas),
        KET_b => KET_b, [description="VPMAS"]

end;

# Initial conditions
u0 = [
    :GLN_e => 0.28,  # mM
    :GLN_i => 0.07,  # mM
    :GLU_e => 10.0,  # mM
    :GLU_i => 0.06,  # mM
    :GABA_i => 0.6,  # mM
    :GABA_v => 0.06,  # mM
    :GLN_a => 3.8,  # mM
    :GLU_a => 0.8,  # mM
    :KET_b => 0.0,  # mM
    ];  # [X] = mM

# Parameters
ps = Dict([

    # Neurotranstmitter cycling
    :c_vpmas => 1.0,
    :k_syn_e => 0.01912,
    :k_syn_i => 0.79882, 
    :Vmax_GAD67 => 0.20769,
    :KM_GAD67 => 0.2,
    :Vmax_GT => 0.05860,
    :KM_GT => 0.13359,
    :Vmax_GAD65 => 0.05591,
    :KM_GAD65 => 0.01,
    :Vmax_GS => 0.753,
    :KM_GS => 0.8,
    :KI_GS => 3.8,
    :h_GS => 4.0,
    :Vmax_GDH => 0.0764,
    :KM_GDH => 0.8,
    :h_GDH => 4.0,
    :k_ox => 0.2,
    :V_out => 0.012,

    # Energy metabolism
    :V_ATP => 11.94,  # mM/min
    :ATPglc => 32.0,

    # Ketone metabolism
    :Tmax_ket => 0.462,  # mM/min
    :KT_ket => 27.5,  # mM
    :k_ket => 0.162,  # 1/min
    :ATPket => 21.5,

    ]);# [V] = mM/min, [KM] = mM, [X] = mM

# Time span
tmax = 1000;
tspan = (0., tmax);

# ODE problem
prob = ODEProblem(model, u0, tspan, ps);

# Simulate
sol = solve(prob, Vern7());

# Analyze simulation results
# ----------

# Make dataframe
df = DataFrame(sol);
rename!(df, [replace(item, "(t)" => "") for item in names(df)]);

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
# MCA - concentration control
# -------------------------

# Setup
C_rows = []  # Collection for control coefficients
ϵ = 0.01  # Extent of perturbation
tspan = (0., 1000.);  # Longer time span to reach steady state

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
hm = heatmap!(ax, mat, colormap=:seismic, colorrange =(-600, +600),)
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
