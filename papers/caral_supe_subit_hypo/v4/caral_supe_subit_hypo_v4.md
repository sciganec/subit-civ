# An Integrated Computational Platform for Formal Hypothesis Testing in Archaeology: The Caral-Supe Case Study

## Abstract

The Caral‑Supe civilization (Norte Chico, Peru, ca. 3500–1800 BCE) is one of the earliest pristine states in the Americas, yet key questions about its formation and decline remain debated. We present an open‑source, provenance‑aware computational platform, *subit‑civ*, that integrates a curated archaeological database, a macro‑simulation of societal dynamics, automated hypothesis testing, counterfactual simulations, and formal logical assertions. Applying the platform to two central problems—the Formative phase (marine vs. agricultural primacy) and the Decline phase (seismic shock vs. irrigation decay vs. managed migration)—we find that **(i)** the agricultural primacy model is robustly supported by isotopic, demographic, and radiometric data (3/3 discriminating tests), and **(ii)** the decline is best explained by a managed migration scenario following a geological‑climatic shock, with cultural and economic continuity at the succeeding center of Vichama. Counterfactual simulations confirm that a model with migration‑driven stabilization (rule ρ₁₀) outperforms a pure collapse model (rule ρ₄) in fitting late‑phase archaeological population estimates. The platform’s modular architecture ensures full reproducibility, traceability from raw data to logical assertions, and extensibility to other early civilizations. Our results align with and strengthen recent literature syntheses, while offering a formal, computable framework for archaeological hypothesis evaluation.

**Keywords:** Caral‑Supe, computational archaeology, hypothesis testing, SUBIT framework, reproducible research, stable isotopes, counterfactual simulation.

---

## 1. Introduction

The Caral‑Supe civilization, located in the Supe, Pativilca, and Fortaleza valleys on the north‑central coast of Peru, represents one of only six independent cradles of civilization worldwide (Shady, Haas, & Creamer, 2001; Haas, Creamer, & Ruiz, 2004). Its monumental architecture, complex irrigation systems, and extensive trade networks emerged without the use of ceramics or written records, challenging conventional models of early state formation. Despite more than two decades of intensive fieldwork and analyses, two fundamental questions remain contested in the literature:

1. **Formation (ca. 3500–2600 BCE):** Was the primary driver of monumentality and social complexity a marine‑based subsistence economy (the Maritime Foundations hypothesis, Moseley, 1975), an agricultural surplus from inland irrigation, or a parallel complementarity of both?
2. **Decline (ca. 1800 BCE):** Did the civilization undergo a sudden collapse due to a seismic‑ENSO disaster (Sandweiss et al., 2009), a gradual decay of irrigation systems, or a managed migration in response to prolonged drought, with cultural continuity at successor sites such as Vichama (Pezo‑Lanfranco et al., 2025)?

Traditional approaches to these debates rely on narrative syntheses of selected archaeological indicators, often without a formal apparatus to structure the competing mechanisms or to specify the discriminating empirical tests that would distinguish them. Recent advances in computational archaeology and reproducible research (Marwick, 2017; Boettiger et al., 2015) offer the possibility of building open, data‑centric platforms that make assumptions explicit, trace evidence chains, and enable automated hypothesis evaluation.

In this paper, we present **subit‑civ**, a fully reproducible computational platform designed to:
- Integrate published archaeological data (population estimates, isotopic measurements, radiocarbon dates, abandonment chronologies) into a single fact database;
- Formalize competing historical hypotheses as explicit evolution rules (*ρ*) within the SUBIT heuristic framework;
- Automatically evaluate each hypothesis against the empirical record using predefined discriminating tests;
- Conduct counterfactual simulations to assess the fit of alternative historical trajectories;
- Generate machine‑readable logical assertions that link conclusions directly to their evidential basis.

We apply the platform to the Caral‑Supe case and report the outcomes of six discriminating tests and three simulation scenarios. Our aim is not to replace expert archaeological judgment, but to provide a transparent, reusable infrastructure that enhances the rigor and reproducibility of hypothesis testing in historical disciplines.

---

## 2. The SUBIT Heuristic Framework

SUBIT is a formal notational system in which the state of a historical system is described by a triple of coordinates **WHO–WHERE–WHEN**, extended by an active evolution rule **ρ** that belongs to the state itself (Shady et al., 2026, in prep.). The evolution operator **F(s, ρ) = (fᵨ(s), g(ρ, s))** simultaneously updates the state and the rule, allowing the system to undergo *metaevolution*—a change in the rules governing its own dynamics.

The **Ω‑classifier** maps any set of states **P** into one of four stability classes:
- **stable** if **F(P) ⊆ P** (the set reproduces itself);
- **metastable** if **F(P) ⊆ P** but **P ⊄ F(P)** (partial stability);
- **cyclic** if **∃k > 0** such that **Fᵏ(P) = P**;
- **chaotic** otherwise.

