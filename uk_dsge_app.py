import streamlit as st

st.set_page_config(page_title="UK DSGE Simulator")

st.title("UK DSGE Simulator")

st.sidebar.subheader("Recommended Teaching Scenarios")

st.sidebar.markdown("""
1. COVID Demand Shock
2. 2022 Energy Crisis
3. Aggressive Monetary Tightening
4. Sterling Depreciation
""")

tab1, tab2, tab3 = st.tabs(
    ["Explanation", "Simulation", "Exercises"]
)

with tab1:

    st.header("Explanation")

    st.write("""
This app demonstrates a simplified Bank of England style
DSGE model for teaching purposes.

Use the Simulation tab to explore scenarios.
""")

with tab2:

    st.header("Simulation")

    scenario = st.selectbox(
        "Scenario",
        [
            "COVID Demand Shock",
            "2022 Energy Crisis",
            "Aggressive Monetary Tightening",
            "Sterling Depreciation"
        ]
    )

    st.write(f"Selected scenario: {scenario}")

with tab3:

    st.header("Exercises")

    st.markdown("""
### Exercise

1. Select a scenario.
2. Predict outcomes.
3. Compare with results.
4. Explain your reasoning.
""")
