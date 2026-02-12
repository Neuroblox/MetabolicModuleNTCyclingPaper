# POST /api/simulate - Run simulation for both conditions

@post "/api/simulate" function(req::HTTP.Request)
    body = JSON3.read(String(req.body))

    # Create models for each condition
    model1 = NTModel()
    model2 = NTModel()

    # Apply parameters for condition 1
    if haskey(body, :condition1)
        c1 = body.condition1
        if haskey(c1, :parameters)
            for (key, value) in pairs(c1.parameters)
                model1.ps[Symbol(key)] = Float64(value)
            end
        end
        if haskey(c1, :states)
            for (key, value) in pairs(c1.states)
                model1.u0[Symbol(key)] = Float64(value)
            end
        end
    end

    # Apply parameters for condition 2
    if haskey(body, :condition2)
        c2 = body.condition2
        if haskey(c2, :parameters)
            for (key, value) in pairs(c2.parameters)
                model2.ps[Symbol(key)] = Float64(value)
            end
        end
        if haskey(c2, :states)
            for (key, value) in pairs(c2.states)
                model2.u0[Symbol(key)] = Float64(value)
            end
        end
    end

    # Get simulation settings
    simLength = get(body, :simLength, 600.0)
    simLength = min(Float64(simLength), 10000.0)  # Cap at 10000 minutes

    selectedStates = get(body, :selectedStates, ["GLN_a", "GLU_e", "GABA_i"])
    selectedStates = String.(selectedStates)

    percentageChange = get(body, :percentageChange, false)

    # Run simulations
    sol1 = simulate(model1; tspan=(0.0, simLength))
    sol2 = simulate(model2; tspan=(0.0, simLength))

    # Extract results
    results1 = extract_results(sol1, selectedStates, percentageChange)
    results2 = extract_results(sol2, selectedStates, percentageChange)

    return JSON3.write(Dict(
        "condition1" => results1,
        "condition2" => results2
    ))
end
