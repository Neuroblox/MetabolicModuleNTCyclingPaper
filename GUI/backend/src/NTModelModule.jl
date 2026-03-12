module NTModelModule

using Catalyst
using OrdinaryDiffEqTsit5

export NTModel, simulate, get_defaults, extract_results
export unknowns

mutable struct NTModel
    """
    Struct with Neurotransmitter Model
    """
    model::ReactionSystem
    u0::Dict{Symbol, Float64}
    ps::Dict{Symbol, Float64}
    prob::Union{ODEProblem, Nothing}
    u0_units::Dict{Symbol, String}
    ps_units::Dict{Symbol, String}
    u0_desc::Dict{Symbol, String}
    ps_desc::Dict{Symbol, String}

    function NTModel()

        # Initial conditions
        u0 = Dict([
            :GLN_e => 0.28,  # mM
            :GLN_i => 0.07,  # mM
            :GLU_e => 10.0,  # mM
            :GLU_i => 0.06,  # mM
            :GABA_i => 0.6,  # mM
            :GABA_v => 0.06,  # mM
            :GLN_a => 3.8,  # mM
            :GLU_a => 0.8,  # mM
            :KET_b => 0.0,  # mM
        ])

        # Units for initial conditions
        u0_units = Dict([
            :GLN_e => "mM",
            :GLN_i => "mM",
            :GLU_e => "mM",
            :GLU_i => "mM",
            :GABA_i => "mM",
            :GABA_v => "mM",
            :GLN_a => "mM",
            :GLU_a => "mM",
            :KET_b => "mM",
        ])

        u0_desc = Dict([
            :GLN_e => "Glutamine in excitatory neurons",
            :GLN_i => "Glutamine in inhibitory neurons",
            :GLU_e => "Glutamate in excitatory neurons",
            :GLU_i => "Glutamate in inhibitory neurons",
            :GABA_i => "GABA (cytosolic) in inhibitory neurons",
            :GABA_v => "GABA in vesicles",
            :GLN_a => "Glutamine in astrocytes",
            :GLU_a => "Glutamate in astrocytes",
            :KET_b => "Brain ketone concentration",
        ])

        # Parameters
        ps = Dict([
            # Neurotransmitter cycling
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
            :KET_p => 0,
        ])

        # Units for parameters
        ps_units = Dict([
            # Neurotransmitter cycling
            :c_vpmas => "-",
            :k_syn_e => "1/min",
            :k_syn_i => "1/min",
            :Vmax_GAD67 => "mM/min",
            :KM_GAD67 => "mM",
            :Vmax_GT => "mM/min",
            :KM_GT => "mM",
            :Vmax_GAD65 => "mM/min",
            :KM_GAD65 => "mM",
            :Vmax_GS => "mM/min",
            :KM_GS => "mM",
            :KI_GS => "mM",
            :h_GS => "-",
            :Vmax_GDH => "mM/min",
            :KM_GDH => "mM",
            :h_GDH => "-",
            :k_ox => "-",
            :V_out => "mM/min",

            # Energy metabolism
            :V_ATP => "mM/min",
            :ATPglc => "-",

            # Ketone metabolism
            :Tmax_ket => "mM/min",
            :KT_ket => "mM",
            :k_ket => "1/min",
            :ATPket => "-",
            :KET_p => "mM",
        ])

        ps_desc = Dict([
            # Neurotransmitter cycling
            :c_vpmas => "relative rate of PMAS",
            :k_syn_e => "rate constant for glutamate vesicle loading",
            :k_syn_i => "rate constant for GABA vesicle loading",
            :Vmax_GAD67 => "GAD67 maximum rate",
            :KM_GAD67 => "GAD67 Michaelis-Menten constant for glutamate",
            :Vmax_GT => "GT maximum rate",
            :KM_GT => "GT Michaelis-Menten constant for GABA",
            :Vmax_GAD65 => "GAD65 maximum rate",
            :KM_GAD65 => "GAD65 Michaelis-Menten constant for glutamate",
            :Vmax_GS => "GS maximum rate",
            :KM_GS => "GS Michaelis-Menten constant for glutamate",
            :KI_GS => "GS inhibition constant for glutamine",
            :h_GS => "GS Hill exponent for the inhibition by GLN",
            :Vmax_GDH => "GDH maximum rate",
            :KM_GDH => "GDH Michaelis-Menten constant for glutamate",
            :h_GDH => "GDH Hill exponent",
            :k_ox => "relative portion of glutamate oxidation",
            :V_out => "rate of GLN efflux",

            # Energy metabolism
            :V_ATP => "rate of ATP synthesis",
            :ATPglc => "ATP yield from GLC",

            # Ketone metabolism
            :Tmax_ket => "Ketone transport maximum rate",
            :KT_ket => "Ketone transport Michaelis-Menten constant",
            :k_ket => "Ketone utilization rate constant",
            :ATPket => "ATP yield from ketones",
            :KET_p => "Plasma Ketone concentration",
        ])

        # Model definition
        # Custom rate functions
        mm_reversible(S1P, S1B, Vmax, Km1) =
            Vmax / Km1 * (S1P - S1B) / (1 + S1P/Km1 + S1B/Km1)
        CMRglc(V_ATP, KET_b, k_ket, ATPglc, ATPket) = ((V_ATP - ATPket*KET_b*k_ket)/ATPglc)/0.91
        Vpmas_e(cmrglc, c_vpmas) = c_vpmas*(cmrglc*0.91*0.75*0.83 - 0.077)/0.812
        Vpmas_i(cmrglc, c_vpmas) = c_vpmas*(cmrglc*0.91*0.75*0.17 - 0.011)/0.763

        # Reaction network
        model = @reaction_network begin

            # Ketone transport
            mm_reversible(KET_p, KET_b, Tmax_ket, KT_ket), 0 => KET_b, [description="Ketone transport"]

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

        end

        return new(model, u0, ps, nothing, u0_units, ps_units, u0_desc, ps_desc)

    end

