import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# =====================================================
# PAGE SETUP
# =====================================================

st.set_page_config(
    page_title="UK DSGE Simulator",
    layout="wide"
)

st.title("UK DSGE Simulator")
st.subheader("A simplified Bank of England-style teaching model")

st.markdown("""
This app uses a calibrated, reduced-form New Keynesian open-economy model for teaching.

It is not a full estimated DSGE model. It is designed to help students understand
how different shocks transmit through output, inflation, interest rates and the exchange rate.
""")

# =====================================================
# SIDEBAR GUIDE
# =====================================================

st.sidebar.title("Teaching Guide")

st.sidebar.info("""
Recommended sequence:

1. COVID demand contraction
2. 2022 energy / cost-push inflation
3. Monetary tightening
4. Sterling depreciation

Teaching workflow:

Predict -> Simulate -> Explain
""")

# =====================================================
# SCENARIO AND MODEL FUNCTIONS
# =====================================================

def get_base_parameters():
    return {
        "rho_y": 0.60,
        "rho_pi": 0.65,
        "rho_i": 0.80,
        "rho_q": 0.60,
        "alpha_r": 0.30,
        "alpha_q": 0.03,
        "alpha_energy_y": 0.015,
        "kappa": 0.20,
        "gamma_q": 0.025,
        "gamma_energy_pi": 0.035,
        "phi_pi": 1.50,
        "phi_y": 0.40,
        "eta_i": 0.80,
        "shock_persistence": 0.70,
        "shock_size": 1.0,
        "shock_type": "Demand",
        "shock_sign": 1.0
    }


def get_scenario_parameters(scenario):
    params = get_base_parameters()

    if scenario == "COVID demand contraction":
        params["shock_type"] = "Demand"
        params["shock_size"] = 4.0
        params["shock_sign"] = -1.0
        params["shock_persistence"] = 0.55
        params["phi_pi"] = 1.50
        params["phi_y"] = 0.50

    elif scenario == "2022 energy / cost-push inflation":
        params["shock_type"] = "Energy"
        params["shock_size"] = 40.0
        params["shock_sign"] = 1.0
        params["shock_persistence"] = 0.80
        params["phi_pi"] = 1.70
        params["phi_y"] = 0.35

    elif scenario == "Monetary tightening":
        params["shock_type"] = "Monetary policy"
        params["shock_size"] = 1.0
        params["shock_sign"] = 1.0
        params["shock_persistence"] = 0.65
        params["phi_pi"] = 2.20
        params["phi_y"] = 0.40

    elif scenario == "Sterling depreciation":
        params["shock_type"] = "Exchange rate"
        params["shock_size"] = 12.0
        params["shock_sign"] = 1.0
        params["shock_persistence"] = 0.70
        params["phi_pi"] = 1.60
        params["phi_y"] = 0.40

    elif scenario == "Demand expansion":
        params["shock_type"] = "Demand"
        params["shock_size"] = 2.0
        params["shock_sign"] = 1.0
        params["shock_persistence"] = 0.60
        params["phi_pi"] = 1.50
        params["phi_y"] = 0.50

    return params


