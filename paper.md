---
title: "EIRE AIAI Dairy Energy Simulator: An Interactive Tool for Dairy Farm Energy and PV Adoption Analysis"
tags:
  - Python
  - dairy farming
  - energy simulation
  - photovoltaic adoption
  - agent-based modeling
  - decision support
authors:
  - name: Junlin Lu
    affiliation: 1
  - name: Hossein Khaleghy
    affiliation: 1
    # equal-contrib: true
  - name: Iias Faiud
    affiliation: 1
    # equal-contrib: true
  - name: Karl Mason
    affiliation: 1
affiliations:
  - name: University of Galway
    index: 1
date: 02 April 2026
bibliography: paper.bib
---

# Summary

The transition towards sustainable energy systems in agriculture requires accessible tools for evaluating energy consumption, renewable integration, and financial outcomes [@buckley2024farm; @breen2020photovoltaic]. Dairy farms present complex energy profiles due to heterogeneous operations, seasonal variability, and increasing electrification demands [@buckley2024farm].

EIRE AIAI Dairy Energy Simulator is an interactive, open-source software system designed to support decision-making in dairy farm energy management. The software combines simulation and economic modeling modules with a graphical user interface (GUI) that supports scenario exploration by non-specialist users. In addition to its core analytical workflows, the system includes optional large language model (LLM)-assisted functionality to support more accessible interaction and interpretation of results [@li2025review].

The system is implemented in Python and combines backend simulation modules with a multi-page interactive interface, enabling both researchers and practitioners to evaluate energy strategies without requiring extensive programming expertise.

# Statement of need

Energy transition in agriculture is not only a technical problem but also a usability problem. Dairy farms and related stakeholders increasingly need to evaluate questions such as how much energy is consumed on-farm, whether PV investment is economically justified, and how sensitive outcomes are to assumptions about prices, generation, or system sizing [@buckley2024farm; @breen2020photovoltaic]. Although simulation and financial models for these tasks are common in research, they are often fragmented across scripts, spreadsheets, or bespoke prototypes that are difficult for non-technical users to access and interpret [@arulnathan2020farm].

There is therefore a need for software that combines (1) domain-specific energy and photovoltaic analysis, (2) an accessible interactive interface, and (3) support for integrated scenario exploration. EIRE AIAI Dairy Energy Simulator addresses this need by integrating farm-energy estimation, PV financial analysis, and PV adoption scenario modeling within a multi-page GUI. In doing so, it brings together previously separate research-oriented workflows for modelling electricity consumption in Irish dairy farms and simulating solar PV adoption in Irish dairy farms into a unified software environment. An optional LLM-assisted interaction layer is also provided to support more natural user interaction with the application. This combination lowers the barrier to exploring energy scenarios and helps bridge the gap between technical modeling and practical decision support [@kyriakarakos2023design; @li2025review].

The software is relevant for researchers working on agricultural energy systems, as well as for practitioners, advisors, and policy stakeholders who require an interpretable and interactive tool for dairy-farm energy and PV planning.

# State of the field

A growing body of research has developed software and computational workflows for farm-energy analysis, photovoltaic planning, and agricultural decision support. Recent work such as the Farm Electricity System Simulator (FESS) demonstrates the value of dedicated dairy-farm electricity simulation for representing farm operations and electricity demand in a domain-specific manner [@buckley2024farm]. Other studies have addressed photovoltaic sizing and investment analysis for dairy farms, including multi-objective or financially oriented assessments of PV deployment under farm-specific operating conditions [@breen2020photovoltaic]. Broader farm-level decision-support tools have also been proposed to support sustainability-oriented technology selection and ranking [@kyriakarakos2023design], while review work has noted that many practical decision-support implementations remain fragmented across spreadsheets, scripts, and bespoke research prototypes [@arulnathan2020farm].

