# GET /api/examples - List available examples
# GET /api/example/:id - Get specific example configuration

const EXAMPLES = Dict(
    "ketosis" => Dict(
        "name" => "Ketosis",
        "description" => "Simulates ketogenic diet conditions with elevated plasma ketones",
        "condition1" => Dict(
            "parameters" => Dict{String,Any}(),  # Default values
            "states" => Dict{String,Any}()
        ),
        "condition2" => Dict(
            "parameters" => Dict(
                "KET_p" => 3.9   # Elevated plasma ketones (mM)
            ),
            "states" => Dict{String,Any}()
        ),
        "selectedStates" => ["GLU_e", "GABA_i"],
        "simLength" => 90,
        "percentageChange" => true,
        "conditionNames" => Dict(
            "condition1" => "Control",
            "condition2" => "Ketosis"
        ),
        "referenceDataPercent" => [
            Dict("state" => "GLU_e", "mean" => -10.6, "error" => 1.2, "time" => 60),
            Dict("state" => "GABA_i", "mean" => -36.9, "error" => 4.2, "time" => 60)
        ]
    ),
    "gabat" => Dict(
        "name" => "GABA-T Inhibitor",
        "description" => "Simulates GABA transaminase inhibition (e.g., vigabatrin)",
        "condition1" => Dict(
            "parameters" => Dict{String,Any}(),
            "states" => Dict{String,Any}()
        ),
        "condition2" => Dict(
            "parameters" => Dict(
                "Vmax_GT" => 0.05567  # Reduced GABA transaminase activity
            ),
            "states" => Dict{String,Any}()
        ),
        "selectedStates" => ["GLU_e", "GABA_i"],
        "simLength" => 7200,
        "percentageChange" => true,
        "conditionNames" => Dict(
            "condition1" => "Control",
            "condition2" => "GABA-T Inhibitor"
        )
    )
)

@get "/api/examples" function(req::HTTP.Request)
    examples_list = [
        Dict(
            "id" => id,
            "name" => ex["name"],
            "description" => ex["description"]
        )
        for (id, ex) in EXAMPLES
    ]
    return JSON3.write(examples_list)
end

@get "/api/example/{id}" function(req::HTTP.Request, id::String)
    if haskey(EXAMPLES, id)
        return JSON3.write(EXAMPLES[id])
    else
        return HTTP.Response(404, JSON3.write(Dict("error" => "Example not found")))
    end
end