def simulate_model(params, T=40):

    y = np.zeros(T)
    pi = np.zeros(T)
    rate = np.zeros(T)
    q = np.zeros(T)

    demand_shock = np.zeros(T)
    energy_shock = np.zeros(T)
    cost_push_shock = np.zeros(T)
    monetary_shock = np.zeros(T)
    exchange_rate_shock = np.zeros(T)

    generic_shock = np.zeros(T)
    generic_shock[1] = params["shock_sign"] * params["shock_size"]

    for t in range(2, T):
        generic_shock[t] = params["shock_persistence"] * generic_shock[t - 1]

    if params["shock_type"] == "Demand":
        demand_shock = generic_shock.copy()

    elif params["shock_type"] == "Energy":
        energy_shock = generic_shock.copy()

    elif params["shock_type"] == "Cost-push":
        cost_push_shock = generic_shock.copy()

    elif params["shock_type"] == "Monetary policy":
        monetary_shock = generic_shock.copy()

    elif params["shock_type"] == "Exchange rate":
        exchange_rate_shock = generic_shock.copy()

    for t in range(1, T):

        rate[t] = (
            params["rho_i"] * rate[t - 1]
            + (1 - params["rho_i"]) * (
                params["phi_pi"] * pi[t - 1]
                + params["phi_y"] * y[t - 1]
            )
            + monetary_shock[t]
        )

        q[t] = (
            params["rho_q"] * q[t - 1]
            - params["eta_i"] * (rate[t] - rate[t - 1])
            + exchange_rate_shock[t]
        )

        y[t] = (
            params["rho_y"] * y[t - 1]
            - params["alpha_r"] * (rate[t - 1] - pi[t - 1])
            + params["alpha_q"] * q[t - 1]
            + demand_shock[t]
            - params["alpha_energy_y"] * energy_shock[t]
        )

        pi[t] = (
            params["rho_pi"] * pi[t - 1]
            + params["kappa"] * y[t]
            + params["gamma_q"] * q[t]
            + params["gamma_energy_pi"] * energy_shock[t]
            + cost_push_shock[t]
        )

    return y, pi, rate, q


def calculate_summary(y, pi, rate, q):

    summary = {
        "peak_inflation": float(np.max(pi)),
        "inflation_trough": float(np.min(pi)),
        "output_peak": float(np.max(y)),
        "output_trough": float(np.min(y)),
        "peak_rate": float(np.max(rate)),
        "rate_trough": float(np.min(rate)),
        "peak_fx": float(np.max(q)),
        "fx_trough": float(np.min(q)),
        "inflation_peak_period": int(np.argmax(pi)),
        "output_trough_period": int(np.argmin(y)),
        "rate_peak_period": int(np.argmax(rate)),
        "fx_peak_period": int(np.argmax(q))
    }

    return summary


def make_summary_table(summary):

    return {
        "Metric": [
            "Peak inflation deviation from target",
            "Lowest inflation deviation from target",
            "Peak output gap",
            "Lowest output gap",
            "Peak Bank Rate response",
            "Peak sterling depreciation",
            "Quarter of inflation peak",
            "Quarter of output trough",
            "Quarter of peak Bank Rate",
            "Quarter of peak FX effect"
        ],
        "Value": [
            f"{summary['peak_inflation']:.2f} percentage points",
            f"{summary['inflation_trough']:.2f} percentage points",
            f"{summary['output_peak']:.2f}% of potential GDP",
            f"{summary['output_trough']:.2f}% of potential GDP",
            f"{summary['peak_rate']:.2f} percentage points",
            f"{summary['peak_fx']:.2f}% depreciation",
            f"Quarter {summary['inflation_peak_period']}",
            f"Quarter {summary['output_trough_period']}",
            f"Quarter {summary['rate_peak_period']}",
            f"Quarter {summary['fx_peak_period']}"
        ]
    }


