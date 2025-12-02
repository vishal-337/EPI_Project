# Opioid Epidemic Network Modeling - 10 Minute Presentation

## Slide 1: Title Slide (30 seconds)
**Title:** Opioid Epidemic Network Modeling: Spatial Diffusion of High-Prescribing Behaviors

**Subtitle:** Analyzing Geographic Spread Using Network Science and Computational Epidemiology

**Team Members:**
- Rishi Bandi
- Vishal Maradana

**Date:** December 2, 2025

**Speaking Lines:**
"Good morning. Today we'll be presenting our work on modeling the opioid epidemic as a network diffusion process. I'm [Name] and this is [Name], and we'll show you how geographic proximity drives the spread of high-prescribing behaviors across states and counties."

---

## Slide 2: Motivation & Problem Statement (1.5 minutes)
**Key Points:**
- The US Opioid Crisis: 500,000+ deaths from 1999-2019
- Traditional approaches treat states/counties in isolation
- **Key Question:** How does high-prescribing behavior spread across geographic boundaries?
- **Hypothesis:** Opioid prescribing patterns diffuse spatially through neighbor influence, similar to a contagion

**Why This Matters:**
- Understanding diffusion mechanisms can inform policy interventions
- Early identification of "super-spreader" regions enables targeted prevention
- Network-based models can predict future hotspots before they emerge

**Visual:** None needed (text-heavy slide)

**Speaking Lines:**
"The opioid crisis has claimed over 500,000 lives in the United States from 1999 to 2019. Traditional epidemiological approaches often treat states and counties as independent units, but we believe this misses a critical mechanism: spatial diffusion.

Our key research question is: How does high-prescribing behavior spread across geographic boundaries? We hypothesize that opioid prescribing patterns diffuse spatially through neighbor influence, similar to how a virus spreads through a network.

Why does this matter? Understanding these diffusion mechanisms can inform targeted policy interventions. If we can identify 'super-spreader' regions early, we can prevent the epidemic from reaching new areas. Network-based models allow us to predict future hotspots before they emerge, giving policymakers a crucial head start."

## Slide 3: Our Approach - Network Science Framework (1.5 minutes)
**Key Points:**
- **Core Idea:** Model high-prescribing as a "contagion" spreading through a network
- **Binary Adoption:** States/Counties become "infected" when dispensing rate > threshold (87.35)
- **Network Construction:** 
  - Edges = influence relationships (State A → State B)
  - Only geographically adjacent states can influence each other
  - Temporal decay: recent adopters are stronger influencers
- **Why It Works:**
  - Captures spatial autocorrelation (neighbors influence neighbors)
  - Accounts for temporal precedence (cause before effect)
  - Enables predictive modeling and intervention simulation

**Visual:** Use `influence_network_graph.png` or `influence_network.png` to show the state-level network structure

**Speaking Lines:**
"Here's our core approach. We model high-prescribing as a contagion spreading through a network. [Point to network graph] Each node represents a state, and each edge represents an influence relationship—State A influenced State B to adopt high-prescribing behaviors.

We define a state as 'infected' when its opioid dispensing rate exceeds 87.35 prescriptions per 100 persons—this is the 75th percentile threshold that identifies the worst of the worst prescribers.

Our network construction has three key constraints: First, only geographically adjacent states can influence each other—this captures the physical reality of cross-border patient flow. Second, we use temporal decay—recent adopters are stronger influencers than states that turned high years ago. Third, we require temporal precedence—the source state must be high before the target state adopts.

Why does this work? First, it makes intuitive sense—neighbors influence neighbors. If Tennessee has high prescribing rates, it's likely to affect Georgia next door. Second, we only count influence if the source state was high before the target state—this ensures we're capturing real cause and effect, not just coincidence. And third, this framework lets us do two powerful things: predict which states will become high next year, and test 'what if' scenarios—like what would have happened if we had blocked Tennessee from influencing its neighbors. We'll show you those results later."