end

"""
    get_defaults(model::NTModel)

Returns default parameters and states as JSON-compatible Dict.
"""
function get_defaults(model::NTModel)
    return Dict(
        "parameters" => Dict(string(k) => v for (k, v) in model.ps),
        "states" => Dict(string(k) => v for (k, v) in model.u0),
        "parameterUnits" => Dict(string(k) => v for (k, v) in model.ps_units),
        "stateUnits" => Dict(string(k) => v for (k, v) in model.u0_units),
        "parameterDescriptions" => Dict(string(k) => v for (k, v) in model.ps_desc),
        "stateDescriptions" => Dict(string(k) => v for (k, v) in model.u0_desc)
    )
end

"""
    simulate(model::NTModel; tspan=(0., 600.))

Simulates the model over the given time span (in minutes).
Returns the ODE solution.
"""
function simulate(model::NTModel; tspan=(0., 600.))
    # ODE problem
    model.prob = ODEProblem(model.model, model.u0, tspan, model.ps)

    # Simulate
    sol = solve(model.prob, Tsit5())

    return sol
end

"""
    extract_results(sol, selected_states::Vector{String}, percentage_change::Bool)

Extracts time series for selected states from a solution.
If percentage_change is true, returns percentage change from initial value.
"""
function extract_results(sol, selected_states::Vector{String}, percentage_change::Bool)
    time_points = collect(sol.t)
    states = Dict{String, Vector{Float64}}()

    for state_name in selected_states
        state_sym = Symbol(state_name)
        values = collect(sol[state_sym])
        if percentage_change && values[1] != 0
            values = 100.0 .* (values ./ values[1] .- 1.0)
        end
        states[state_name] = round.(values, digits=4)
    end

    return Dict(
        "time" => round.(time_points, digits=4),
        "states" => states
    )
end

#"""
#    get_timeseries(sol; selected_states=["GLN_e(t)"], percentage_change=false)
#
#Returns time series as DataFrame for selected states.
#"""
#function get_timeseries(sol; selected_states=["GLN_e(t)"], percentage_change=false)
#    timeseries = []
#    for state in selected_states
#        state_symbol = Symbol(replace(state, "(t)" => ""))
#        if percentage_change
#            push!(timeseries, round.(100 .* sol[state_symbol]./(sol[state_symbol][1]) .- 100, digits=1))
#        else
#            push!(timeseries, sol[state_symbol])
#        end
#    end
#
#    df = DataFrame([sol.t, timeseries...], Symbol.(["time", selected_states...]))
#    return df
#end

end
