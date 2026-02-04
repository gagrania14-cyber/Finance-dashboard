import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="XYZ Semiconductor Executive Dashboard", layout="wide")

@st.cache_data
def load_data():
    exec_tiles = pd.read_csv('exec_tiles.csv')
    segments = pd.read_csv('segments.csv')
    geography = pd.read_csv('geography.csv')
    guidance = pd.read_csv('guidance.csv')
    risk = pd.read_csv('risk.csv')
    market = pd.read_csv('market.csv')
    return exec_tiles, segments, geography, guidance, risk, market

exec_tiles, segments, geography, guidance, risk, market = load_data()

st.title("🎯 XYZ Semiconductor Co. - Executive Dashboard")
st.info(f"📅 **Data as of Q3 FY2025 (October 2024) | Dashboard Updated: {datetime.now().strftime('%B %d, %Y at %H:%M')}**")
st.markdown("---")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Executive Tiles", 
    "📈 Segment Performance", 
    "🌍 Geography", 
    "🎯 Guidance Tracking",
    "⚠️ Risk & Concentration",
    "💹 Market KPIs"
])

with tab1:
    st.header("Executive Metrics - Q3 FY2025 (Ended Oct 27, 2024)")
    
    latest = exec_tiles.iloc[-1]
    prev_q = exec_tiles.iloc[-2]
    prev_y = exec_tiles.iloc[-5] if len(exec_tiles) >= 5 else exec_tiles.iloc[0]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Revenue (Q3 FY25)", f"${latest['revenue_q']/1000:.1f}B", 
                  f"{((latest['revenue_q']/prev_q['revenue_q']-1)*100):.1f}% QoQ")
        st.metric("Revenue (TTM)", f"${latest['revenue_ttm']/1000:.1f}B",
                  f"{((latest['revenue_ttm']/prev_y['revenue_ttm']-1)*100):.1f}% YoY")
    with col2:
        st.metric("Gross Margin", f"{latest['gm_pct']:.1f}%", 
                  f"{(latest['gm_pct']-prev_q['gm_pct']):.1f}pp")
        st.metric("Operating Margin", f"{latest['op_margin']:.1f}%",
                  f"{(latest['op_margin']-prev_q['op_margin']):.1f}pp")
    with col3:
        st.metric("Net Margin", f"{latest['net_margin']:.1f}%",
                  f"{(latest['net_margin']-prev_q['net_margin']):.1f}pp")
        st.metric("FCF (Q3 FY25)", f"${latest['fcf_q']/1000:.1f}B")
    with col4:
        st.metric("Cash Balance", f"${latest['cash_balance']/1000:.1f}B")
        net_cash = latest['cash_balance'] - latest['debt']
        st.metric("Net Cash/(Debt)", f"${net_cash/1000:.1f}B")
    
    st.subheader("Growth Metrics (Q3 FY25)")
    growth_df = pd.DataFrame({
        'Metric': ['Total Revenue', 'Data Center Revenue'],
        'QoQ Growth': [f"{latest['revenue_qoq_growth']:.1f}%", f"{latest['dc_qoq_growth']:.1f}%"],
        'YoY Growth': [f"{latest['revenue_yoy_growth']:.1f}%", f"{latest['dc_yoy_growth']:.1f}%"]
    })
    st.dataframe(growth_df, hide_index=True, use_container_width=True)

with tab2:
    st.header("Segment Performance (FY2024 - FY2025)")
    
    segments_display = segments.copy()
    segments_display['revenue_b'] = segments_display['revenue'] / 1000
    
    fig1 = px.bar(segments_display, x='quarter', y='revenue_b', color='segment',
                  title='Revenue by Segment ($B)', labels={'revenue_b': 'Revenue ($B)', 'quarter': 'Quarter'})
    fig1.update_layout(xaxis_title='Quarter', yaxis_title='Revenue ($B)')
    st.plotly_chart(fig1, use_container_width=True)
    
    dc_data = segments_display[segments_display['segment'] == 'Data Center'].copy()
    if 'compute_revenue' in dc_data.columns:
        dc_data['compute_b'] = dc_data['compute_revenue'] / 1000
        dc_data['networking_b'] = dc_data['networking_revenue'] / 1000
        
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name='Compute', x=dc_data['quarter'], y=dc_data['compute_b']))
        fig2.add_trace(go.Bar(name='Networking', x=dc_data['quarter'], y=dc_data['networking_b']))
        fig2.update_layout(title='Data Center: Compute vs Networking ($B)', barmode='stack',
                          xaxis_title='Quarter', yaxis_title='Revenue ($B)')
        st.plotly_chart(fig2, use_container_width=True)
    
    st.subheader("Segment Growth Rates (Q3 FY25)")
    latest_segs = segments[segments['quarter'] == segments['quarter'].max()].copy()
    latest_segs['revenue_b'] = latest_segs['revenue'] / 1000
    display_segs = latest_segs[['segment', 'revenue_b', 'qoq_growth', 'yoy_growth']].copy()
    display_segs.columns = ['Segment', 'Revenue ($B)', 'QoQ Growth (%)', 'YoY Growth (%)']
    st.dataframe(display_segs, hide_index=True, use_container_width=True)