## Slide 4: Methodology - State-Level Analysis (1 minute)
**Key Points:**
- **Spatial Autoregressive Model (SAR):**
  - Formula: Y = βY(t-1) + γWY + ε
  - β = path dependence (0.981) - states follow their own trajectory
  - γ = neighbor spillover (0.009) - modest but significant neighbor influence
- **Network Metrics:**
  - Out-Degree: Direct spreader score
  - Eigenvector Centrality: Connectedness to other influencers
  - Betweenness: Bridge/gateway role

**Visual:** Show a simple diagram of the SAR model equation, or use `state_influence_rankings.csv` data in a table format

**Speaking Lines:**
"For state-level analysis, we use a Spatial Autoregressive Model, or SAR. The formula is Y equals beta times Y at time t-minus-1, plus gamma times W times Y, plus epsilon.

Beta, at 0.981, represents path dependence—states heavily follow their own trajectory. This means once a state starts down a high-prescribing path, it tends to continue. Gamma, at 0.009, represents neighbor spillover—this is modest but statistically significant. Even a small neighbor influence can compound over time.

We also compute network centrality metrics: Out-Degree measures direct spreader score—how many neighbors did this state infect? Eigenvector Centrality measures connectedness to other influencers—are you connected to the major players? And Betweenness measures the bridge or gateway role—do you connect different regions of the network?"

## Slide 5: Methodology - County-Level Analysis (1 minute)
**Key Points:**
- **Intra-State Networks:** Build separate networks within each state
- **State-Specific Thresholds:** 75th percentile per state (normalizes for regional differences)
- **Super-Spreader Detection:** Counties that adopt before their state does
- **Case Study:** Georgia-specific predictive model

**Visual:** Use `top_influential_counties.png` to show county-level rankings

**Speaking Lines:**
"At the county level, we take a different approach. Instead of one massive national network, we build separate influence networks within each state. This makes sense because county-to-county influence is primarily local.

We use state-specific thresholds—the 75th percentile of each state's dispensing rates. This normalizes for regional differences. A 'high' county in California might have a different absolute rate than a 'high' county in West Virginia, but relative to their peers, they're both extreme.

We also identify super-spreader counties—those that adopted high-prescribing behaviors before their state did. These are likely the early entry points for the epidemic. We also built a case study focusing specifically on Georgia to test county-level predictive models."

## Slide 6: Data Overview (1 minute)
**Key Points:**
- **Source:** CDC Opioid Dispensing Rate Data
- **State-Level:**
  - 2006-2018 (extended to 2023)
  - 50 states + DC
  - ~650 state-year observations
- **County-Level:**
  - 3,000+ counties
  - ~40,000 county-year observations
- **Variables:** Opioid dispensing rate (prescriptions per 100 persons)
- **Preprocessing:** Merged datasets, cleaned FIPS codes, handled missing values

**Visual:** Show a sample row from `dispensing_state_year.csv` or a data table screenshot

**Speaking Lines:**
"Our data comes from the CDC's Opioid Dispensing Rate dataset. At the state level, we have data from 2006 to 2018, extended to 2023, covering all 50 states plus DC—that's about 650 state-year observations.

At the county level, we have over 3,000 counties with approximately 40,000 county-year observations. The key variable is opioid dispensing rate, measured as prescriptions per 100 persons.

We did significant preprocessing: merging multiple CDC datasets, cleaning FIPS codes to ensure proper geographic matching, and handling missing values. This gave us a clean panel dataset ready for network analysis."

