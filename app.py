import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Shipping Cost Analyzer",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean, professional look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'DM Sans', sans-serif;
    }
    
    .main > div {
        padding-top: 2rem;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1a1a2e !important;
        color: white !important;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
        margin-top: 0.25rem;
    }
    
    .issue-card {
        background: #fff;
        border-left: 4px solid #ff6b6b;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
        border-radius: 0 8px 8px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .issue-card.warning {
        border-left-color: #feca57;
    }
    
    .issue-card.info {
        border-left-color: #54a0ff;
    }
    
    .issue-title {
        font-weight: 600;
        margin-bottom: 0.25rem;
        color: #1a1a2e;
    }
    
    .issue-detail {
        font-size: 0.85rem;
        color: #666;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }
    
    .upload-zone {
        border: 2px dashed #e0e0e0;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        background: #fafafa;
        transition: all 0.3s ease;
    }
    
    .upload-zone:hover {
        border-color: #667eea;
        background: #f5f5ff;
    }
    
    h1 {
        color: #1a1a2e;
        font-weight: 700;
    }
    
    h2, h3 {
        color: #1a1a2e;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Chinese to English country mapping
COUNTRY_MAP = {
    '美国': 'United States',
    '英国': 'United Kingdom',
    '澳大利亚': 'Australia',
    '爱尔兰': 'Ireland',
    '加拿大': 'Canada',
    '荷兰': 'Netherlands',
    '挪威': 'Norway',
    '阿联酋': 'United Arab Emirates',
    '德国': 'Germany',
    '丹麦': 'Denmark',
    '以色列': 'Israel',
    '瑞典': 'Sweden',
    '芬兰': 'Finland',
    '瑞士': 'Switzerland',
    '新西兰': 'New Zealand',
    '法国': 'France',
    '意大利': 'Italy',
    '西班牙': 'Spain',
    '比利时': 'Belgium',
    '奥地利': 'Austria',
    '波兰': 'Poland',
    '葡萄牙': 'Portugal',
    '日本': 'Japan',
    '韩国': 'South Korea',
    '新加坡': 'Singapore',
    '香港': 'Hong Kong',
    '台湾': 'Taiwan',
    '马来西亚': 'Malaysia',
    '泰国': 'Thailand',
    '印度': 'India',
    '墨西哥': 'Mexico',
    '巴西': 'Brazil',
    '南非': 'South Africa',
    '希腊': 'Greece',
    '捷克': 'Czech Republic',
    '匈牙利': 'Hungary',
    '罗马尼亚': 'Romania',
    '斯洛伐克': 'Slovakia',
    '斯洛文尼亚': 'Slovenia',
    '克罗地亚': 'Croatia',
    '保加利亚': 'Bulgaria',
    '塞浦路斯': 'Cyprus',
    '爱沙尼亚': 'Estonia',
    '拉脱维亚': 'Latvia',
    '立陶宛': 'Lithuania',
    '卢森堡': 'Luxembourg',
    '马耳他': 'Malta',
    '冰岛': 'Iceland',
    '土耳其': 'Turkey',
    '俄罗斯': 'Russia',
    '乌克兰': 'Ukraine',
    '沙特阿拉伯': 'Saudi Arabia',
    '卡塔尔': 'Qatar',
    '科威特': 'Kuwait',
    '巴林': 'Bahrain',
    '阿曼': 'Oman',
    '菲律宾': 'Philippines',
    '印度尼西亚': 'Indonesia',
    '越南': 'Vietnam',
}

RMB_TO_USD = 0.139

def translate_country(chinese_name):
    """Translate Chinese country name to English."""
    return COUNTRY_MAP.get(chinese_name, chinese_name)

def process_data(shipping_df, shopify_df):
    """Process and merge the two dataframes."""
    
    # Rename shipping columns for clarity
    shipping_df = shipping_df.rename(columns={
        '物流单号': 'tracking_number',
        '收货时间': 'ship_date',
        '总金额': 'shipping_cost_rmb',
        '国家/计费分区': 'country_chinese',
        '计费重': 'weight_kg',
        '客户单号': 'internal_order_id'
    })
    
    # Convert shipping cost to USD
    shipping_df['shipping_cost_usd'] = shipping_df['shipping_cost_rmb'] * RMB_TO_USD
    
    # Translate country names
    shipping_df['country_from_shipping'] = shipping_df['country_chinese'].apply(translate_country)
    
    # Rename Shopify columns
    shopify_df = shopify_df.rename(columns={
        'Order': 'order_number',
        'Order created at date': 'order_date',
        'Tracking number': 'tracking_number',
        'Net payout': 'net_payout',
        'Shipping country': 'country',
        'Cost': 'product_cost'
    })
    
    # Merge on tracking number
    merged_df = pd.merge(
        shopify_df,
        shipping_df[['tracking_number', 'shipping_cost_usd', 'shipping_cost_rmb', 'weight_kg', 'ship_date', 'country_from_shipping']],
        on='tracking_number',
        how='outer',
        indicator=True
    )
    
    # Calculate shipping as % of net payout
    merged_df['shipping_pct'] = (merged_df['shipping_cost_usd'] / merged_df['net_payout'] * 100).round(2)
    
    # Calculate profit
    merged_df['profit'] = merged_df['net_payout'] - merged_df['product_cost'] - merged_df['shipping_cost_usd']
    
    return merged_df, shipping_df, shopify_df

def identify_issues(merged_df, shopify_df):
    """Identify all issues for the Issues tab."""
    issues = {
        'unmatched_shipments': [],
        'unmatched_orders': [],
        'multi_tracking': [],
        'country_mismatch': []
    }
    
    # Unmatched shipments (in shipping file but not in Shopify)
    unmatched_ship = merged_df[merged_df['_merge'] == 'right_only']
    for _, row in unmatched_ship.iterrows():
        issues['unmatched_shipments'].append({
            'tracking': row['tracking_number'],
            'shipping_cost': row['shipping_cost_usd'],
            'ship_date': row['ship_date'],
            'country': row['country_from_shipping']
        })
    
    # Unmatched orders (4PX tracking in Shopify but no shipping cost)
    unmatched_orders = merged_df[
        (merged_df['_merge'] == 'left_only') & 
        (merged_df['tracking_number'].str.contains('4PX', na=False))
    ]
    for _, row in unmatched_orders.iterrows():
        issues['unmatched_orders'].append({
            'order': row['order_number'],
            'tracking': row['tracking_number'],
            'net_payout': row['net_payout'],
            'country': row['country']
        })
    
    # Check for multi-tracking (same order number appears multiple times)
    order_counts = shopify_df['order_number'].value_counts()
    multi_orders = order_counts[order_counts > 1]
    for order_num, count in multi_orders.items():
        order_rows = shopify_df[shopify_df['order_number'] == order_num]
        issues['multi_tracking'].append({
            'order': order_num,
            'count': count,
            'trackings': order_rows['tracking_number'].tolist(),
            'net_payout': order_rows['net_payout'].iloc[0]
        })
    
    # Country mismatch between shipping file and Shopify
    matched = merged_df[merged_df['_merge'] == 'both'].copy()
    mismatches = matched[matched['country'] != matched['country_from_shipping']]
    for _, row in mismatches.iterrows():
        if pd.notna(row['country']) and pd.notna(row['country_from_shipping']):
            issues['country_mismatch'].append({
                'order': row['order_number'],
                'tracking': row['tracking_number'],
                'shopify_country': row['country'],
                'shipping_country': row['country_from_shipping']
            })
    
    return issues

def create_download_excel(df):
    """Create downloadable Excel file."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Merged Data')
    output.seek(0)
    return output

# Main app
def main():
    st.title("📦 Shipping Cost Analyzer")
    st.markdown("Upload your shipping costs and Shopify exports to analyze your logistics performance.")
    
    # Sidebar for uploads
    with st.sidebar:
        st.header("📁 Upload Files")
        
        st.markdown("**Shipping Costs (Excel)**")
        shipping_file = st.file_uploader(
            "Drag and drop your shipping cost file",
            type=['xlsx', 'xls'],
            key='shipping',
            label_visibility='collapsed'
        )
        
        st.markdown("**Shopify Export (CSV)**")
        shopify_file = st.file_uploader(
            "Drag and drop your Shopify export",
            type=['csv'],
            key='shopify',
            label_visibility='collapsed'
        )
        
        st.divider()
        
        st.markdown(f"**Exchange Rate:** 1 RMB = ${RMB_TO_USD} USD")
        
        if shipping_file and shopify_file:
            st.success("✓ Both files uploaded")
    
    # Main content
    if not shipping_file or not shopify_file:
        # Show upload instructions
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="upload-zone">
                <h3>📊 Shipping Costs</h3>
                <p>Excel file with columns:</p>
                <ul style="text-align: left; display: inline-block;">
                    <li>物流单号 (Tracking number)</li>
                    <li>收货时间 (Ship date)</li>
                    <li>总金额 (Total cost in RMB)</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="upload-zone">
                <h3>🛒 Shopify Export</h3>
                <p>CSV file with columns:</p>
                <ul style="text-align: left; display: inline-block;">
                    <li>Order</li>
                    <li>Tracking number</li>
                    <li>Net payout</li>
                    <li>Shipping country</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        st.info("👈 Upload both files in the sidebar to get started")
        return
    
    # Process the data
    try:
        shipping_df = pd.read_excel(shipping_file)
        shopify_df = pd.read_csv(shopify_file)
        merged_df, shipping_processed, shopify_processed = process_data(shipping_df, shopify_df)
        issues = identify_issues(merged_df, shopify_processed)
    except Exception as e:
        st.error(f"Error processing files: {str(e)}")
        return
    
    # Count issues
    total_issues = (
        len(issues['unmatched_shipments']) + 
        len(issues['unmatched_orders']) + 
        len(issues['multi_tracking']) +
        len(issues['country_mismatch'])
    )
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Dashboard",
        f"⚠️ Issues ({total_issues})",
        "📋 Data Table",
        "📥 Export"
    ])
    
    # Get matched data for analytics
    matched_data = merged_df[merged_df['_merge'] == 'both'].copy()
    
    # TAB 1: Dashboard
    with tab1:
        if len(matched_data) == 0:
            st.warning("No matching records found between the two files.")
            return
        
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Matched Orders",
                f"{len(matched_data):,}",
                delta=f"{len(matched_data)/len(shopify_processed)*100:.1f}% of Shopify orders"
            )
        
        with col2:
            avg_shipping = matched_data['shipping_cost_usd'].mean()
            st.metric(
                "Avg Shipping Cost",
                f"${avg_shipping:.2f}",
                delta=None
            )
        
        with col3:
            avg_pct = matched_data['shipping_pct'].mean()
            st.metric(
                "Avg Shipping %",
                f"{avg_pct:.1f}%",
                delta="of Net Payout"
            )
        
        with col4:
            total_shipping = matched_data['shipping_cost_usd'].sum()
            st.metric(
                "Total Shipping Cost",
                f"${total_shipping:,.2f}",
                delta=None
            )
        
        st.divider()
        
        # Charts row
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📍 Average Shipping Cost by Country")
            country_stats = matched_data.groupby('country').agg({
                'shipping_cost_usd': ['mean', 'count', 'sum'],
                'shipping_pct': 'mean'
            }).round(2)
            country_stats.columns = ['avg_cost', 'order_count', 'total_cost', 'avg_pct']
            country_stats = country_stats.sort_values('avg_cost', ascending=True)
            
            fig = px.bar(
                country_stats.reset_index(),
                y='country',
                x='avg_cost',
                orientation='h',
                color='avg_cost',
                color_continuous_scale='Blues',
                labels={'avg_cost': 'Average Cost (USD)', 'country': 'Country'}
            )
            fig.update_layout(
                height=400,
                showlegend=False,
                coloraxis_showscale=False,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📈 Shipping % of Net Payout by Country")
            fig = px.bar(
                country_stats.reset_index(),
                y='country',
                x='avg_pct',
                orientation='h',
                color='avg_pct',
                color_continuous_scale='Reds',
                labels={'avg_pct': 'Shipping % of Net Payout', 'country': 'Country'}
            )
            fig.update_layout(
                height=400,
                showlegend=False,
                coloraxis_showscale=False,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Country breakdown table
        st.subheader("📊 Country Breakdown")
        country_table = country_stats.reset_index()
        country_table.columns = ['Country', 'Avg Cost (USD)', 'Orders', 'Total Cost (USD)', 'Avg % of Payout']
        country_table = country_table.sort_values('Orders', ascending=False)
        country_table['Avg Cost (USD)'] = country_table['Avg Cost (USD)'].apply(lambda x: f"${x:.2f}")
        country_table['Total Cost (USD)'] = country_table['Total Cost (USD)'].apply(lambda x: f"${x:,.2f}")
        country_table['Avg % of Payout'] = country_table['Avg % of Payout'].apply(lambda x: f"{x:.1f}%")
        st.dataframe(country_table, use_container_width=True, hide_index=True)
        
        st.divider()
        
        # Outliers section
        st.subheader("🔴 Outliers - Highest Shipping Costs")
        
        # Filter options
        col1, col2 = st.columns([1, 3])
        with col1:
            outlier_country = st.selectbox(
                "Filter by country",
                ["All Countries"] + sorted(matched_data['country'].dropna().unique().tolist())
            )
        
        outliers = matched_data.copy()
        if outlier_country != "All Countries":
            outliers = outliers[outliers['country'] == outlier_country]
        
        outliers = outliers.nlargest(20, 'shipping_cost_usd')[
            ['order_number', 'tracking_number', 'country', 'net_payout', 'shipping_cost_usd', 'shipping_pct', 'weight_kg']
        ]
        outliers.columns = ['Order', 'Tracking', 'Country', 'Net Payout', 'Shipping Cost', 'Shipping %', 'Weight (kg)']
        outliers['Net Payout'] = outliers['Net Payout'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "-")
        outliers['Shipping Cost'] = outliers['Shipping Cost'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "-")
        outliers['Shipping %'] = outliers['Shipping %'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "-")
        outliers['Weight (kg)'] = outliers['Weight (kg)'].apply(lambda x: f"{x:.3f}" if pd.notna(x) else "-")
        
        st.dataframe(outliers, use_container_width=True, hide_index=True)
    
    # TAB 2: Issues
    with tab2:
        st.subheader("🔧 Issues to Review")
        st.markdown("These items need your attention. Review and fix them in your source data.")
        
        # Summary cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Unmatched Shipments", len(issues['unmatched_shipments']))
        with col2:
            st.metric("Unmatched Orders", len(issues['unmatched_orders']))
        with col3:
            st.metric("Multi-Tracking", len(issues['multi_tracking']))
        with col4:
            st.metric("Country Mismatch", len(issues['country_mismatch']))
        
        st.divider()
        
        # Issue type selector
        issue_type = st.selectbox(
            "Filter by issue type",
            ["All Issues", "Unmatched Shipments", "Unmatched Orders", "Multi-Tracking Orders", "Country Mismatches"]
        )
        
        # Display issues
        if issue_type in ["All Issues", "Unmatched Shipments"] and issues['unmatched_shipments']:
            st.markdown("### 📦 Unmatched Shipments")
            st.markdown("*These tracking numbers are in your shipping file but have no matching Shopify order.*")
            
            unmatched_ship_df = pd.DataFrame(issues['unmatched_shipments'])
            unmatched_ship_df['shipping_cost'] = unmatched_ship_df['shipping_cost'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "-")
            unmatched_ship_df.columns = ['Tracking Number', 'Shipping Cost', 'Ship Date', 'Country']
            st.dataframe(unmatched_ship_df, use_container_width=True, hide_index=True)
            st.markdown("---")
        
        if issue_type in ["All Issues", "Unmatched Orders"] and issues['unmatched_orders']:
            st.markdown("### 🛒 Unmatched Orders")
            st.markdown("*These 4PX orders in Shopify have no matching shipping cost record.*")
            
            unmatched_orders_df = pd.DataFrame(issues['unmatched_orders'])
            unmatched_orders_df['net_payout'] = unmatched_orders_df['net_payout'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "-")
            unmatched_orders_df.columns = ['Order', 'Tracking Number', 'Net Payout', 'Country']
            st.dataframe(unmatched_orders_df, use_container_width=True, hide_index=True)
            st.markdown("---")
        
        if issue_type in ["All Issues", "Multi-Tracking Orders"] and issues['multi_tracking']:
            st.markdown("### 📑 Multi-Tracking Orders")
            st.markdown("*These orders have multiple tracking numbers. Verify the shipping cost allocation.*")
            
            for item in issues['multi_tracking']:
                with st.expander(f"Order {item['order']} — {item['count']} tracking numbers"):
                    st.markdown(f"**Net Payout:** ${item['net_payout']:.2f}")
                    st.markdown("**Tracking Numbers:**")
                    for t in item['trackings']:
                        st.markdown(f"- `{t}`")
            st.markdown("---")
        
        if issue_type in ["All Issues", "Country Mismatches"] and issues['country_mismatch']:
            st.markdown("### 🌍 Country Mismatches")
            st.markdown("*These orders have different countries in Shopify vs the shipping file.*")
            
            mismatch_df = pd.DataFrame(issues['country_mismatch'])
            mismatch_df.columns = ['Order', 'Tracking', 'Shopify Country', 'Shipping File Country']
            st.dataframe(mismatch_df, use_container_width=True, hide_index=True)
        
        if total_issues == 0:
            st.success("🎉 No issues found! All data matched perfectly.")
    
    # TAB 3: Data Table
    with tab3:
        st.subheader("📋 Merged Data")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            show_filter = st.selectbox(
                "Show",
                ["Matched Only", "All Records", "Unmatched Only"]
            )
        with col2:
            country_filter = st.selectbox(
                "Country",
                ["All"] + sorted(matched_data['country'].dropna().unique().tolist()),
                key='data_country'
            )
        
        # Apply filters
        display_df = merged_df.copy()
        if show_filter == "Matched Only":
            display_df = display_df[display_df['_merge'] == 'both']
        elif show_filter == "Unmatched Only":
            display_df = display_df[display_df['_merge'] != 'both']
        
        if country_filter != "All":
            display_df = display_df[display_df['country'] == country_filter]
        
        # Select columns to display
        display_cols = ['order_number', 'tracking_number', 'country', 'net_payout', 
                       'product_cost', 'shipping_cost_usd', 'shipping_pct', 'profit', 'order_date']
        display_df = display_df[[c for c in display_cols if c in display_df.columns]]
        
        # Format columns
        if 'net_payout' in display_df.columns:
            display_df['net_payout'] = display_df['net_payout'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "-")
        if 'product_cost' in display_df.columns:
            display_df['product_cost'] = display_df['product_cost'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "-")
        if 'shipping_cost_usd' in display_df.columns:
            display_df['shipping_cost_usd'] = display_df['shipping_cost_usd'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "-")
        if 'shipping_pct' in display_df.columns:
            display_df['shipping_pct'] = display_df['shipping_pct'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "-")
        if 'profit' in display_df.columns:
            display_df['profit'] = display_df['profit'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "-")
        
        display_df.columns = ['Order', 'Tracking', 'Country', 'Net Payout', 'Product Cost', 
                             'Shipping Cost', 'Shipping %', 'Profit', 'Order Date']
        
        st.dataframe(display_df, use_container_width=True, hide_index=True, height=600)
        st.caption(f"Showing {len(display_df):,} records")
    
    # TAB 4: Export
    with tab4:
        st.subheader("📥 Export Data")
        
        st.markdown("Download the merged data as an Excel file for further analysis.")
        
        # Prepare export data
        export_df = merged_df[merged_df['_merge'] == 'both'].copy()
        export_cols = ['order_number', 'tracking_number', 'order_date', 'country', 
                      'net_payout', 'product_cost', 'shipping_cost_usd', 'shipping_cost_rmb',
                      'shipping_pct', 'profit', 'weight_kg']
        export_df = export_df[[c for c in export_cols if c in export_df.columns]]
        export_df.columns = ['Order', 'Tracking', 'Order Date', 'Country', 
                            'Net Payout (USD)', 'Product Cost (USD)', 'Shipping Cost (USD)', 
                            'Shipping Cost (RMB)', 'Shipping %', 'Profit (USD)', 'Weight (kg)']
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            excel_data = create_download_excel(export_df)
            st.download_button(
                label="📥 Download Excel",
                data=excel_data,
                file_name=f"shipping_analysis_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        st.divider()
        
        st.markdown("### Preview")
        st.dataframe(export_df.head(20), use_container_width=True, hide_index=True)
        st.caption(f"Total records for export: {len(export_df):,}")

if __name__ == "__main__":
    main()