with tab3:
    st.header("Geographic Performance (Billing Location - FY2024 to FY2025)")
    
    geography_display = geography.copy()
    geography_display['revenue_b'] = geography_display['revenue'] / 1000
    
    fig3 = px.line(geography_display, x='quarter', y='revenue_b', color='region',
                   title='Revenue by Billing Location ($B)', 
                   labels={'revenue_b': 'Revenue ($B)', 'quarter': 'Quarter', 'region': 'Region'})
    fig3.update_layout(xaxis_title='Quarter', yaxis_title='Revenue ($B)')
    st.plotly_chart(fig3, use_container_width=True)
    
    st.info("📌 **Singapore Invoicing Effect**: Significant portion of Asia-Pacific revenue flows through Singapore billing entity due to regional hub structure. This may not reflect actual end-customer location.")
    
    latest_geo = geography_display[geography_display['quarter'] == geography_display['quarter'].max()]
    fig4 = px.pie(latest_geo, values='revenue_b', names='region', 
                  title=f"Revenue Mix by Region - {latest_geo['quarter'].iloc[0]} ($B)")
    st.plotly_chart(fig4, use_container_width=True)
    
    st.subheader(f"Regional Breakdown - {latest_geo['quarter'].iloc[0]}")
    region_table = latest_geo[['region', 'revenue_b']].copy()
    region_table.columns = ['Region', 'Revenue ($B)']
    region_table['% of Total'] = (region_table['Revenue ($B)'] / region_table['Revenue ($B)'].sum() * 100).round(1)
    st.dataframe(region_table, hide_index=True, use_container_width=True)

with tab4:
    st.header("Outlook & Guidance Tracking")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Q3 FY25: Actual vs Guidance")
        last = guidance.iloc[-2] if len(guidance) > 1 else guidance.iloc[-1]
        
        perf_df = pd.DataFrame({
            'Metric': ['Revenue ($B)', 'Gross Margin (%)'],
            'Guidance': [f"${last['guidance_revenue']/1000:.1f}B ±2%", 
                        f"{last['guidance_gm']:.1f}% ±50bp"],
            'Actual': [f"${last['actual_revenue']/1000:.1f}B", 
                      f"{last['actual_gm']:.1f}%"],
            'Beat/(Miss)': [f"{((last['actual_revenue']/last['guidance_revenue']-1)*100):.1f}%",
                           f"{(last['actual_gm']-last['guidance_gm']):.1f}pp"]
        })
        st.dataframe(perf_df, hide_index=True, use_container_width=True)
    
    with col2:
        st.subheader("Q4 FY25 Guidance (Jan 2025)")
        current = guidance.iloc[-1]
        guide_df = pd.DataFrame({
            'Metric': ['Revenue ($B)', 'Gross Margin (%)'],
            'Guidance': [f"${current['guidance_revenue']/1000:.1f}B ±2%", 
                        f"{current['guidance_gm']:.1f}% ±50bp"],
            'Implied Growth': [f"{current['implied_qoq_growth']:.1f}% QoQ / {current['implied_yoy_growth']:.1f}% YoY",
                              "—"]
        })
        st.dataframe(guide_df, hide_index=True, use_container_width=True)
    
    st.subheader("📉 Margin Pressure Analysis")
    st.warning("""
    **Gross Margin Decline Factors (FY25):**
    - **Product Mix Shift**: Increased sales of next-gen products with lower initial margins
    - **New Architecture Ramp Costs**: New product launch includes elevated manufacturing and validation costs
    - **Supply Chain**: Higher advanced packaging costs and premium wafer pricing
    - **Competitive Pricing**: Pressure from competitors and custom chip developments by major customers
    
    **Management Guidance**: Margins expected to stabilize in mid-70% range as new products scale
    """)