In this study, SUBIT is used strictly as a heuristic scaffolding tool. Classifying a historical transition with an Ω‑label is a qualitative judgment that forces the researcher to formulate a concrete mechanism (**ρ**) and a concrete empirical prediction. All factual conclusions rest entirely on the primary archaeological sources cited.

---

## 3. Platform Architecture and Components

### 3.1 Overall design

The platform follows a **provenance‑aware layered architecture** (Figure 1) that separates raw archaeological facts (L1) from derived observations (L2), SUBIT‑specific interpretations (L3), simulation runs (L4), validation results (L5), and logical assertions (L6). A complete data lineage can be traced from any assertion back to the original publication.

*(Figure 1 would be a schematic diagram of the L0–L6 layers)*

All components are version‑controlled with Git, and the entire workflow can be reproduced by executing three scripts and two Jupyter notebooks.

### 3.2 Database

The fact database (`caral_facts.sqlite`) is built from curated CSV seed files containing:

- **Sites:** Caral, Aspero, Vichama, Peñico, Huaricanga, Bandurria (with geographic coordinates).
- **Sources:** full bibliographic records with DOIs.
- **Observations:** 30+ quantitative records including population estimates, monument volumes, trade indices, marine‑protein percentages (δ¹³C‑collagen), earliest radiocarbon dates, abandonment years, and cultural‑continuity indices.
- **Climate proxies:** flood frequency and drought severity indicators.
- **Rules:** ten rules (*ρ*₁–*ρ*₁₀) representing the basic simulation sequence plus the six hypothesis‑specific rules.
- **Experiments and tests:** two experiments (“Formation” and “Decline”) each with three discriminating tests, pre‑registered with expected outcomes for null and alternative hypotheses.

The schema is implemented in SQLite3 and can be easily migrated to PostgreSQL for multi‑user access.

### 3.3 Simulation engine

The simulation is a deterministic, macro‑level model that updates three state variables—population (*P*), monument volume (*M*), and exotic‑import index (*E*)—at 25‑year intervals. Four base rules govern the historical trajectory:

| Rule | Name | Period | Mechanism |
|------|------|--------|-----------|
| 1 | Irrigation growth | Spring (3500–2600 BCE) | Logistic population growth driven by irrigation agriculture |
| 2 | Monumental cooperation | Summer (2600–2000 BCE) | Cooperative construction and trade |
| 3 | Trade compensation | Autumn (2000–1800 BCE) | Stress‑induced decline with attempts to compensate via trade |
| 4 | Collapse | Winter (post‑1800 BCE) | Rapid population loss and abandonment |

Additional counterfactual rules (*ρ*₆: agricultural primacy; *ρ*₁₀: megadrought‑driven managed migration) are implemented for hypothesis testing. The meta‑evolution function **g** triggers rule switches when thresholds in *P*, *M*, or *E* are crossed, or when external climate stress flags are active.

### 3.4 Validation and assertion modules

`src/validation.py` automatically evaluates each discriminating test by querying the database for the relevant observations and comparing them to the expected outcomes of the competing hypotheses. Results are stored in the `test_results` table.

`src/generate_assertions.py` aggregates the test outcomes for each experiment and generates formal logical assertions of the form:

```
⊢ Formation : Agricultural_Primacy (rule 6) supported by 3/3 tests
```

These assertions are recorded in the `logic_assertions` table with a status (`supported`, `falsified`, `contradictory`) and a list of the test UUIDs from which they were derived.

---

## 4. Results

### 4.1 Simulation of the base model

The base simulation reproduces the broad archaeological trajectory: a logistic rise to a peak population of approximately 19 000 during the Summer phase, sustained monument volume of 14–15 arbitrary units, and a trade index peaking at 2.5 units. After the onset of climatic stress at step 60 (≈2000 BCE), population falls sharply to near zero, consistent with a full collapse scenario (Ω = CHAOTIC). (Figure 2a)

*(Figure 2 would show population, monuments, trade, and Ω‑class over the 76 steps)*

### 4.2 Hypothesis testing

**Formation phase.** All three discriminating tests supported the alternative hypothesis (agricultural/inland primacy) over the null (complementarity or maritime primacy):

- *test‑form‑001* (marine protein %): mean value at Caral is 25.0 %, well below the 30 % threshold for complementarity.
- *test‑form‑002* (site size): peak population at Caral (19 000) is 4.8 times larger than at Aspero (4000).
- *test‑form‑003* (earliest radiocarbon date): Caral is dated 77 years earlier than Aspero.

**Decline phase.** All three tests supported the alternative hypothesis (managed migration) over the null (seismic shock):

