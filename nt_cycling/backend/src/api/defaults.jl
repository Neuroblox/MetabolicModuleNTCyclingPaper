# GET /api/defaults - Returns default parameters, states, units, descriptions

@get "/api/defaults" function(req::HTTP.Request)
    model = NTModel()
    defaults = get_defaults(model)
    return JSON3.write(defaults)
end
