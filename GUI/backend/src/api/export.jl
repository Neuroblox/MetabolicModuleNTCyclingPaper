# POST /api/export - Generate XLSX file

function _handle_export(req::HTTP.Request)
    body = JSON3.read(String(req.body))

    # Create a temporary file for the XLSX
    filename = tempname() * ".xlsx"

    XLSX.openxlsx(filename, mode="w") do xf
        # Sheet 1: Parameters
        sheet1 = xf[1]
        XLSX.rename!(sheet1, "Parameters")
        sheet1["A1"] = "Parameter"
        sheet1["B1"] = "Condition 1"
        sheet1["C1"] = "Condition 2"
        sheet1["D1"] = "Unit"
        sheet1["E1"] = "Description"

        if haskey(body, :parameters)
            params = body.parameters
            row = 2
            for (name, data) in pairs(params)
                sheet1["A$row"] = string(name)
                sheet1["B$row"] = get(data, :condition1, "")
                sheet1["C$row"] = get(data, :condition2, "")
                sheet1["D$row"] = get(data, :unit, "")
                sheet1["E$row"] = get(data, :description, "")
                row += 1
            end
        end

        # Sheet 2: Condition 1 Data
        XLSX.addsheet!(xf, "Condition 1")
        sheet2 = xf[2]
        if haskey(body, :condition1Data)
            c1 = body.condition1Data
            if haskey(c1, :time)
                sheet2["A1"] = "Time"
                times = collect(c1.time)
                for (i, t) in enumerate(times)
                    sheet2["A$(i+1)"] = t
                end

                col = 2
                if haskey(c1, :states)
                    for (state_name, values) in pairs(c1.states)
                        col_letter = Char('A' + col - 1)
                        sheet2["$(col_letter)1"] = string(state_name)
                        vals = collect(values)
                        for (i, v) in enumerate(vals)
                            sheet2["$(col_letter)$(i+1)"] = v
                        end
                        col += 1
                    end
                end
            end
        end

        # Sheet 3: Condition 2 Data
        XLSX.addsheet!(xf, "Condition 2")
        sheet3 = xf[3]
        if haskey(body, :condition2Data)
            c2 = body.condition2Data
            if haskey(c2, :time)
                sheet3["A1"] = "Time"
                times = collect(c2.time)
                for (i, t) in enumerate(times)
                    sheet3["A$(i+1)"] = t
                end

                col = 2
                if haskey(c2, :states)
                    for (state_name, values) in pairs(c2.states)
                        col_letter = Char('A' + col - 1)
                        sheet3["$(col_letter)1"] = string(state_name)
                        vals = collect(values)
                        for (i, v) in enumerate(vals)
                            sheet3["$(col_letter)$(i+1)"] = v
                        end
                        col += 1
                    end
                end
            end
        end
    end

    # Read the file and return as binary
    xlsx_data = read(filename)
    rm(filename)  # Clean up temp file

    headers = [
        "Content-Type" => "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "Content-Disposition" => "attachment; filename=\"nt_cycling_results.xlsx\""
    ]
    return HTTP.Response(200, headers, xlsx_data)
end

function register_export_routes!()
    @post "/api/export" _handle_export
end
