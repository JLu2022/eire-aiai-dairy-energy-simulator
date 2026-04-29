# EIRE AIAI Dairy Energy Simulator

An interactive Streamlit application for dairy-farm energy estimation, photovoltaic (PV) adoption scenario analysis, and notebook-aligned PV financial analysis.

## Overview

EIRE AIAI Dairy Energy Simulator provides a multi-page graphical interface for exploring three related workflows in a single environment:

- **Farm Energy Estimator** – estimate daily farm electricity demand and hourly load shape
- **PV Adoption Model** – simulate PV adoption under group-aligned WP4 scenarios
- **PV ROI Calculator** – inspect notebook-aligned annual savings, maintenance, discounted savings, subsidy, and economic utility
- **Local LLM Assistant (optional)** – ask energy-related questions through a locally running Ollama model

The application is implemented in **Python** and built with **Streamlit**.

## Installation

Create and activate a virtual environment if desired, then install dependencies:

```bash
pip install -r requirements.txt
```

Run the application locally with:

```bash
streamlit run Smart_QA.py
```

## Main workflows

### 1. Farm Energy Estimator
Estimate a farm's 24-hour electricity demand based on:

- number of cows
- number of milking units
- month and day
- morning and evening milking schedule
- milk cooling system
- electric water heating option

Outputs include:

- total daily energy consumption
- peak demand
- peak hour
- hourly load curve
- equipment-level energy breakdown

### 2. PV Adoption Model
Simulate PV adoption over time using group-aligned WP4 scenarios.

Inputs include:

- group scenario selection
- total number of farms
- initial adopters
- random seed

Outputs include:

- adoption rate over time
- cumulative adoptions
- year-by-year economic inputs and adoption probabilities

### 3. PV ROI Calculator
Inspect notebook-aligned farm-scale PV economics.

Inputs include:

- group scenario selection
- year selection
- optional override of notebook defaults

Outputs include:

- annual savings
- annual maintenance
- discounted savings
- subsidy
- economic utility
- active scenario assumptions

## Example workflows

### Farm Energy Estimator
Default example inputs:

- Cows: 55
- Milking units: 10
- Month: 1
- Day: 15
- Morning milking start: 7
- Evening milking start: 17
- Milk cooling system: DX
- Electric water heating: YES

Default example outputs:

- Total energy: 41.2 kWh
- Peak power: 7.59 kW
- Peak hour: 8:00

![Farm Energy Estimator](docs/images/farm_energy_estimator.png)

### PV Adoption Model
Default example inputs:

- Group scenario: WP4 Historical baseline (2005–2022)
- Total farms: 18000
- Random seed: 42
- Initial adopters: 0

Default example outputs:

- Final adoption rate: 2.3%
- Cumulative adoptions: 416

![PV Adoption Model](docs/images/pv_adoption.png)

### PV ROI Calculator
Default example inputs:

- Group scenario: WP4 Historical baseline (2005–2022)
- Year: 2005
- Override notebook defaults: No

Default example outputs:

- Annual savings: €1,366
- Annual maintenance: €1,000
- Discounted savings: €5,153
- Economic utility: €-44,847
- PV cost: €50,000
- Subsidy: €0

![PV ROI Calculator](docs/images/pv_roi.png)

## Optional local LLM assistant (Ollama)

This project includes an optional local question-answering interface powered by Ollama.

To use this feature:

1. Install Ollama separately on your machine.
2. Start the Ollama service locally.
3. Pull a compatible local model, for example:
   ```bash
   ollama pull llama3.2:3b
   ```
4. Run the Streamlit app:
   ```bash
   streamlit run Smart_QA.py
   ```

Notes:

- The Ollama-based assistant is optional and is not required for the core analytical workflows.
- Model availability and licensing depend on the model selected by the user.
- This repository does not redistribute Ollama binaries or model weights.

## Data

This repository does not redistribute datasets whose licensing status is uncertain. Where external data are required, users should upload their own CSV files in the expected format. The repository includes only representative example inputs where appropriate.

## Project structure

```text
eire-aiai-dairy-energy-simulator/
├── Smart_QA.py
├── pages/
│   ├── Farm_Energy_Estimator.py
│   ├── PV_Adoption.py
│   └── PV_ROI.py
├── src/
│   ├── core/
│   │   ├── abm_model.py
│   │   ├── adoption_models.py
│   │   ├── finance.py
│   │   ├── group_models.py
│   │   ├── roi.py
│   │   ├── simulate.py
│   │   └── solar.py
│   └── utils/
│       └── ollama_client.py
├── docs/
│   └── images/
├── tests/
├── requirements.txt
└── README.md
```
