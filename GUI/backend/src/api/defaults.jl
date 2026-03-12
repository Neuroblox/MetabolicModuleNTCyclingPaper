# GET /api/defaults - Returns default parameters, states, units, descriptions

function _handle_defaults(req::HTTP.Request)
    model = NTModel()
    defaults = get_defaults(model)
    return JSON3.write(defaults)
end

function register_defaults_routes!()
    @get "/api/defaults" _handle_defaults
end
