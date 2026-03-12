# Neurotransmitter Cycling Model

![](tutorial/figures/fig_model.png)

This repository contains a computational framework for modeling neurotransmitter cycling in the human brain, with a focus on glutamate and GABA dynamics in response to metabolic interventions.

This model is part of the Neuroblox computational neuroscience platform [(https://www.neuroblox.ai/)](https://www.neuroblox.ai/).

## Corresponding publication

[Link to preprint](https://www.biorxiv.org/content/10.64898/2026.02.11.700015): *Computational modeling of neurotransmitter cycling predicts human brain glutamate and GABA dynamics in response to administration of exogenous ketones*

## Repository structure

- `GUI/`  
  Code for a web application that runs the model. A live version can be accessed here: [link to GUI](https://nt-cycling.fly.dev/).

- `reproduce_paper/`  
  Code to reproduce the results reported in the corresponding publication.  

- `tutorial/`  
  A general tutorial demonstrating how to use the neurotransmitter cycling model for custom analyses and exploratory purposes.

## Running the Electron App

The app can be run in dev mode or compiled into a distributable binary.

### Dev mode

```bash
# Install Julia dependencies (first time only)
julia --project=GUI/backend -e 'using Pkg; Pkg.instantiate()'

# Install Node dependencies (first time only)
cd GUI/electron && npm install

# Launch
npm start
```

Electron spawns the Julia server automatically using your system `julia`. The app polls `http://127.0.0.1:8090/` and loads once Julia is ready — first launch takes a moment due to precompilation.

### Production build

Produces a distributable `.dmg` / `.exe` / `AppImage` with a self-contained Julia binary.

```bash
# Install build-env dependencies (first time only)
julia --project=GUI/backend/build -e 'using Pkg; Pkg.instantiate()'

# Compile the Julia app (~10–20 min)
julia --project=GUI/backend/build GUI/backend/build.jl
# Output: GUI/backend/julia-app/

# Install Node dependencies (first time only)
cd GUI/electron && npm install

# Package the Electron app
npm run build           # current platform
# or: npm run build:mac / build:win / build:linux
# Output: GUI/electron/dist/
```