More specifically, recent agent-based modeling research has proposed dedicated workflows for modelling electricity consumption in Irish dairy farms and for simulating solar PV adoption in Irish dairy farms. These studies demonstrate the feasibility and value of domain-specific modeling approaches for Irish dairy-farm energy analysis, but they are primarily presented as research models rather than as unified interactive software environments for non-specialist users [@khaleghy2023modelling;@faiud2024agent].

Despite this progress, a gap remains between research-grade modeling workflows and software that can be readily used by non-specialist stakeholders. Existing approaches are often distributed across notebooks, scripts, or single-purpose analytical tools, making it difficult to combine energy estimation, PV investment appraisal, and adoption-oriented scenario analysis within one coherent workflow. In addition, many such tools are not designed around interactive exploration by users who may not be familiar with programming environments.

EIRE AIAI Dairy Energy Simulator addresses this gap by integrating multiple complementary tasks, i.e. farm-energy estimation, PV financial analysis, and PV adoption scenario modeling, i.e. within a single interactive Python-based software system. Rather than replacing detailed research workflows, the software provides a unified, reusable, and dairy-farm-specific interface through which non-specialist users can move from baseline energy estimation to investment and adoption analysis within one coherent graphical environment.

# Software design

## System architecture

The software is implemented as a modular Python application with a separation between modeling logic and user-interface components. A Streamlit-based graphical user interface provides page-level access to the main workflows, while backend modules encapsulate simulation, photovoltaic, and financial calculations. This separation supports both interactive use and future reuse of the underlying computational components outside the graphical interface.

The design was informed by pre-existing notebook-based research code developed across multiple work packages. In contrast to those exploratory implementations, the software reorganizes the relevant logic into callable modules with consistent parameter handling and a unified workflow. This architectural choice improves usability, reduces duplication across scenarios, and makes the system easier to document and extend.

## Energy and simulation models

The farm-energy estimation component represents electricity demand at the farm level using a modular equipment-oriented structure. The model combines user-configurable farm descriptors—such as herd size, number of milking units, date, milking schedule, milk cooling configuration, and water-heating choice, with component-level demand calculations to estimate daily electricity consumption, hourly load shape, and equipment-level contributions. Seasonal effects are represented through month-dependent inputs and interpolated daily behavior, allowing the tool to express changing demand patterns across the production year.

This component is designed to support practical scenario exploration rather than high-complexity physical simulation. The modeling strategy prioritizes interpretable inputs and outputs that are meaningful to farm-level decision support, while preserving a structure that remains close to the underlying research logic from which the implementation was derived.

## PV adoption and financial modeling

The software includes two complementary photovoltaic analysis layers: farm-scale return-on-investment analysis and scenario-based PV adoption modeling. The ROI component exposes notebook-aligned economic calculations under selected scenarios and years, allowing users to inspect quantities such as annual savings, annual maintenance, discounted savings, subsidy, and economic utility. The adoption component supports scenario analysis over multiple years by combining assumptions on electricity prices, PV costs, subsidy conditions, and prior adoption levels to estimate uptake trajectories across a farm population.

In the integrated software package, these capabilities are exposed through parameterized backend functions that consolidate functionality previously distributed across notebook-based research workflows. Where necessary for interactive use, some parameters are simplified or surfaced through curated scenario controls so that users can explore assumptions without directly editing research code. This design balances methodological provenance with usability and responsiveness in a GUI setting.

## Interactive graphical user interface

A central design goal of the software is accessibility for users who are not expected to work directly with notebooks or source code. The graphical interface is therefore organized as a multi-page application in which each page corresponds to a distinct analytical workflow: farm-energy estimation, PV adoption analysis, PV ROI analysis, and optional LLM-assisted question answering. This page-based structure helps users move from baseline energy estimation to investment and adoption analysis within a single consistent environment.

The GUI is not intended merely as a visual wrapper. It functions as the integration layer through which dispersed domain models become a coherent software workflow. By combining input forms, computed indicators, plots, and scenario outputs in one interface, the system supports exploratory analysis, communication of assumptions, and comparison of alternative energy strategies for dairy-farm contexts.

# Example usage

A typical workflow involves:

