# Neurotransmitter Cycling Model

A web application for simulating neurotransmitter dynamics in the brain, focusing on glutamate and GABA cycling between neurons and astrocytes.

## Overview

This interactive tool allows researchers to:
- Simulate how metabolic perturbations affect brain neurotransmitter levels
- Compare two conditions side-by-side (e.g., Control vs. Ketosis)
- Visualize time-series dynamics and endpoint concentrations
- Test hypotheses about interventions like ketogenic diet or enzyme inhibitors

The model is based on the pseudo malate-aspartate shuttle (PMAS) framework, which links neurotransmitter synthesis to neuronal glucose metabolism.

## Requirements

- Julia 1.10 or later
- A modern web browser

## Installation

1. Clone or download this repository

2. Install Julia dependencies:
```bash
cd nt_cycling
julia --project=backend -e "using Pkg; Pkg.instantiate()"
```

## Running the Application

Start the server:
```bash
cd nt_cycling
julia --project=backend -e 'include("backend/src/server.jl"); start_server()'
```

Then open your browser to: http://localhost:8090

## Usage

### Main Interface

- **Left Panel**: Modify parameters and initial conditions for each condition
- **Right Panel**: View simulation results as time-series plots or endpoint bar charts

### Quick Start

1. Click **Ketosis** or **GABA-T Inhibitor** to load a preset example
2. Toggle between **Condition 1** and **Condition 2** to modify parameters for each
3. Select which states to plot using the state chips
4. Enable **Percentage Change** to view relative changes from initial values
5. Click **Download Results** to export data as Excel

### Reference Data

Enable **Show Reference Datapoints** to overlay experimental reference values on plots. Reference data is mode-specific (percentage or concentration).

## Model States

| State | Description |
|-------|-------------|
| GLN_e | Glutamine in excitatory neurons |
| GLN_i | Glutamine in inhibitory neurons |
| GLU_e | Glutamate in excitatory neurons |
| GLU_i | Glutamate in inhibitory neurons |
| GABA_i | GABA (cytosolic) in inhibitory neurons |
| GABA_v | GABA in vesicles |
| GLN_a | Glutamine in astrocytes |
| GLU_a | Glutamate in astrocytes |
| KET_b | Brain ketone concentration |

## Project Structure

```
nt_cycling/
├── README.md
├── backend/
│   ├── Project.toml              # Julia dependencies
│   ├── public/
│   │   ├── index.html            # Main simulation page
│   │   ├── docs.html             # Documentation page
│   │   ├── css/app.css
│   │   └── images/
│   └── src/
│       ├── server.jl             # Oxygen.jl web server
│       ├── NTModelModule.jl      # Neurotransmitter model
│       └── api/
│           ├── defaults.jl       # GET /api/defaults
│           ├── simulation.jl     # POST /api/simulate
│           ├── examples.jl       # GET /api/examples
│           └── export.jl         # POST /api/export
```

## Technology Stack

- **Backend**: Julia with Oxygen.jl (web framework), Catalyst.jl (reaction networks)
- **Frontend**: Vue 3, Bootstrap 5, Plotly.js (all via CDN, no build step)

## References

- Rothman et al. (2024). Mechanistic stoichiometric relationship between the rates of neurotransmission and neuronal glucose oxidation. *Journal of Neurochemistry*
- Sibson et al. (1998). Stoichiometric coupling of brain glucose metabolism and glutamatergic neuronal activity. *PNAS*

## License

Part of the Neuroblox project. Visit [neuroblox.ai](https://neuroblox.ai) for more information.