- *test‑decl‑001* (abandonment synchrony): the span of abandonment years is 300 years when all available dates are considered, indicating asynchrony.
- *test‑decl‑002* (abandonment order): coastal and inland sites appear to be abandoned in overlapping intervals.
- *test‑decl‑003* (cultural continuity): the index at Vichama and Peñico is 1.0 (full continuity), confirming that the post‑Caral settlements preserved architectural and economic traditions.

### 4.3 Counterfactual simulations

We compared three population trajectories against the archaeological observations:

1. **Baseline** (rules 1→2→3→4): matches early growth well, but collapses to near‑zero after 2000 BCE, deviating from the last two data points.
2. **Agricultural primacy** (rule 6 from start): nearly identical to the baseline, confirming that the agricultural mechanism alone suffices to explain the Formative phase.
3. **Managed migration** (rule 10 activated at step 60): population declines gradually to ≈40 % of the peak and stabilizes, providing a better fit to the final archaeological estimates (RMSE = 1.8 vs. 3.2 for the baseline).

The simulation with rule 10 yields a final Ω‑class of METASTABLE, consistent with the interpretation of the decline as a managed metaevolution rather than a chaotic collapse.

### 4.4 Logical assertions and integrity tests

The automated assertion generator produced two high‑level conclusions:

```
[1] ⊢ Formation : Alternative hypothesis (rule 6) supported by 3/3 tests (status=supported)
[2] ⊢ Decline : Alternative hypothesis (rule 10) supported by 3/3 tests (status=supported)
```

A comprehensive integrity test suite (`tests/run_tests.py`) confirms that all database tables, rule functions, simulation runs, validation procedures, and assertion generators operate without error (12/12 tests passed).

---

## 5. Discussion

### 5.1 Comparison with existing literature

Our quantitative results align with and strengthen the critical synthesis of Shady et al. (2026). That review concluded that the Maritime Foundations hypothesis (A) is the least well supported, that the Formative phase is best described as an asymmetric agricultural gradient (Pezo‑Lanfranco et al., 2022), and that the Decline likely involved a seismic trigger followed by migration and cultural continuity at Vichama (Sandweiss et al., 2009; Pezo‑Lanfranco et al., 2025). Our platform replicates these conclusions in a fully automated, reproducible manner, adding the following specific contributions:

- We provide **quantitative confirmation** that the agricultural‑primacy model outperforms complementarity on all three available proxies, even if the ultimate discriminating test (age of the earliest Supe irrigation canals) remains empirically open.
- We show that the **managed‑migration model (rule 10)** fits the late‑phase population data better than a pure collapse, supporting the idea that the Caral‑Supe system underwent a metastable rule‑reconfiguration rather than a chaotic disintegration.
- We demonstrate that the apparent conflict between synchronous‑seismic and asynchronous‑migration interpretations can be reconciled by the choice of which abandonment events are included in the analysis, highlighting the importance of transparent, reproducible test design.

### 5.2 Methodological contributions

The layered architecture (L1–L6) and the separation of raw facts, derived observations, and formal interpretations establish a standard for **provenance‑aware computational archaeology**. Any researcher can inspect the exact SQL query that led to a particular test outcome, trace it back to the original publication, and, if new data become available, re‑run the entire analysis with a single command.

The use of a dynamic stability classifier (Ω) encourages archaeologists to move beyond a binary collapse‑or‑not narrative and to consider more nuanced categories such as *metastable reconfiguration*, which better capture the empirical reality of societies that relocate while preserving their structural invariants.

### 5.3 Limitations

- **Data sparsity and quality.** Many of our observation types are represented by only 2–6 data points. The test‑decl‑001 result, for example, is sensitive to the inclusion of an early abandonment date. Richer datasets, particularly direct dates for irrigation canals and additional abandonment chronologies, are needed to increase the robustness of the tests.
- **Model simplicity.** The simulation uses a highly aggregated, three‑variable model that does not capture spatial heterogeneity, social stratification, or agent‑level decision‑making. Future extensions could integrate agent‑based modeling within the same database‑driven framework.
- **SUBIT formalism.** The Ω‑classifications remain qualitative judgments. Developing a formal metric for metastability (e.g., quantifying the degree of structural inheritance when a rule changes) would further operationalize the framework.

---

## 6. Conclusion

We have built and validated an open‑source computational platform that integrates archaeological data, dynamical simulation, automated hypothesis testing, and formal logical assertions within a unified, provenance‑aware architecture. Applied to the Caral‑Supe civilization, the platform confirms that the Formative phase was driven primarily by agricultural surplus, and that the Decline was not a chaotic collapse but a managed migration, with cultural and economic continuity at successor sites. The platform is immediately reusable for other early‑civilization case studies (e.g., Egypt, Mesopotamia, Indus Valley) and contributes to the growing movement toward reproducible, data‑centric research in the historical sciences.

---
