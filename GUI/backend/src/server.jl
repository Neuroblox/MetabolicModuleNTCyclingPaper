using Oxygen
using HTTP
using JSON3
using XLSX

# Include the model
include("NTModelModule.jl")
using .NTModelModule

# Serve static files from public directory
const PUBLIC_DIR = get(ENV, "NT_PUBLIC_DIR", joinpath(@__DIR__, "..", "public"))

# Include API files at module load time so handler functions are compiled into the sysimage.
# Route *registration* (@get/@post calls) happens inside register_routes!() at runtime,
# because Oxygen's HTTP router state does not survive sysimage serialisation.
include("api/defaults.jl")
include("api/simulation.jl")
include("api/examples.jl")
include("api/export.jl")

function register_routes!()

    # Main page
    @get "/" function(req::HTTP.Request)
        html_content = read(joinpath(PUBLIC_DIR, "index.html"), String)
        return HTTP.Response(200, ["Content-Type" => "text/html"], html_content)
    end

    # Documentation page
    @get "/documentation" function(req::HTTP.Request)
        filepath = joinpath(PUBLIC_DIR, "docs.html")
        if isfile(filepath)
            html_content = read(filepath, String)
            return HTTP.Response(200, ["Content-Type" => "text/html"], html_content)
        else
            return HTTP.Response(404, "Documentation page not found")
        end
    end

    # Serve static files (CSS, images, etc.)
    @get "/css/{filename}" function(req::HTTP.Request, filename::String)
        filepath = joinpath(PUBLIC_DIR, "css", filename)
        if isfile(filepath)
            content = read(filepath, String)
            return HTTP.Response(200, ["Content-Type" => "text/css"], content)
        else
            return HTTP.Response(404, "File not found")
        end
    end

    @get "/images/{filename}" function(req::HTTP.Request, filename::String)
        filepath = joinpath(PUBLIC_DIR, "images", filename)
        if isfile(filepath)
            content = read(filepath)
            content_type = endswith(filename, ".png") ? "image/png" : "image/jpeg"
            return HTTP.Response(200, ["Content-Type" => content_type], content)
        else
            return HTTP.Response(404, "File not found")
        end
    end

    # API routes
    register_defaults_routes!()
    register_simulation_routes!()
    register_examples_routes!()
    register_export_routes!()
end

# Start server
function start_server(; host="127.0.0.1", port::Int=8090)
    register_routes!()
    println("Starting NT Cycling Model server on http://localhost:$port")
    println("Press Ctrl+C to stop the server")
    serve(; host=host, port=port)
end

# Run if executed directly
if abspath(PROGRAM_FILE) == @__FILE__
    start_server()
end
