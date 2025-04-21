
import streamlit as st
import pandas as pd
from scipy.optimize import linprog
import numpy as np

st.title("Cara Orange Growers: Transportation Optimization")

st.markdown("### Transportation Cost Table")
cost_data = {
    "Atlanta, GA": [500, 400, 900],
    "Chicago, IL": [700, 600, 850],
    "Dallas, TX": [800, 300, 650],
    "Los Angeles, CA": [1200, 1000, 400]
}
supply = [150, 170, 200]
demand = [140, 130, 120, 130]
regions = ["Indian River, FL", "Rio Grande Valley, TX", "Central Valley, CA"]
rdcs = ["Atlanta, GA", "Chicago, IL", "Dallas, TX", "Los Angeles, CA"]

cost_df = pd.DataFrame(cost_data, index=regions)
cost_df["Supply"] = supply
cost_df.loc["Demand"] = demand + [None]
st.dataframe(cost_df)

st.markdown("### Optimization Result")

# Flatten cost matrix
c = [cost_data[rdc][i] for i in range(3) for rdc in rdcs]

# Supply constraints (<=)
A_ub = []
b_ub = supply
for i in range(3):
    row = [0] * 12
    for j in range(4):
        row[i * 4 + j] = 1
    A_ub.append(row)

# Demand constraints (==)
A_eq = []
b_eq = demand
for j in range(4):
    row = [0] * 12
    for i in range(3):
        row[i * 4 + j] = 1
    A_eq.append(row)

bounds = [(0, None)] * 12

res = linprog(c=c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

if res.success:
    st.success("Optimal solution found!")
    shipments = pd.DataFrame(
        [res.x[i * 4:(i + 1) * 4] for i in range(3)],
        index=regions,
        columns=rdcs
    )
    st.dataframe(shipments)
    st.markdown(f"### Total Cost: ${res.fun:,.2f}")
    
    st.markdown("### Sensitivity Analysis Insights")
    st.write("""
    The dual values (shadow prices) from the optimization provide the following insights:

    - **Shadow Price on Supply Constraints**: Indicates how much the total cost would decrease if we could supply 1 more ton from that region.
    - **Shadow Price on Demand Constraints**: Indicates how much total cost would increase if we had to supply 1 more ton to that RDC.

    These can guide decisions like expanding capacity or adjusting supply routes.
    """)

    shadow_prices_supply = res.ineqlin.get("marginals")[:3]  # Supply shadow prices
    shadow_prices_demand = res.eqlin.get("marginals")        # Demand shadow prices

    if shadow_prices_demand is not None:
        shadow_df = pd.DataFrame({
            "Supply Constraint Shadow Price": shadow_prices_supply,
        }, index=regions)
        shadow_df_demand = pd.DataFrame({
            "Demand Constraint Shadow Price": shadow_prices_demand,
        }, index=rdcs)
        st.markdown("#### Shadow Prices - Supply")
        st.dataframe(shadow_df)
        st.markdown("#### Shadow Prices - Demand")
        st.dataframe(shadow_df_demand)
else:
    st.error("Optimization failed.")