def create_mpc_briefing(scenario, params, summary):

    shock_type = params["shock_type"]

    if shock_type == "Energy":

        briefing = f"""
### MPC Briefing Note: Energy / Cost-Push Inflation Scenario

The simulation suggests an energy-driven inflation episode. Inflation rises by approximately
**{summary['peak_inflation']:.1f} percentage points above target**, reaching its peak in
**Quarter {summary['inflation_peak_period']}**.

Economic activity weakens, with the output gap reaching **{summary['output_trough']:.1f}% of potential GDP**
in **Quarter {summary['output_trough_period']}**. Bank Rate rises by approximately
**{summary['peak_rate']:.1f} percentage points** as policymakers respond to above-target inflation.

This resembles a stagflation-style shock: inflation increases while output weakens. The policy challenge is
that tighter monetary policy may reduce inflation pressure, but at the cost of weaker demand.

**MPC discussion question:** Should policymakers accept temporarily above-target inflation, or tighten policy
more aggressively despite weaker growth?
"""

    elif shock_type == "Demand" and params["shock_sign"] < 0:

        briefing = f"""
### MPC Briefing Note: Demand Contraction Scenario

The simulation suggests a negative demand shock. The output gap reaches **{summary['output_trough']:.1f}% of
potential GDP**, with the trough occurring in **Quarter {summary['output_trough_period']}**.

Inflationary pressure is weaker than in a cost-push scenario. The model therefore shows a case where falling
demand reduces inflation pressure rather than intensifying it.

This resembles a recessionary demand shortfall. The main policy issue is whether monetary policy should support
activity or remain cautious about future inflation risks.

**MPC discussion question:** Should policy focus on stabilising output, or should policymakers remain concerned
about future inflation?
"""

    elif shock_type == "Demand" and params["shock_sign"] > 0:

        briefing = f"""
### MPC Briefing Note: Demand Expansion Scenario

The simulation suggests a positive demand shock. Output rises above potential, with the output gap peaking at
**{summary['output_peak']:.1f}% of potential GDP**.

Inflation rises as demand pressure builds, reaching a peak deviation of **{summary['peak_inflation']:.1f}
percentage points above target**.

This resembles a demand-led overheating scenario. The policy challenge is to reduce inflationary pressure
without creating unnecessary output volatility.

**MPC discussion question:** How aggressively should monetary policy respond to excess demand?
"""

    elif shock_type == "Monetary policy":

        briefing = f"""
### MPC Briefing Note: Monetary Tightening Scenario

The simulation shows a direct policy-rate shock. Bank Rate rises by approximately
**{summary['peak_rate']:.1f} percentage points**, reaching its peak in **Quarter {summary['rate_peak_period']}**.

Output weakens following the tightening, with the output gap reaching **{summary['output_trough']:.1f}% of
potential GDP**. Inflation adjusts more gradually, illustrating the lagged effect of monetary policy.

This scenario demonstrates the standard New Keynesian transmission mechanism:

**Higher interest rates -> lower demand -> lower inflation pressure**

**MPC discussion question:** Are the inflation benefits of tightening worth the output costs?
"""

    elif shock_type == "Exchange rate":

        briefing = f"""
### MPC Briefing Note: Sterling Depreciation Scenario

The simulation shows sterling depreciating by approximately **{summary['peak_fx']:.1f}%**, with the peak effect
in **Quarter {summary['fx_peak_period']}**.

Inflation rises through import-price pass-through, reaching a peak deviation of **{summary['peak_inflation']:.1f}
percentage points above target**. Output effects are more ambiguous because depreciation may support net exports
while also raising import costs.

This highlights the open-economy dimension of UK inflation dynamics.

**MPC discussion question:** Should monetary policy respond strongly to imported inflation if domestic demand is weak?
"""

    else:

        briefing = f"""
### MPC Briefing Note

The selected scenario generates a peak inflation deviation of **{summary['peak_inflation']:.1f} percentage points**
and an output trough of **{summary['output_trough']:.1f}% of potential GDP**.

The policy response peaks at **{summary['peak_rate']:.1f} percentage points** above baseline.

**MPC discussion question:** Does this scenario look more like a demand shock, a supply shock, or a policy shock?
"""

    return briefing


