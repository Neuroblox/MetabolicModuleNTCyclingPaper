# Precompile workload for PackageCompiler.
# This script exercises key code paths so the compiled sysimage covers them,
# resulting in faster startup and response times.

using Catalyst
using HTTP
using Oxygen
using OrdinaryDiffEqTsit5
using JSON3
using XLSX

include(joinpath(@__DIR__, "src", "NTModelModule.jl"))
using .NTModelModule

# Exercise model construction and simulation
model = NTModel()
sol = simulate(model; tspan=(0.0, 600.0))

# Exercise result extraction (both absolute and percentage modes)
results = extract_results(sol, ["GLU_e", "GABA_i", "GLN_a", "GLN_e", "GLU_i", "GABA_v", "GLN_i", "GLU_a", "KET_b"], false)
results_pct = extract_results(sol, ["GLU_e", "GABA_i"], true)

# Exercise defaults serialisation
defaults = get_defaults(model)

# Exercise JSON round-trip
json_str = JSON3.write(results)
JSON3.read(json_str)
json_str2 = JSON3.write(defaults)
JSON3.read(json_str2)

# Exercise a second simulation with modified parameters (mirrors /api/simulate usage)
model2 = NTModel()
model2.ps[:KET_p] = 3.9
sol2 = simulate(model2; tspan=(0.0, 90.0))
extract_results(sol2, ["GLU_e", "GABA_i"], true)

# Exercise Oxygen route registration — this is the critical step that ensures
# Oxygen's router, @get/@post macro expansions, and handler dispatch are all
# compiled into the sysimage.  (serve() itself cannot be called here because
# it blocks, but registering routes + invoking handlers covers all hot paths.)
using NTCycling
NTCycling.register_routes!()

# Exercise handler functions directly to precompile the full request/response
# dispatch path for each endpoint.
NTCycling._handle_defaults(HTTP.Request("GET", "/api/defaults"))

simulate_body = """{"simLength":60,"selectedStates":["GLU_e","GABA_i"],"percentageChange":false}"""
NTCycling._handle_simulate(
    HTTP.Request("POST", "/api/simulate",
        ["Content-Type" => "application/json"],
        simulate_body)
)

println("Precompile workload complete")
