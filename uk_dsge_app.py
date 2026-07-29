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
This app uses a reduced-form New Keynesian open-economy model for teaching.
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
# TABS
# =====================================================

ttab1, tab2, tab3, tab4 = st.tabs(
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

A rise in interest rates weakens demand.  
A sterling depreciation can support demand through net exports but may also raise inflation.

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

In this teaching model, a positive exchange-rate value represents depreciation.
Depreciation raises import-price pressure but may improve net export demand.

---

### Key teaching idea

The aim is to understand the mechanism:

Shock -> transmission channel -> output/inflation response -> policy trade-off
""")

# =====================================================
# TAB 2: SIMULATION
# =====================================================

with tab2:

    st.header("Interactive simulation")

    st.markdown("""
Select a preset scenario or build your own custom shock. The graphs show the model response over 40 periods.
""")

    # -------------------------------------------------
    # SCENARIO CHOICE
    # -------------------------------------------------

    scenario = st.selectbox(
        "Choose scenario",
        [
            "COVID demand contraction",
            "2022 energy / cost-push inflation",
            "Monetary tightening",
            "Sterling depreciation",
            "Demand expansion",
            "Custom"
        ]
    )

    # -------------------------------------------------
    # CALIBRATED TEACHING UNITS
    # -------------------------------------------------
    # Units:
    # y      = output gap, percentage points of potential GDP
    # pi     = CPI inflation deviation from 2% target, percentage points
    # rate   = Bank Rate deviation from baseline, percentage points
    # q      = sterling depreciation, per cent. Positive = depreciation
    # energy = energy price / cost shock, per cent

    rho_y = 0.60       # output-gap persistence
    rho_pi = 0.65      # inflation persistence
    rho_i = 0.80       # interest-rate smoothing
    rho_q = 0.60       # exchange-rate persistence

    # Transmission parameters in interpretable units
    alpha_r = 0.30     # effect of 1 pp real rate rise on output gap
    alpha_q = 0.03     # effect of 1% sterling depreciation on output gap
    alpha_energy_y = 0.015  # output drag from 1% energy price increase

    kappa = 0.20       # Phillips curve: effect of 1 pp output gap on inflation
    gamma_q = 0.025    # import-price pass-through: 1% depreciation -> inflation pp
    gamma_energy_pi = 0.035  # 1% energy shock -> inflation pp

    phi_pi = 1.50      # Taylor-rule response to inflation
    phi_y = 0.40       # Taylor-rule response to output gap
    eta_i = 0.80       # interest-rate effect on exchange rate

    shock_persistence = 0.70
    shock_size = 1.0
    shock_type = "Demand"
    shock_sign = 1.0

    # -------------------------------------------------
    # PRESET SCENARIOS WITH REAL ECONOMIC MAGNITUDES
    # -------------------------------------------------

    if scenario == "COVID demand contraction":
        # A large temporary negative demand shock.
        # Unit: percentage points of output gap.
        shock_type = "Demand"
        shock_size = 4.0
        shock_sign = -1.0
        shock_persistence = 0.55
        phi_pi = 1.50
        phi_y = 0.50

    elif scenario == "2022 energy / cost-push inflation":
        # A large and persistent energy-price shock.
        # Unit: per cent energy price/cost increase.
        shock_type = "Energy"
        shock_size = 40.0
        shock_sign = 1.0
        shock_persistence = 0.80
        phi_pi = 1.70
        phi_y = 0.35

    elif scenario == "Monetary tightening":
        # A direct increase in Bank Rate.
        # Unit: percentage points.
        shock_type = "Monetary policy"
        shock_size = 1.0
        shock_sign = 1.0
        shock_persistence = 0.65
        phi_pi = 2.20
        phi_y = 0.40

    elif scenario == "Sterling depreciation":
        # A sterling depreciation.
        # Unit: per cent depreciation.
        shock_type = "Exchange rate"
        shock_size = 12.0
        shock_sign = 1.0
        shock_persistence = 0.70
        phi_pi = 1.60
        phi_y = 0.40

    elif scenario == "Demand expansion":
        # A positive demand shock.
        # Unit: percentage points of output gap.
        shock_type = "Demand"
        shock_size = 2.0
        shock_sign = 1.0
        shock_persistence = 0.60
        phi_pi = 1.50
        phi_y = 0.50

    # -------------------------------------------------
    # CUSTOM CONTROLS
    # -------------------------------------------------

    if scenario == "Custom":

        st.subheader("Custom scenario controls")

        col1, col2, col3 = st.columns(3)

        with col1:
            shock_type = st.selectbox(
                "Shock type",
                [
                    "Demand",
                    "Energy",
                    "Cost-push",
                    "Monetary policy",
                    "Exchange rate"
                ]
            )

        with col2:
            if shock_type == "Demand":
                shock_size = st.slider(
                    "Demand shock: output-gap effect, percentage points",
                    min_value=0.1,
                    max_value=6.0,
                    value=2.0,
                    step=0.1
                )

            elif shock_type == "Energy":
                shock_size = st.slider(
                    "Energy shock: energy price increase, per cent",
                    min_value=1.0,
                    max_value=80.0,
                    value=30.0,
                    step=1.0
                )

            elif shock_type == "Cost-push":
                shock_size = st.slider(
                    "Cost-push shock: inflation effect, percentage points",
                    min_value=0.1,
                    max_value=5.0,
                    value=1.0,
                    step=0.1
                )

            elif shock_type == "Monetary policy":
                shock_size = st.slider(
                    "Monetary policy shock: Bank Rate change, percentage points",
                    min_value=0.1,
                    max_value=5.0,
                    value=1.0,
                    step=0.1
                )

            elif shock_type == "Exchange rate":
                shock_size = st.slider(
                    "Exchange-rate shock: sterling depreciation, per cent",
                    min_value=1.0,
                    max_value=30.0,
                    value=10.0,
                    step=1.0
                )

        with col3:
            shock_persistence = st.slider(
                "Shock persistence",
                min_value=0.10,
                max_value=0.95,
                value=0.70,
                step=0.05
            )

        shock_direction = st.radio(
            "Shock direction",
            ["Positive", "Negative"],
            horizontal=True
        )

        if shock_direction == "Positive":
            shock_sign = 1.0
        else:
            shock_sign = -1.0

        st.markdown("### Policy and structural parameters")

        p1, p2, p3 = st.columns(3)

        with p1:
            phi_pi = st.slider(
                "Policy response to inflation",
                min_value=0.5,
                max_value=3.0,
                value=1.5,
                step=0.1
            )

        with p2:
            phi_y = st.slider(
                "Policy response to output",
                min_value=0.0,
                max_value=1.5,
                value=0.4,
                step=0.1
            )

        with p3:
            kappa = st.slider(
                "Phillips curve slope",
                min_value=0.05,
                max_value=0.50,
                value=0.20,
                step=0.01
            )

    # -------------------------------------------------
    # MODEL SIMULATION
    # -------------------------------------------------

    T = 40

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
    generic_shock[1] = shock_sign * shock_size

    for t in range(2, T):
        generic_shock[t] = shock_persistence * generic_shock[t - 1]

    if shock_type == "Demand":
        demand_shock = generic_shock.copy()

    elif shock_type == "Energy":
        energy_shock = generic_shock.copy()

    elif shock_type == "Cost-push":
        cost_push_shock = generic_shock.copy()

    elif shock_type == "Monetary policy":
        monetary_shock = generic_shock.copy()

    elif shock_type == "Exchange rate":
        exchange_rate_shock = generic_shock.copy()

    for t in range(1, T):

        # Monetary policy rule
        # rate is in percentage points.
        rate[t] = (
            rho_i * rate[t - 1]
            + (1 - rho_i) * (phi_pi * pi[t - 1] + phi_y * y[t - 1])
            + monetary_shock[t]
        )

        # Exchange-rate equation
        # q is per cent sterling depreciation. Positive q = depreciation.
        q[t] = (
            rho_q * q[t - 1]
            - eta_i * (rate[t] - rate[t - 1])
            + exchange_rate_shock[t]
        )

        # Aggregate demand / IS equation
        # y is output gap in percentage points of potential GDP.
        y[t] = (
            rho_y * y[t - 1]
            - alpha_r * (rate[t - 1] - pi[t - 1])
            + alpha_q * q[t - 1]
            + demand_shock[t]
            - alpha_energy_y * energy_shock[t]
        )

        # Phillips curve
        # pi is inflation deviation from the 2% target, in percentage points.
        pi[t] = (
            rho_pi * pi[t - 1]
            + kappa * y[t]
            + gamma_q * q[t]
            + gamma_energy_pi * energy_shock[t]
            + cost_push_shock[t]
        )

    # -------------------------------------------------
    # SUMMARY METRICS
    # -------------------------------------------------

    st.markdown("### Current scenario")

    m1, m2, m3, m4 = st.columns(4)

    m1.metric("Shock type", shock_type)
    m2.metric("Shock size", round(shock_size, 2))
    m3.metric("Persistence", round(shock_persistence, 2))
    m4.metric("Policy inflation response", round(phi_pi, 2))

    # -------------------------------------------------
    # PLOTS
    # -------------------------------------------------

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
    st.pyplot(fig)

    # -------------------------------------------------
    # INTERPRETATION
    # -------------------------------------------------

    st.markdown("### Interpretation")

    if shock_type == "Demand":
        st.info("""
A demand shock moves output first. Inflation then responds through the Phillips curve.
A negative demand shock resembles a contraction in spending. A positive demand shock resembles excess demand.
""")

    elif shock_type == "Energy":
        st.info("""
An energy shock directly raises inflation and also weakens output. This creates a policy trade-off:
raising interest rates can reduce inflation pressure, but may worsen the output gap.
""")

    elif shock_type == "Cost-push":
        st.info("""
A cost-push shock raises inflation independently of demand. This illustrates why inflation can rise
even when output is weak.
""")

    elif shock_type == "Monetary policy":
        st.info("""
A monetary policy shock raises the interest rate directly. Output falls through the demand channel,
and inflation adjusts with a lag.
""")

    elif shock_type == "Exchange rate":
        st.info("""
A sterling depreciation raises import-price pressure and can also support demand through net exports.
This highlights the open-economy inflation channel.
""")

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