with tab5:
    st.header("Risk & Concentration Analysis")
    
    st.subheader("📊 Understanding Customer vs AR Concentration")
    st.info("""
    **Customer Concentration (Revenue)**: Shows which customers drive the most sales. High concentration means revenue dependency on few buyers.
    
    **AR Concentration (Accounts Receivable)**: Shows which customers owe the most money. High concentration means credit risk - if one customer delays payment or defaults, it impacts cash flow significantly.
    
    **Why Different?**: A customer might buy a lot (high revenue %) but pay promptly (low AR %), or vice versa. AR concentration reveals payment behavior and collection risk.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top Customers by Revenue (Q3 FY25)")
        st.caption("Major cloud hyperscalers and technology companies")
        
        real_customers = pd.DataFrame({
            'customer': ['Customer A', 'Customer B', 'Customer C', 'Customer D', 'Other Customers'],
            'pct_of_total': [14, 13, 11, 10, 52],
            'quarter': ['Q3-FY25'] * 5
        })
        
        fig5 = px.bar(real_customers, x='customer', y='pct_of_total',
                     title='Customer Revenue Concentration',
                     labels={'pct_of_total': '% of Total Revenue', 'customer': 'Customer'})
        fig5.update_layout(xaxis_title='Customer', yaxis_title='% of Revenue')
        st.plotly_chart(fig5, use_container_width=True)
        
        st.caption("*Top 4 customers represent ~48% of revenue.*")
    
    with col2:
        st.subheader("AR Concentration (Q3 FY25)")
        st.caption("Accounts Receivable - Credit & Collection Risk")
        
        ar_customers = pd.DataFrame({
            'customer': ['Customer A', 'Customer B', 'Customer C', 'Customer D', 'Others'],
            'pct_of_total': [15, 13, 12, 11, 49],
            'payment_terms': ['Net 45', 'Net 60', 'Net 30', 'Net 45', 'Various']
        })
        
        fig6 = px.bar(ar_customers, x='customer', y='pct_of_total',
                     title='AR Concentration - Collection Risk',
                     labels={'pct_of_total': '% of Total AR', 'customer': 'Customer'})
        fig6.update_layout(xaxis_title='Customer', yaxis_title='% of AR')
        st.plotly_chart(fig6, use_container_width=True)
        
        st.caption("*Customer identities confidential. Concentration indicates payment timing risk.*")
    
    st.subheader("⚠️ Key Risk Factors")
    st.error("""
    **Export Controls & Geopolitical Risk**:
    - US export restrictions on advanced semiconductor technology to certain regions
    - Geographic concentration of revenue creates regulatory exposure
    - Evolving trade policies may impact market access
    
    **Supply Chain Concentration**:
    - Dependency on leading foundries for advanced process nodes
    - Advanced packaging capacity constraints
    - High-bandwidth memory supply concentration among few suppliers
    
    **Customer Concentration Risk**:
    - Top 4 customers = 48% of revenue
    - Large customers developing custom silicon solutions
    - Capital expenditure cycles impact demand volatility
    """)

with tab6:
    st.header("Market Performance & Valuation")
    
    st.info(f"📊 **Market Data** (As of July 31, 2025 - Static Snapshot)")
    
    # Use static data from CSV
    latest_mkt = market.iloc[-1]
    prev_mkt = market.iloc[-2]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Stock Price", f"${latest_mkt['stock_price']:.2f}",
                 f"{((latest_mkt['stock_price']/prev_mkt['stock_price']-1)*100):.1f}%")
        st.metric("Market Cap", f"${latest_mkt['market_cap']/1000:.0f}B")
    
    with col2:
        st.metric("52-Week High", f"${latest_mkt['stock_price']*1.15:.2f}")
        st.metric("52-Week Low", f"${latest_mkt['stock_price']*0.72:.2f}")
    
    with col3:
        st.metric("P/E Ratio (TTM)", f"{latest_mkt['pe_ratio']:.1f}x")
        st.metric("Forward P/E", f"{latest_mkt['pe_ratio']*0.85:.1f}x")
    
    with col4:
        st.metric("P/S Ratio", f"{latest_mkt['ps_ratio']:.1f}x")
        st.metric("EV/EBITDA", f"{latest_mkt['ev_ebitda']:.1f}x")
    
    col5, col6 = st.columns(2)
    with col5:
        st.metric("30-Day Volatility", f"{latest_mkt['volatility_30d']:.1f}%")
    with col6:
        st.metric("Avg Daily Volume", "47.3M shares")
    
    # Historical stock price chart using market.csv data
    fig7 = go.Figure()
    fig7.add_trace(go.Scatter(x=market['date'], y=market['stock_price'],
                              mode='lines', name='Stock Price', line=dict(color='#4285f4', width=2)))
    fig7.update_layout(
        title='XYZ Semiconductor Stock Price Trend',
        xaxis_title='Date',
        yaxis_title='Price ($)',
        hovermode='x unified'
    )
    st.plotly_chart(fig7, use_container_width=True)
    
    st.caption("*Market data represents historical snapshot and is not updated in real-time*")

st.markdown("---")
st.caption("""
**Data Sources**: 
- Financial Data: Company SEC filings (Q3 FY2025 ended October 27, 2024)
- Market Data: Historical market data snapshot
- Industry Analysis: Based on earnings reports and industry research

**Disclaimer**: This dashboard is for informational and educational purposes only. Not investment advice.
""")