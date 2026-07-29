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
    