1. Estimating a farm’s baseline daily electricity demand using the Farm Energy Estimator, based on inputs such as herd size, number of milking units, date, milking schedule, milk cooling system, and electric water heating option.
2. Reviewing the estimated outputs, including total daily energy consumption, peak demand, peak hour, the hourly load curve, and the equipment-level energy breakdown.
3. Exploring PV adoption scenarios with the PV Adoption Model by varying assumptions such as the number of farms, simulation horizon, electricity price trend, PV cost trend, subsidy rate, and random seed.
4. Evaluating farm-scale PV investment with the PV ROI Calculator by selecting a notebook-aligned scenario and year, and optionally overriding default assumptions where needed.
5. Inspecting the resulting PV metrics, including annual savings, annual maintenance, discounted savings, subsidy, and economic utility under the active scenario assumptions.
6. Where needed, using the local LLM assistant to ask energy-related questions within the application interface.

This workflow supports both exploratory analysis and structured decision-making for dairy-farm energy assessment and PV planning.


# Research impact statement

EIRE AIAI Dairy Energy Simulator contributes a reusable research software package for interactive analysis of dairy-farm electricity demand, photovoltaic investment, and adoption-oriented energy scenarios. Its main contribution is not the introduction of a single new modeling method, but the software engineering work required to transform dispersed, research-oriented modeling components into a unified and accessible analytical workflow.

This integration has practical research value in at least three ways. First, it lowers the barrier to using domain-specific energy and PV models by allowing scenario exploration through a graphical interface rather than direct notebook manipulation. Second, it supports comparison across related analytical tasks—baseline demand estimation, farm-level PV investment appraisal, and adoption dynamics—within one software environment. Third, it provides a foundation for reproducible extension, allowing future work to refine calibration, add empirical datasets, compare policy interventions, or replace individual modeling modules without redesigning the whole application.

The software is therefore relevant not only for exploratory decision support in agricultural energy contexts, but also for teaching, prototyping, and applied research workflows that benefit from an interpretable, modifiable, and domain-specific tool for dairy-farm energy planning.


# Availability

The software is implemented in Python and distributed as an open-source repository. The repository contains the application source code, the interactive interface, and example workflow documentation required for the documented analyses. The package is intended to be run locally as a Streamlit application, allowing users to interactively estimate farm energy demand, explore photovoltaic adoption scenarios, and evaluate photovoltaic investment outcomes.

The current implementation builds on group-developed notebook-based research code and reorganizes selected model logic into a unified software structure suitable for interactive use. Documentation in the repository describes installation requirements, application launch steps, and the main analytical workflows. The repository includes an explicit open-source license, dependency specification, installation instructions, and example workflow documentation.

Repository: https://github.com/JLu2022/eire-aiai-dairy-energy-simulator 

License: MIT

Documentation: https://github.com/JLu2022/eire-aiai-dairy-energy-simulator/blob/master/README.md

# AI usage disclosure

Generative AI tools were used during the development of this software and manuscript, including ChatGPT 5.1. These tools were used to assist with drafting portions of source code, refining user-interface elements, and improving the wording of documentation and manuscript text. All AI-generated outputs were reviewed, tested, and revised by the human authors before inclusion in the repository or paper. The authors take full responsibility for the correctness, originality, licensing compliance, and scholarly claims of the software and manuscript. Core decisions regarding problem formulation, software scope, system architecture, modeling assumptions, and interpretation of outputs were made by the authors.

# Author contributions

Hossein Khaleghy and Iias Faiud contributed equally to this work. The software package builds on prior research workflows developed in their respective studies on dairy-farm electricity consumption modeling and solar PV adoption modeling. Junlin Lu led the integration of these workflows into the present interactive software package and prepared the software paper. Karl Mason supervised the work and contributed to project direction and manuscript revision.


# Acknowledgements
<!-- Add funding sources, collaborators, or institutional support here. -->
This work has been supported by research conducted with the
financial support of Research Ireland under Grant Number [21/FFPA/9040].

# References
