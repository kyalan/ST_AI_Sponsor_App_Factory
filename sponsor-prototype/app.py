import streamlit as st
import pandas as pd
import numpy as np

# --- Page Configuration ---
st.set_page_config(
    page_title="HKJC Sponsorship Prospecting Tool",
    page_icon="🐎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Mock Backend Data Generation ---
@st.cache_data
def load_mock_data():
    # Mock Companies Database
    df_companies = pd.read_csv("data_source/companies_data.csv")
    
    # Mock Key Staff/Contacts Database
    df_staff = pd.read_csv("data_source/staff_data.csv")
    
    return df_companies, df_staff

df_companies, df_staff = load_mock_data()

# --- Sidebar Filters ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/5/52/Hong_Kong_Jockey_Club_logo.svg/1200px-Hong_Kong_Jockey_Club_logo.svg.png", width=150)
st.sidebar.title("Sponsorship Filters")
st.sidebar.markdown("Filter potential sponsors for upcoming sports events.")

search_query = st.sidebar.text_input("Search Company Name")
selected_industry = st.sidebar.multiselect("Industry", options=df_companies["Industry"].unique(), default=df_companies["Industry"].unique())
min_score = st.sidebar.slider("Minimum Propensity Score", min_value=0, max_value=100, value=75)

# Apply Filters
filtered_df = df_companies[
    (df_companies["Industry"].isin(selected_industry)) & 
    (df_companies["Propensity Score"] >= min_score)
]
if search_query:
    filtered_df = filtered_df[filtered_df["Company Name"].str.contains(search_query, case=False)]

# Sort by Propensity Score descending
filtered_df = filtered_df.sort_values(by="Propensity Score", ascending=False).reset_index(drop=True)


# --- Main Dashboard ---
st.title("🐎 HKJC Sports Event Sponsorship Prospecting")
st.markdown("**Executive Director Dashboard** - Prioritize and analyze potential corporate sponsors based on propensity modeling and strategic fit.")

# Top Level Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Prospects Found", len(filtered_df))
col2.metric("High Propensity (>85)", len(filtered_df[filtered_df["Propensity Score"] >= 85]))
col3.metric("Total Est. Marketing Pool", "HK$ 3.05B")

st.divider()

# --- Split View: List on Left, Details on Right ---
if not filtered_df.empty:
    list_col, detail_col = st.columns([1, 2])
    
    with list_col:
        st.subheader("Target Companies")
        st.markdown("Select a company to view details.")
        
        # Create a selection mechanism using session state
        if 'selected_company_id' not in st.session_state:
            st.session_state.selected_company_id = filtered_df.iloc[0]["Company ID"]
            
        for index, row in filtered_df.iterrows():
            # Highlight selected
            is_selected = st.session_state.selected_company_id == row["Company ID"]
            button_type = "primary" if is_selected else "secondary"
            
            if st.button(f"{row['Company Name']} (Score: {row['Propensity Score']})", key=row["Company ID"], use_container_width=True, type=button_type):
                st.session_state.selected_company_id = row["Company ID"]
                st.rerun()

    with detail_col:
        # Get selected company details
        selected_company = df_companies[df_companies["Company ID"] == st.session_state.selected_company_id].iloc[0]
        
        st.subheader(f"🏢 {selected_company['Company Name']}")
        
        # Propensity Score Progress Bar
        st.markdown(f"**Propensity to Sponsor:** {selected_company['Propensity Score']}/100")
        st.progress(int(selected_company['Propensity Score']))
        
        # Tabs for detailed information
        tab1, tab2, tab3 = st.tabs(["Overview & Digital", "Financial Measures", "Key Personnel"])
        
        with tab1:
            st.markdown("#### Company Demographics")
            st.write(f"**Industry:** {selected_company['Industry']}")
            st.write(f"**Address:** {selected_company['Address']}")
            st.write(f"**Website:** [{selected_company['URL']}](http://{selected_company['URL']})")
            st.write(f"**LinkedIn:** [{selected_company['LinkedIn']}](https://{selected_company['LinkedIn']})")
            
            st.markdown("#### Social Media Measures")
            sm_col1, sm_col2 = st.columns(2)
            sm_col1.metric("Total Followers", selected_company['Social Media Followers'])
            sm_col2.metric("Avg. Engagement Rate", selected_company['Engagement Rate'])
            
        with tab2:
            st.markdown("#### Financial Measures")
            fin_col1, fin_col2 = st.columns(2)
            fin_col1.metric("Annual Revenue (HKD)", selected_company['Annual Revenue (HKD)'])
            fin_col2.metric("Est. Marketing Budget", selected_company['Marketing Budget Est.'])
            
            st.info("💡 **Insight:** Companies with marketing budgets over $500M and high engagement rates are prime targets for Title Sponsorships.")
            
        with tab3:
            st.markdown("#### Suggested Key Persons")
            st.markdown("Leverage existing HKJC networks (Members, Box Owners, Horse Owners) to secure meetings.")
            
            company_staff = df_staff[df_staff["Company ID"] == selected_company["Company ID"]]
            
            if not company_staff.empty:
                st.dataframe(
                    company_staff[["Contact Name", "Role", "Connection Strength", "Previous HKJC Interaction"]],
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.warning("No key personnel data available for this company.")

else:
    st.warning("No companies match the current filter criteria.")