## Slide 7: State-Level Results - Spatial Diffusion Confirmed (1.5 minutes)
**Key Points:**
- **R² = 0.884** - Strong spatial autocorrelation confirmed
- **Path Dependence (β = 0.981):** States heavily follow their own trajectory
- **Neighbor Spillover (γ = 0.009):** Modest but statistically significant neighbor influence
- **Primary Influencers:** Tennessee (#1 Out-Degree), Nevada, South Carolina
- **Southeast Cluster:** Distinct high-prescribing region identified

**Visual:** 
- Use `state_influence_rankings.csv` in a bar chart (create from data)
- Show `top_influencers_bar.png` for top 10 states
- Optionally show `historical_adoption_curve.png` to show temporal spread

**Speaking Lines:**
"Now for our state-level results. [Point to R² value] We achieved an R-squared of 0.884—this confirms strong spatial autocorrelation. Our hypothesis is validated: geography drives the crisis.

Breaking down the SAR model results: Path dependence, beta equals 0.981, shows that states heavily follow their own trajectory. But neighbor spillover, gamma equals 0.009, while modest, is statistically significant. This means even small neighbor influence compounds over time.

[Point to rankings chart] Our network analysis identified the primary influencers: Tennessee ranks number one in Out-Degree—it directly infected the most neighbors. Nevada and South Carolina also rank highly. [Point to adoption curve if shown] The Southeast forms a distinct high-prescribing cluster, with early adopters in 2006-2007 spreading to neighbors over the following years."

## Slide 8: County-Level Results - Early Warning Signs (1 minute)
**Key Points:**
- **Super-Spreader Counties:** Identified counties that adopted 6 years before their state
- **Examples:** Montana counties (2006 vs. state 2012), Kansas counties (2006 vs. state 2011)
- **Implication:** These counties served as early entry points for the epidemic
- **Texas Dominance:** Top influential counties are in Texas (Bowie, Gregg, Wichita)

**Visual:** 
- Use `county_superspreaders.csv` data in a table showing top 5-10 early adopters
- Show `top_superspreaders.png` if available

**Speaking Lines:**
"At the county level, we found striking early warning signs. [Point to table] We identified super-spreader counties that adopted high-prescribing behaviors up to 6 years before their state did.

For example, multiple Montana counties crossed the threshold in 2006, but the state average didn't cross until 2012—that's a 6-year head start. Similarly, Kansas counties were high in 2006, but the state didn't reach that level until 2011.

The implication is clear: these counties served as early entry points for the epidemic. They were the canaries in the coal mine. [Point to rankings] We also found that Texas dominates the most influential counties list—Bowie, Gregg, and Wichita counties have the highest influence scores, likely due to Texas's large size and many internal connections."

## Slide 9: Predictive Performance (1 minute)
**Key Points:**
- **Diffusion Simulation:** 42% accuracy in predicting which states become "High" next year
- **Baseline Comparison:** Random guessing = ~3% accuracy
- **Our Model:** 5-6x better than random
- **Continuous Prediction:** R² = 0.884 for state-level rate prediction

**Visual:** 
- Use `simulation_results.csv` data in a line chart showing accuracy over years
- Show `continuous_prediction_scatter.png` (predicted vs. actual rates)

**Speaking Lines:**
"Now let's talk about predictive performance. [Point to scatter plot] We ran a diffusion simulation where, given the set of high states in year T, we predict which states will become high in year T-plus-1.

Our model achieves 42% accuracy. That might not sound impressive, but consider the baseline: random guessing would only get about 3% accuracy. Our model is 5 to 6 times better than random.

[Point to scatter plot] For continuous prediction of dispensing rates, we achieve an R-squared of 0.884—the same strong performance we saw in the spatial autoregressive model. The scatter plot shows our predictions are tightly clustered around the diagonal, indicating good predictive power."

## Slide 10: Policy Intervention Analysis (1 minute)
**Key Points:**
- **Counterfactual Simulation:** "What if we blocked specific states?"
- **Finding 1:** Blocking Tennessee alone = **Zero Impact** (network redundancy)
- **Finding 2:** Blocking regional cluster (TN+AL+SC) = **-3 states** prevented from becoming High
- **Policy Implication:** Coordinated regional interventions > piecemeal state laws

**Visual:** 
- Use `intervention_results.csv` data in a line chart
- Show `intervention_impact_line.png` comparing Baseline vs. Block_TN vs. Block_Region

**Speaking Lines:**
"Perhaps our most actionable finding comes from counterfactual policy simulations. We asked: What if we had blocked specific states from influencing their neighbors? [Point to chart]

Finding number one: Blocking Tennessee alone—the number one influencer—resulted in zero impact. Why? Network redundancy. If Tennessee is blocked, Alabama or South Carolina still infect the neighbors. The pressure finds another path.

Finding number two: Blocking a regional cluster—Tennessee, Alabama, and South Carolina together—prevented 3 states from becoming high. This creates a 'firebreak' in the network.

The policy implication is clear: Coordinated regional interventions are far more effective than piecemeal state laws. Florida's pill mill law in 2011 was important, but it would have been more effective as part of a coordinated Southeast compact."

## Slide 11: Conclusions (1 minute)
**Key Takeaways:**
1. **Geography matters:** Spatial proximity drives opioid prescribing diffusion (R² = 0.884)
2. **Super-spreaders identified:** Tennessee (national), Florida (regional hub), specific counties (early adopters)
3. **Predictive power:** Network models can forecast hotspots with 42% accuracy
4. **Policy insight:** Regional coordination needed; single-state interventions ineffective

**Future Work:**
- Incorporate policy variables (PDMP implementation dates)
- Model county-to-county spillover across state borders
- Extend to other substance abuse epidemics

**Visual:** Summary bullet points (text slide)

**Speaking Lines:**
"Let me summarize our key takeaways. First, geography matters—spatial proximity drives opioid prescribing diffusion, with an R-squared of 0.884. Second, we've identified super-spreaders at multiple scales: Tennessee at the national level, Florida as a regional hub, and specific counties as early adopters. Third, our network models have predictive power—we can forecast hotspots with 42% accuracy, far better than random. And fourth, our policy insight is that regional coordination is needed—single-state interventions are ineffective due to network redundancy.

For future work, we'd like to incorporate policy variables like PDMP implementation dates, model county-to-county spillover across state borders, and extend this framework to other substance abuse epidemics. Thank you."

## Slide 12: Thank You & Questions (30 seconds)
**Title:** Thank You!

**Contact/Repository:** [Your GitHub repo link]

**Questions?**

**Speaking Lines:**
"Thank you for your attention. We're happy to take any questions. Our code and data are available in our GitHub repository, which is linked on this slide."

## Visual Summary - Which Files to Use:

1. **Slide 3:** `outputs/influence_network_graph.png` or `outputs/influence_network.png`
2. **Slide 5:** `outputs/top_influential_counties.png`
3. **Slide 7:** `outputs/top_influencers_bar.png` + `outputs/historical_adoption_curve.png`
4. **Slide 8:** `outputs/top_superspreaders.png` (if exists) or create table from `county_superspreaders.csv`
5. **Slide 9:** `outputs/continuous_prediction_scatter.png` + line chart from `simulation_results.csv`
6. **Slide 10:** `outputs/intervention_impact_line.png` or create from `intervention_results.csv`

---

## Timing Breakdown (Total: 10 minutes):
- Slide 1: 0:30
- Slide 2: 1:30
- Slide 3: 1:30
- Slide 4: 1:00
- Slide 5: 1:00
- Slide 6: 1:00
- Slide 7: 1:30
- Slide 8: 1:00
- Slide 9: 1:00
- Slide 10: 1:00
- Slide 11: 1:00
- Slide 12: 0:30

**Total: 10:00 minutes**

---

## Presentation Tips:

1. **Practice transitions** between slides - especially when switching from state to county analysis
2. **Emphasize the R² = 0.884 result** - this is your strongest quantitative finding
3. **Tell a story:** Start with the crisis → Our approach → Results → Policy implications
4. **Use the network graph** (Slide 3) to visually explain the concept before diving into numbers
5. **Highlight the policy finding** (Slide 10) - this makes your work actionable
6. **Keep technical details brief** - focus on intuition in Slide 4, save equations for backup slides if needed
7. **Practice with a timer** - 10 minutes is strict, so know which slides you can speed through if needed