def plot_results(y, pi, rate, q):

    fig, axs = plt.subplots(2, 2, figsize=(11, 7))

    axs[0, 0].plot(y, linewidth=2)
    axs[0, 0].set_title("Output gap")
    axs[0, 0].set_ylabel("% of potential GDP")
    axs[0, 0].set_xlabel("Quarter")

    axs[0, 1].plot(pi, linewidth=2)
    axs[0, 1].set_title("Inflation deviation from target")
    axs[0, 1].set_ylabel("Percentage points")
    axs[0, 1].set_xlabel("Quarter")

    axs[1, 0].plot(rate, linewidth=2)
    axs[1, 0].set_title("Policy interest rate")
    axs[1, 0].set_ylabel("Percentage points")
    axs[1, 0].set_xlabel("Quarter")

    axs[1, 1].plot(q, linewidth=2)
    axs[1, 1].set_title("Sterling exchange rate")
    axs[1, 1].set_ylabel("% depreciation")
    axs[1, 1].set_xlabel("Quarter")

    for ax in axs.flat:
        ax.axhline(0, linestyle="--", linewidth=0.8)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()

    return fig


def show_dashboard(summary):

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Peak inflation",
        f"{summary['peak_inflation']:.1f} pp"
    )

    col2.metric(
        "Output trough",
        f"{summary['output_trough']:.1f}%"
    )

    col3.metric(
        "Peak Bank Rate",
        f"{summary['peak_rate']:.1f} pp"
    )

    col4.metric(
        "Peak depreciation",
        f"{summary['peak_fx']:.1f}%"
    )


# =====================================================
# TABS
# =====================================================

tab1, tab2, tab3, tab4 = st.tabs(
    ["Explanation", "Simulation", "Exercises", "Validation"]
)

# =====================================================
# TAB 1: EXPLANATION
# =====================================================

with tab1:

    st.header("How the model works")

    st.markdown("""
### Model structure

The model has four main equations.

#### 1. Aggregate demand / IS curve

Output depends on:

- its own persistence;
- the real interest rate;
- the exchange rate;
- demand shocks;
- energy/import-cost shocks.

A rise in interest rates weakens demand. A sterling depreciation can support demand through net exports,
but may also raise inflation through imported costs.

#### 2. Phillips curve

Inflation depends on:

- past inflation;
- the output gap;
- import-price / exchange-rate pressure;
- energy and cost-push shocks.

This allows students to distinguish demand-led inflation from supply-led inflation.

#### 3. Monetary policy rule

The policy rate responds to:

- inflation;
- the output gap;
- interest-rate smoothing;
- monetary policy shocks.

This captures the logic of inflation-targeting monetary policy.

#### 4. Exchange-rate equation

The exchange rate responds to:

- its own persistence;
- interest-rate changes;
- exchange-rate shocks.

In this teaching model, a positive exchange-rate value represents sterling depreciation.

---

### Units

- Output gap: percentage points of potential GDP.
- Inflation: percentage-point deviation from the 2% CPI target.
- Policy rate: percentage-point change in Bank Rate relative to baseline.
- Exchange rate: per cent sterling depreciation. Positive values mean depreciation.
- Energy shock: per cent increase in energy costs or prices.

---

### Key teaching idea

The aim is to understand the mechanism:

**Shock -> transmission channel -> output/inflation response -> policy trade-off**
""")

# =====================================================
# TAB 2: SIMULATION
# =====================================================

