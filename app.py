"""
Automated Insight Engine - Main Streamlit Application
AdTech Campaign Performance Analysis & Reporting Tool
"""
import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import custom modules
from src.ingest import load_csv, preview_data
from src.process import clean_data, calculate_kpis, get_summary_metrics
from src.insights import (
    generate_insights_openai, 
    generate_insights_gemini, 
    generate_fallback_insights,
    format_insights_for_display
)
from src.visualize import generate_all_charts
from src.report_gen import create_pdf_report, create_pptx_report
from src.utils import ensure_output_dir, get_timestamp


# Page configuration
st.set_page_config(
    page_title="Automated Insight Engine",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced UI
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Header styling */
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .sub-header {
        font-size: 1.3rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 500;
    }
    
    /* Card styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        color: white;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.15);
    }
    
    /* Enhanced metric cards */
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: bold;
        color: #2E86AB;
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 1rem;
        font-weight: 600;
        color: #555;
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #2E86AB 0%, #1a5f7a 100%);
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        border: none;
        box-shadow: 0 4px 8px rgba(46, 134, 171, 0.3);
        transition: all 0.3s ease;
        font-size: 1.1rem;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #1a5f7a 0%, #2E86AB 100%);
        box-shadow: 0 6px 12px rgba(46, 134, 171, 0.4);
        transform: translateY(-2px);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(255, 255, 255, 0.8);
        padding: 10px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: white;
        border-radius: 8px;
        color: #2E86AB;
        font-weight: 600;
        padding: 0 24px;
        border: 2px solid transparent;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%);
        color: white;
        border: 2px solid #2E86AB;
    }
    
    /* File uploader styling */
    .uploadedFile {
        border: 2px dashed #2E86AB;
        border-radius: 10px;
        padding: 20px;
        background-color: rgba(46, 134, 171, 0.05);
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2E86AB 0%, #1a5f7a 100%);
    }
    
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label {
        color: white !important;
    }
    
    section[data-testid="stSidebar"] .stSelectbox > div > div,
    section[data-testid="stSidebar"] .stTextInput > div > div > input,
    section[data-testid="stSidebar"] input {
        background-color: white !important;
        color: #333 !important;
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: white !important;
    }
    
    /* Success/Info/Warning boxes */
    .stSuccess {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        border-radius: 5px;
        padding: 1rem;
    }
    
    .stInfo {
        background-color: #d1ecf1;
        border-left: 5px solid #17a2b8;
        border-radius: 5px;
        padding: 1rem;
    }
    
    .stWarning {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        border-radius: 5px;
        padding: 1rem;
    }
    
    /* DataFrame styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* Divider styling */
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #2E86AB, transparent);
    }
    
    /* Custom info boxes */
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .success-box {
        background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(86, 171, 47, 0.3);
    }
    
    /* Download button special styling */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        border: none;
        box-shadow: 0 4px 8px rgba(86, 171, 47, 0.3);
    }
    
    .stDownloadButton>button:hover {
        background: linear-gradient(135deg, #a8e063 0%, #56ab2f 100%);
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main application function."""
    
    # Initialize session state variables
    if 'df_raw' not in st.session_state:
        st.session_state.df_raw = None
    if 'df_clean' not in st.session_state:
        st.session_state.df_clean = None
    if 'df_kpi' not in st.session_state:
        st.session_state.df_kpi = None
    if 'summary' not in st.session_state:
        st.session_state.summary = None
    if 'insights' not in st.session_state:
        st.session_state.insights = None
    if 'charts' not in st.session_state:
        st.session_state.charts = None
    
    # Header
    st.markdown('<div class="main-header">📊 Automated Insight Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-Powered AdTech Campaign Analysis & Reporting</div>', unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        # Logo/Banner
        st.markdown("""
        <div style='text-align: center; padding: 20px; background: rgba(255,255,255,0.1); border-radius: 10px; margin-bottom: 20px;'>
            <h1 style='color: white; margin: 0; font-size: 2rem;'>📊</h1>
            <h3 style='color: white; margin: 5px 0;'>H-001</h3>
            <p style='color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;'>Insight Engine</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### ⚙️ Configuration")
        
        # AI Provider selection
        ai_provider = st.selectbox(
            "🤖 AI Provider",
            ["None (Rule-based)", "OpenAI GPT-4", "Google Gemini"],
            help="Select AI provider for generating insights"
        )
        
        api_key = None
        if ai_provider != "None (Rule-based)":
            api_key = st.text_input(
                "🔑 API Key",
                type="password",
                help="Enter your API key for the selected provider"
            )
        
        # Report format selection
        report_format = st.selectbox(
            "📄 Report Format",
            ["PDF", "PowerPoint (PPTX)", "Both"],
            help="Select output format for the report"
        )
        
        st.divider()
        
        # Progress indicator
        st.markdown("### 📈 Progress")
        progress_items = [
            ("Upload Data", st.session_state.df_raw is not None),
            ("Clean Data", st.session_state.df_clean is not None),
            ("Calculate KPIs", st.session_state.summary is not None),
            ("Generate Insights", st.session_state.insights is not None),
            ("Create Charts", st.session_state.charts is not None)
        ]
        
        for item, completed in progress_items:
            icon = "✅" if completed else "⭕"
            color = "#56ab2f" if completed else "#999"
            st.markdown(f"<p style='color: {color}; margin: 5px 0;'>{icon} {item}</p>", unsafe_allow_html=True)
        
        st.divider()
        
        # About section
        st.markdown("### 💡 About")
        st.markdown("""
        <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; font-size: 0.9rem;'>
            <p style='color: white; margin: 0;'><strong>Automated Insight Engine</strong> transforms raw AdTech data into executive-ready reports with AI-driven insights.</p>
            <br>
            <p style='color: rgba(255,255,255,0.8); margin: 5px 0;'>📥 CSV ingestion</p>
            <p style='color: rgba(255,255,255,0.8); margin: 5px 0;'>🧹 Auto data cleaning</p>
            <p style='color: rgba(255,255,255,0.8); margin: 5px 0;'>📊 KPI calculation</p>
            <p style='color: rgba(255,255,255,0.8); margin: 5px 0;'>🤖 AI insights</p>
            <p style='color: rgba(255,255,255,0.8); margin: 5px 0;'>📈 Visualizations</p>
            <p style='color: rgba(255,255,255,0.8); margin: 5px 0;'>📄 Report export</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'df_raw' not in st.session_state:
        st.session_state.df_raw = None
    if 'df_clean' not in st.session_state:
        st.session_state.df_clean = None
    if 'df_kpi' not in st.session_state:
        st.session_state.df_kpi = None
    if 'summary' not in st.session_state:
        st.session_state.summary = None
    if 'insights' not in st.session_state:
        st.session_state.insights = None
    if 'charts' not in st.session_state:
        st.session_state.charts = None
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["📥 Upload Data", "📊 Analysis", "🤖 Insights", "📄 Reports"])
    
    # Tab 1: Data Upload
    with tab1:
        st.markdown("## 📥 Upload Campaign Data")
        
        # Create two columns for layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "Choose a CSV file",
                type=['csv'],
                help="Upload your AdTech campaign data in CSV format"
            )
        
        with col2:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 20px; border-radius: 10px; color: white; text-align: center;'>
                <h4 style='margin: 0; color: white;'>📊 Sample Data</h4>
                <p style='margin: 10px 0; font-size: 0.9rem;'>Use our sample CSV to test the app immediately!</p>
                <p style='margin: 0; font-size: 0.8rem;'>Location: data/sample_campaign_data.csv</p>
            </div>
            """, unsafe_allow_html=True)
        
        if uploaded_file is not None:
            # Load data
            df = load_csv(uploaded_file)
            
            if df is not None:
                st.session_state.df_raw = df
                
                st.markdown("""
                <div class='success-box'>
                    <h4 style='margin: 0; color: white;'>✅ Data Loaded Successfully!</h4>
                    <p style='margin: 10px 0 0 0; font-size: 1.1rem;'>
                        <strong>{} rows</strong> × <strong>{} columns</strong>
                    </p>
                </div>
                """.format(df.shape[0], df.shape[1]), unsafe_allow_html=True)
                
                # Preview raw data
                st.markdown("### 👀 Data Preview")
                preview_data(df, "Raw Data", rows=10)
                
                # Clean and process button
                st.markdown("<br>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("🧹 Clean & Process Data", use_container_width=True, type="primary"):
                        with st.spinner("🔄 Cleaning and processing data..."):
                            # Clean data
                            df_clean = clean_data(df)
                            st.session_state.df_clean = df_clean
                            
                            # Calculate KPIs
                            df_kpi = calculate_kpis(df_clean)
                            st.session_state.df_kpi = df_kpi
                            
                            # Get summary metrics
                            summary = get_summary_metrics(df_kpi)
                            st.session_state.summary = summary
                            
                            st.success("✅ Data cleaned and KPIs calculated successfully!")
                            st.balloons()
                            st.rerun()
        
        # Show cleaned data if available
        if st.session_state.df_clean is not None:
            st.divider()
            st.markdown("### ✨ Cleaned Data")
            preview_data(st.session_state.df_clean, "Cleaned Data Preview", rows=10)
    
    # Tab 2: Analysis & KPIs
    with tab2:
        st.markdown("## 📊 Performance Analysis & KPIs")
        
        if st.session_state.summary is not None:
            summary = st.session_state.summary
            
            # Hero metrics section
            st.markdown("""
            <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        border-radius: 15px; margin-bottom: 30px; color: white;'>
                <h2 style='margin: 0; color: white;'>📈 Campaign Performance Dashboard</h2>
                <p style='margin: 10px 0 0 0; font-size: 1.1rem; opacity: 0.9;'>Key metrics at a glance</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Display key metrics in columns with better styling
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if 'total_impressions' in summary:
                    st.metric("👁️ Total Impressions", f"{summary['total_impressions']:,.0f}")
                if 'total_clicks' in summary:
                    st.metric("🖱️ Total Clicks", f"{summary['total_clicks']:,.0f}")
            
            with col2:
                if 'overall_CTR' in summary:
                    st.metric("📊 CTR", f"{summary['overall_CTR']:.2f}%")
                if 'overall_CPC' in summary:
                    st.metric("💵 CPC", f"${summary['overall_CPC']:.2f}")
            
            with col3:
                if 'total_spend' in summary:
                    st.metric("💰 Total Spend", f"${summary['total_spend']:,.2f}")
                if 'overall_CPM' in summary:
                    st.metric("📈 CPM", f"${summary['overall_CPM']:.2f}")
            
            with col4:
                if 'total_conversions' in summary:
                    st.metric("✅ Conversions", f"{summary['total_conversions']:,.0f}")
                if 'overall_ROAS' in summary:
                    st.metric("🎯 ROAS", f"{summary['overall_ROAS']:.2f}x")
            
            st.divider()
            
            # Show KPI data table
            if st.session_state.df_kpi is not None:
                st.markdown("### 📋 Detailed KPI Data")
                st.dataframe(st.session_state.df_kpi, use_container_width=True, height=400)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Generate visualizations
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("📈 Generate Visualizations", use_container_width=True, type="primary"):
                        with st.spinner("🎨 Creating professional charts..."):
                            output_dir = ensure_output_dir("output")
                            charts = generate_all_charts(st.session_state.df_kpi, output_dir)
                            st.session_state.charts = charts
                            st.success("✅ Charts generated successfully!")
                            st.balloons()
                            st.rerun()
        else:
            st.markdown("""
            <div class='info-box'>
                <h3 style='margin: 0; color: white;'>👆 Getting Started</h3>
                <p style='margin: 10px 0 0 0;'>Please upload and process data first in the 'Upload Data' tab.</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Tab 3: AI Insights
    with tab3:
        st.markdown("## 🤖 AI-Powered Insights")
        
        if st.session_state.summary is not None:
            # Info box about AI provider
            if ai_provider != "None (Rule-based)" and not api_key:
                st.markdown("""
                <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                            padding: 20px; border-radius: 15px; color: white; margin-bottom: 20px;'>
                    <h4 style='margin: 0; color: white;'>⚠️ API Key Required</h4>
                    <p style='margin: 10px 0 0 0;'>Please enter your API key in the sidebar or select "None (Rule-based)" to continue.</p>
                </div>
                """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🤖 Generate AI Insights", use_container_width=True, type="primary"):
                    with st.spinner("🧠 Analyzing data and generating insights..."):
                        # Prepare data for AI
                        df_sample = st.session_state.df_kpi.head(20).to_string()
                        summary = st.session_state.summary
                        
                        # Generate insights based on provider
                        if ai_provider == "OpenAI GPT-4" and api_key:
                            insights = generate_insights_openai(summary, df_sample, api_key)
                        elif ai_provider == "Google Gemini" and api_key:
                            insights = generate_insights_gemini(summary, df_sample, api_key)
                        else:
                            insights = generate_fallback_insights(summary)
                        
                        st.session_state.insights = insights
                        st.success("✅ Insights generated successfully!")
                        st.balloons()
                        st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Display insights if available
            if st.session_state.insights is not None:
                insights = st.session_state.insights
                
                # Key Insights
                if insights.get('key_insights'):
                    st.markdown("""
                    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                padding: 25px; border-radius: 15px; margin: 20px 0; color: white;'>
                        <h3 style='margin: 0 0 15px 0; color: white;'>🔍 Key Insights</h3>
                    """, unsafe_allow_html=True)
                    
                    for i, insight in enumerate(insights['key_insights'], 1):
                        st.markdown(f"<p style='color: white; margin: 10px 0; font-size: 1.05rem;'><strong>{i}.</strong> {insight}</p>", unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # Trend Analysis
                if insights.get('trends'):
                    st.markdown("""
                    <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                                padding: 25px; border-radius: 15px; margin: 20px 0; color: white;'>
                        <h3 style='margin: 0 0 15px 0; color: white;'>📈 Trend Analysis</h3>
                    """, unsafe_allow_html=True)
                    
                    for i, trend in enumerate(insights['trends'], 1):
                        st.markdown(f"<p style='color: white; margin: 10px 0; font-size: 1.05rem;'><strong>{i}.</strong> {trend}</p>", unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # Performance Issues
                if insights.get('issues'):
                    st.markdown("""
                    <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
                                padding: 25px; border-radius: 15px; margin: 20px 0; color: #333;'>
                        <h3 style='margin: 0 0 15px 0; color: #333;'>⚠️ Performance Issues</h3>
                    """, unsafe_allow_html=True)
                    
                    for i, issue in enumerate(insights['issues'], 1):
                        st.markdown(f"<p style='color: #333; margin: 10px 0; font-size: 1.05rem;'><strong>{i}.</strong> {issue}</p>", unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # Recommendations
                if insights.get('recommendations'):
                    st.markdown("""
                    <div style='background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%); 
                                padding: 25px; border-radius: 15px; margin: 20px 0; color: white;'>
                        <h3 style='margin: 0 0 15px 0; color: white;'>💡 Actionable Recommendations</h3>
                    """, unsafe_allow_html=True)
                    
                    for i, rec in enumerate(insights['recommendations'], 1):
                        st.markdown(f"<p style='color: white; margin: 10px 0; font-size: 1.05rem;'><strong>{i}.</strong> {rec}</p>", unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='info-box'>
                <h3 style='margin: 0; color: white;'>👆 Getting Started</h3>
                <p style='margin: 10px 0 0 0;'>Please upload and process data first.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Show charts if available
        if st.session_state.charts is not None:
            st.divider()
            st.markdown("### 📊 Performance Visualizations")
            
            chart_cols = st.columns(1)
            for chart_name, chart_path in st.session_state.charts.items():
                if os.path.exists(chart_path):
                    st.image(chart_path, use_container_width=True)
                    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tab 4: Report Generation
    with tab4:
        st.markdown("## 📄 Generate Executive Report")
        
        if st.session_state.summary and st.session_state.insights:
            # Report format display
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 25px; border-radius: 15px; color: white; text-align: center; margin-bottom: 30px;'>
                <h3 style='margin: 0; color: white;'>📊 Report Configuration</h3>
                <p style='margin: 15px 0 0 0; font-size: 1.2rem;'><strong>Selected Format:</strong> {report_format}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("📄 Generate Report", use_container_width=True, type="primary"):
                    with st.spinner("📝 Generating professional report..."):
                        output_dir = ensure_output_dir("output")
                        timestamp = get_timestamp()
                        
                        # Ensure charts are generated
                        if st.session_state.charts is None:
                            charts = generate_all_charts(st.session_state.df_kpi, output_dir)
                            st.session_state.charts = charts
                        
                        report_files = []
                        
                        # Generate PDF
                        if report_format in ["PDF", "Both"]:
                            pdf_path = os.path.join(output_dir, f"campaign_report_{timestamp}.pdf")
                            create_pdf_report(
                                st.session_state.summary,
                                st.session_state.insights,
                                st.session_state.charts,
                                pdf_path
                            )
                            report_files.append(("PDF", pdf_path))
                        
                        # Generate PPTX
                        if report_format in ["PowerPoint (PPTX)", "Both"]:
                            pptx_path = os.path.join(output_dir, f"campaign_report_{timestamp}.pptx")
                            create_pptx_report(
                                st.session_state.summary,
                                st.session_state.insights,
                                st.session_state.charts,
                                pptx_path
                            )
                            report_files.append(("PPTX", pptx_path))
                        
                        st.success("✅ Report generated successfully!")
                        st.balloons()
                        
                        # Download section
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown("""
                        <div style='background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%); 
                                    padding: 25px; border-radius: 15px; color: white; text-align: center;'>
                            <h3 style='margin: 0; color: white;'>📥 Download Your Reports</h3>
                            <p style='margin: 10px 0 0 0;'>Your professional reports are ready!</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Download buttons in columns
                        download_cols = st.columns(len(report_files))
                        
                        for idx, (format_name, file_path) in enumerate(report_files):
                            with download_cols[idx]:
                                with open(file_path, "rb") as file:
                                    file_data = file.read()
                                    file_name = os.path.basename(file_path)
                                    
                                    st.download_button(
                                        label=f"⬇️ Download {format_name}",
                                        data=file_data,
                                        file_name=file_name,
                                        mime="application/pdf" if format_name == "PDF" else "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                                        use_container_width=True
                                    )
        else:
            st.markdown("""
            <div class='info-box'>
                <h3 style='margin: 0; color: white;'>📋 Checklist Before Generating Report</h3>
                <p style='margin: 15px 0 10px 0;'>Complete these steps first:</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show checklist with better styling
            checklist_items = [
                ("Upload data", st.session_state.df_raw is not None),
                ("Clean & process data", st.session_state.df_clean is not None),
                ("Calculate KPIs", st.session_state.summary is not None),
                ("Generate insights", st.session_state.insights is not None)
            ]
            
            for item, completed in checklist_items:
                icon = "✅" if completed else "❌"
                color = "#56ab2f" if completed else "#f5576c"
                st.markdown(f"""
                <div style='background: {color}; color: white; padding: 15px; 
                            border-radius: 10px; margin: 10px 0; font-size: 1.1rem;'>
                    {icon} <strong>{item}</strong>
                </div>
                """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
