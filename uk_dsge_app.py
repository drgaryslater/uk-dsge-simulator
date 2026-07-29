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

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("Teaching Guide")

st.sidebar.info("""
Recommended sequence:

1. COVID Demand Shock
2. Energy Crisis
3. Monetary Tightening
4. Sterling Depreciation

For each simulation:

Predict → Simulate → Explain
""")

# =====================================================
# TABS
# =====================================================

tab1, tab2, tab3 = st.tabs(
    ["📘 Explanation", "📊 Simulation", "🧠 Exercises"]
)

# =====================================================
# EXPLANATION
# =====================================================

with tab1:

    st.header("How the model works")

    st.markdown("""

This is a simplified DSGE-style model.

### Output

Output depends upon:

- interest rates
- exchange rates
- shocks

### Inflation

Inflation depends upon:

- previous inflation
- output pressures
- supply-side shocks

### Monetary Policy

The Bank of England reacts to:

- inflation
- output

through interest rate changes.

### Learning Goal

The objective is not forecasting.

The objective is understanding:

**Shock → Transmission Mechanism → Economic Outcome**
""")

# =====================================================
# SIMULATION
# =====================================================

with tab2:

    st.header("Interactive Simulation")

    scenario = st.selectbox(
        "Choose scenario",
        [
            "2022 Energy Crisis",
            "COVID Demand Shock",
            "Aggressive Monetary Tightening",
            "Sterling Depreciation",
            "Custom"
        ]
    )

    if scenario == "2022 Energy Crisis":
        shock_type = "Cost-Push"
        shock_size = 1.5
        persistence = 0.9

    elif scenario == "COVID Demand Shock":
        shock_type = "Demand"
        shock_size = 2.0
        persistence = 0.7

    elif scenario == "Aggressive Monetary Tightening":
        shock_type = "Monetary"
        shock_size = 1.0
        persistence = 0.7

    elif scenario == "Sterling Depreciation":
        shock_type = "Exchange Rate"
        shock_size = 1.2
        persistence = 0.8

    else:

        shock_type = st.selectbox(
            "Shock Type",
            ["Demand","Cost-Push","Monetary","Exchange Rate"]
        )

        shock_size = st.slider(
            "Shock Size",
            0.1,
            3.0,
            1.0
        )

        persistence = st.slider(
            "Shock Persistence",
            0.1,
            0.95,
            0.7
        )

    T = 40
    
y = np.zeros(T)
pi = np.zeros(T)
r = np.zeros(T)
q = np.zeros(T)
shock = np.zeros(T)
 
shock[1] = shock_size
 
for t in range(2, T):
 
shock[t] = persistence * shock[t-1]

        if shock_type == "Demand":
            y[t] = 0.8*y[t-1] + shock[t]

        elif shock_type == "Cost-Push":
            pi[t] = 0.8*pi[t-1] + shock[t]

        elif shock_type == "Monetary":
            r[t] = 0.8*r[t-1] + shock[t]
            y[t] = y[t] - 0.3*r[t]

        elif shock_type == "Exchange Rate":
            q[t] = 0.8*q[t-1] + shock[t]
            pi[t] = pi[t] + 0.2*q[t]

        pi[t] += 0.2*y[t]

    fig, axs = plt.subplots(2,2, figsize=(10,6))

    axs[0,0].plot(y)
    axs[0,0].set_title("Output")

    axs[0,1].plot(pi)
    axs[0,1].set_title("Inflation")

    axs[1,0].plot(r)
    axs[1,0].set_title("Interest Rate")

    axs[1,1].plot(q)
    axs[1,1].set_title("Exchange Rate")

    plt.tight_layout()

    st.pyplot(fig)

# =====================================================
# EXERCISES
# =====================================================

with tab3:

    st.header("Student Exercises")

    st.markdown("""

## Exercise 1

Compare:

- COVID Demand Shock
- Energy Crisis

Question:

Which generates stagflation?

---

## Exercise 2

Compare:

- Monetary Tightening
- Demand Shock

Question:

How quickly can inflation be stabilised?

---

## Exercise 3

Run:

- Sterling Depreciation

Question:

Why might imported inflation occur?

---

## Exercise 4

Use:

- Custom

Question:

Can you create a scenario which resembles the UK economy in 2022?
""")