with tab2:

    st.header("Interactive simulation")

    st.markdown("""
Select a preset scenario or build your own custom shock. The graphs show the model response over 40 quarters.
""")

    scenario = st.selectbox(
        "Choose scenario",
        [
            "COVID demand contraction",
            "2022 energy / cost-push inflation",
            "Monetary tightening",
            "Sterling depreciation",
            "Demand expansion",
            "Custom"
        ],
        key="simulation_scenario"
    )

    if scenario == "Custom":

        params = get_base_parameters()

        st.subheader("Custom scenario controls")

        col1, col2, col3 = st.columns(3)

        with col1:
            params["shock_type"] = st.selectbox(
                "Shock type",
                [
                    "Demand",
                    "Energy",
                    "Cost-push",
                    "Monetary policy",
                    "Exchange rate"
                ],
                key="custom_shock_type"
            )

        with col2:
            if params["shock_type"] == "Demand":
                params["shock_size"] = st.slider(
                    "Demand shock: output-gap effect, percentage points",
                    min_value=0.1,
                    max_value=6.0,
                    value=2.0,
                    step=0.1,
                    key="custom_demand_size"
                )

            elif params["shock_type"] == "Energy":
                params["shock_size"] = st.slider(
                    "Energy shock: energy price increase, per cent",
                    min_value=1.0,
                    max_value=80.0,
                    value=30.0,
                    step=1.0,
                    key="custom_energy_size"
                )

            elif params["shock_type"] == "Cost-push":
                params["shock_size"] = st.slider(
                    "Cost-push shock: inflation effect, percentage points",
                    min_value=0.1,
                    max_value=5.0,
                    value=1.0,
                    step=0.1,
                    key="custom_cost_size"
                )

            elif params["shock_type"] == "Monetary policy":
                params["shock_size"] = st.slider(
                    "Monetary policy shock: Bank Rate change, percentage points",
                    min_value=0.1,
                    max_value=5.0,
                    value=1.0,
                    step=0.1,
                    key="custom_policy_size"
                )

            elif params["shock_type"] == "Exchange rate":
                params["shock_size"] = st.slider(
                    "Exchange-rate shock: sterling depreciation, per cent",
                    min_value=1.0,
                    max_value=30.0,
                    value=10.0,
                    step=1.0,
                    key="custom_fx_size"
                )

        with col3:
            params["shock_persistence"] = st.slider(
                "Shock persistence",
                min_value=0.10,
                max_value=0.95,
                value=0.70,
                step=0.05,
                key="custom_persistence"
            )

        shock_direction = st.radio(
            "Shock direction",
            ["Positive", "Negative"],
            horizontal=True,
            key="custom_direction"
        )

        if shock_direction == "Positive":
            params["shock_sign"] = 1.0
        else:
            params["shock_sign"] = -1.0

        st.markdown("### Policy and structural parameters")

        p1, p2, p3 = st.columns(3)

        with p1:
            params["phi_pi"] = st.slider(
                "Policy response to inflation",
                min_value=0.5,
                max_value=3.0,
                value=1.5,
                step=0.1,
                key="custom_phi_pi"
            )

        with p2:
            params["phi_y"] = st.slider(
                "Policy response to output",
                min_value=0.0,
                max_value=1.5,
                value=0.4,
                step=0.1,
                key="custom_phi_y"
            )

        with p3:
            params["kappa"] = st.slider(
                "Phillips curve slope",
                min_value=0.05,
                max_value=0.50,
                value=0.20,
                step=0.01,
                key="custom_kappa"
            )

    else:
        params = get_scenario_parameters(scenario)

    y, pi, rate, q = simulate_model(params)
    summary = calculate_summary(y, pi, rate, q)

    st.markdown("### Current scenario")

    m1, m2, m3, m4 = st.columns(4)

    m1.metric("Shock type", params["shock_type"])
    m2.metric("Shock size", round(params["shock_size"], 2))
    m3.metric("Persistence", round(params["shock_persistence"], 2))
    m4.metric("Policy inflation response", round(params["phi_pi"], 2))

    fig = plot_results(y, pi, rate, q)
    st.pyplot(fig)

    st.markdown("### MPC dashboard")
    show_dashboard(summary)

    st.markdown("### Scenario summary table")
    st.table(make_summary_table(summary))

    st.markdown(create_mpc_briefing(scenario, params, summary))

# =====================================================
# TAB 3: EXERCISES
# =====================================================

