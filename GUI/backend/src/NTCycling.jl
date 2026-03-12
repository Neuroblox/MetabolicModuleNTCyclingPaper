module NTCycling

include("server.jl")

Base.@ccallable function julia_main()::Cint
    try
        port = parse(Int, get(ENV, "NT_PORT", "8090"))
        host = get(ENV, "NT_HOST", "127.0.0.1")
        start_server(; host=host, port=port)
    catch e
        println(stderr, "Error starting server: ", e)
        return 1
    end
    return 0
end

end
