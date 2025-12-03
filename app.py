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

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E86AB;
    }
    .stButton>button {
        background-color: #2E86AB;
        color: white;
        font-weight: bold;
        border-radius: 0.5rem;
        padding: 0.5rem 2rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #1a5f7a;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main application function."""
    
    # Header
    st.markdown('<div class="main-header">📊 Automated Insight Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-Powered AdTech Campaign Analysis & Reporting</div>', unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/2E86AB/FFFFFF?text=H-001", use_container_width=True)
        st.title("⚙️ Configuration")
        
        # AI Provider selection
        ai_provider = st.selectbox(
            "AI Provider",
            ["None (Rule-based)", "OpenAI GPT-4", "Google Gemini"],
            help="Select AI provider for generating insights"
        )
        
        api_key = None
        if ai_provider != "None (Rule-based)":
            api_key = st.text_input(
                "API Key",
                type="password",
                help="Enter your API key for the selected provider"
            )
        
        # Report format selection
        report_format = st.selectbox(
            "Report Format",
            ["PDF", "PowerPoint (PPTX)", "Both"],
            help="Select output format for the report"
        )
        
        st.divider()
        
        # About section
        st.markdown("### About")
        st.info("""
        **Automated Insight Engine** transforms raw AdTech data into executive-ready reports with AI-driven insights.
        
        **Features:**
        - 📥 CSV data ingestion
        - 🧹 Automatic data cleaning
        - 📊 KPI calculation
        - 🤖 AI-powered insights
        - 📈 Performance visualization
        - 📄 Professional report generation
        """)
    
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
        st.header("Upload Campaign Data")
        
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=['csv'],
            help="Upload your AdTech campaign data in CSV format"
        )
        
        if uploaded_file is not None:
            # Load data
            df = load_csv(uploaded_file)
            
            if df is not None:
                st.session_state.df_raw = df
                st.success(f"✅ Data loaded successfully! {df.shape[0]} rows × {df.shape[1]} columns")
                
                # Preview raw data
                preview_data(df, "Raw Data Preview", rows=10)
                
                # Clean and process button
                if st.button("🧹 Clean & Process Data", use_container_width=True):
                    with st.spinner("Cleaning and processing data..."):
                        # Clean data
                        df_clean = clean_data(df)
                        st.session_state.df_clean = df_clean
                        
                        # Calculate KPIs
                        df_kpi = calculate_kpis(df_clean)
                        st.session_state.df_kpi = df_kpi
                        
                        # Get summary metrics
                        summary = get_summary_metrics(df_kpi)
                        st.session_state.summary = summary
                        
                        st.success("✅ Data cleaned and KPIs calculated!")
                        st.rerun()
        
        # Show cleaned data if available
        if st.session_state.df_clean is not None:
            st.divider()
            preview_data(st.session_state.df_clean, "Cleaned Data Preview", rows=10)
    
    # Tab 2: Analysis & KPIs
    with tab2:
        st.header("Performance Analysis & KPIs")
        
        if st.session_state.summary is not None:
            summary = st.session_state.summary
            
            # Display key metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if 'total_impressions' in summary:
                    st.metric("Total Impressions", f"{summary['total_impressions']:,.0f}")
                if 'total_clicks' in summary:
                    st.metric("Total Clicks", f"{summary['total_clicks']:,.0f}")
            
            with col2:
                if 'overall_CTR' in summary:
                    st.metric("CTR", f"{summary['overall_CTR']:.2f}%")
                if 'overall_CPC' in summary:
                    st.metric("CPC", f"${summary['overall_CPC']:.2f}")
            
            with col3:
                if 'total_spend' in summary:
                    st.metric("Total Spend", f"${summary['total_spend']:,.2f}")
                if 'overall_CPM' in summary:
                    st.metric("CPM", f"${summary['overall_CPM']:.2f}")
            
            with col4:
                if 'total_conversions' in summary:
                    st.metric("Total Conversions", f"{summary['total_conversions']:,.0f}")
                if 'overall_ROAS' in summary:
                    st.metric("ROAS", f"{summary['overall_ROAS']:.2f}x")
            
            st.divider()
            
            # Show KPI data table
            if st.session_state.df_kpi is not None:
                st.subheader("Detailed KPI Data")
                st.dataframe(st.session_state.df_kpi, use_container_width=True)
                
                # Generate visualizations
                if st.button("📈 Generate Visualizations", use_container_width=True):
                    with st.spinner("Creating charts..."):
                        output_dir = ensure_output_dir("output")
                        charts = generate_all_charts(st.session_state.df_kpi, output_dir)
                        st.session_state.charts = charts
                        st.success("✅ Charts generated!")
                        st.rerun()
        else:
            st.info("👆 Please upload and process data first in the 'Upload Data' tab.")
    
    # Tab 3: AI Insights
    with tab3:
        st.header("AI-Powered Insights")
        
        if st.session_state.summary is not None:
            if st.button("🤖 Generate AI Insights", use_container_width=True):
                with st.spinner("Generating insights with AI..."):
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
                    st.success("✅ Insights generated!")
                    st.rerun()
            
            # Display insights if available
            if st.session_state.insights is not None:
                insights = st.session_state.insights
                
                # Key Insights
                if insights.get('key_insights'):
                    st.subheader("🔍 Key Insights")
                    for i, insight in enumerate(insights['key_insights'], 1):
                        st.markdown(f"**{i}.** {insight}")
                    st.divider()
                
                # Trend Analysis
                if insights.get('trends'):
                    st.subheader("📈 Trend Analysis")
                    for i, trend in enumerate(insights['trends'], 1):
                        st.markdown(f"**{i}.** {trend}")
                    st.divider()
                
                # Performance Issues
                if insights.get('issues'):
                    st.subheader("⚠️ Performance Issues")
                    for i, issue in enumerate(insights['issues'], 1):
                        st.warning(f"**{i}.** {issue}")
                    st.divider()
                
                # Recommendations
                if insights.get('recommendations'):
                    st.subheader("💡 Actionable Recommendations")
                    for i, rec in enumerate(insights['recommendations'], 1):
                        st.success(f"**{i}.** {rec}")
        else:
            st.info("👆 Please upload and process data first.")
        
        # Show charts if available
        if st.session_state.charts is not None:
            st.divider()
            st.subheader("📊 Performance Visualizations")
            
            for chart_name, chart_path in st.session_state.charts.items():
                if os.path.exists(chart_path):
                    st.image(chart_path, use_container_width=True)
    
    # Tab 4: Report Generation
    with tab4:
        st.header("Generate Executive Report")
        
        if st.session_state.summary and st.session_state.insights:
            st.info(f"**Report Format:** {report_format}")
            
            if st.button("📄 Generate Report", use_container_width=True, type="primary"):
                with st.spinner("Generating professional report..."):
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
                    
                    # Download buttons
                    st.subheader("📥 Download Reports")
                    
                    for format_name, file_path in report_files:
                        with open(file_path, "rb") as file:
                            file_data = file.read()
                            file_name = os.path.basename(file_path)
                            
                            st.download_button(
                                label=f"⬇️ Download {format_name} Report",
                                data=file_data,
                                file_name=file_name,
                                mime="application/pdf" if format_name == "PDF" else "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                                use_container_width=True
                            )
                    
                    st.balloons()
        else:
            st.info("👆 Please complete the analysis and generate insights first.")
            
            # Show checklist
            st.markdown("### ✅ Checklist:")
            st.markdown(f"- {'✅' if st.session_state.df_raw is not None else '❌'} Upload data")
            st.markdown(f"- {'✅' if st.session_state.df_clean is not None else '❌'} Clean & process data")
            st.markdown(f"- {'✅' if st.session_state.summary is not None else '❌'} Calculate KPIs")
            st.markdown(f"- {'✅' if st.session_state.insights is not None else '❌'} Generate insights")


if __name__ == "__main__":
    main()