with tab3:

    st.header("Student exercises")

    st.markdown("""
### Exercise 1: Demand shock versus energy shock

1. Run **COVID demand contraction**.
2. Run **2022 energy / cost-push inflation**.
3. Compare output and inflation.

Question: Which scenario creates the sharper policy trade-off?

---

### Exercise 2: Monetary tightening

1. Run **Monetary tightening**.
2. Observe the paths of output and inflation.
3. Then use **Custom** and increase the policy response to inflation.

Question: Does stronger policy stabilise inflation more quickly? What happens to output?

---

### Exercise 3: Sterling depreciation

1. Run **Sterling depreciation**.
2. Observe inflation and the exchange rate.
3. Discuss imported inflation.

Question: Why might exchange-rate movements complicate inflation targeting in an open economy?

---

### Exercise 4: Custom experiment

Use **Custom** mode to create a scenario with:

- a persistent supply shock;
- weak output;
- high inflation.

Question: Why is this difficult for monetary policy?

---

### Reflection question

What does this reduced model leave out?

Possible answers include:

- fiscal policy;
- financial instability;
- distributional effects;
- expectations formation;
- labour-market institutions;
- firm pricing power;
- sectoral supply chains;
- productivity dynamics.
""")

# =====================================================
# TAB 4: VALIDATION
# =====================================================

with tab4:

    st.header("Validation and historical comparison")

    st.markdown("""
This tab helps students compare the simulator with broad historical UK macroeconomic episodes.

The purpose is not exact forecasting. The purpose is to ask whether the model captures the direction,
timing, relative magnitude and policy trade-offs associated with different shocks.
""")

    validation_scenario = st.selectbox(
        "Choose scenario for validation",
        [
            "COVID demand contraction",
            "2022 energy / cost-push inflation",
            "Monetary tightening",
            "Sterling depreciation",
            "Demand expansion"
        ],
        key="validation_scenario"
    )

    validation_params = get_scenario_parameters(validation_scenario)
    vy, vpi, vrate, vq = simulate_model(validation_params)
    validation_summary = calculate_summary(vy, vpi, vrate, vq)

    st.markdown("### Model output for selected validation scenario")

    show_dashboard(validation_summary)

    st.markdown("### Peak-value summary table")

    st.table(make_summary_table(validation_summary))

    st.markdown("### Historical comparison table")

    historical_comparison = [
        {
            "Scenario": "COVID demand contraction",
            "Historical UK episode": "2020 recession and pandemic disruption",
            "Expected pattern": "Output falls sharply; inflation pressure initially weakens; policy remains accommodative.",
            "What to examine": "Output trough and inflation response."
        },
        {
            "Scenario": "2022 energy / cost-push inflation",
            "Historical UK episode": "2021-23 inflation surge and energy-price shock",
            "Expected pattern": "Inflation rises; real incomes weaken; output comes under pressure; Bank Rate rises.",
            "What to examine": "Peak inflation, output trough and policy response."
        },
        {
            "Scenario": "Monetary tightening",
            "Historical UK episode": "2022-25 tightening cycle",
            "Expected pattern": "Bank Rate rises; output weakens with a lag; inflation falls later.",
            "What to examine": "Timing of output trough and inflation moderation."
        },
        {
            "Scenario": "Sterling depreciation",
            "Historical UK episode": "Sterling depreciation episodes such as ERM exit or post-referendum depreciation",
            "Expected pattern": "Depreciation raises import-price pressure; inflation rises; demand effect is mixed.",
            "What to examine": "Exchange-rate peak and inflation pass-through."
        },
        {
            "Scenario": "Demand expansion",
            "Historical UK episode": "Demand-led overheating episode",
            "Expected pattern": "Output rises above potential; inflation pressure builds; policy tightens.",
            "What to examine": "Output peak, inflation peak and policy response."
        }
    ]

    st.table(historical_comparison)

    st.markdown("### MPC briefing for validation scenario")

    st.markdown(create_mpc_briefing(validation_scenario, validation_params, validation_summary))

    st.markdown("### Validation questions for students")

    st.markdown("""
1. Does the model move output, inflation, interest rates and the exchange rate in the expected direction?
2. Are the peak values plausible for the historical episode?
3. Does the timing of the response look realistic?
4. Does monetary policy respond too strongly, too weakly, or about right?
5. What does the model leave out?
6. Would a Post-Keynesian, structuralist or political economy interpretation challenge the model's explanation?
""")
