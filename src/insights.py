"""
AI-powered insights generation using LLMs (GPT-4 or Gemini).
"""
import os
from typing import Dict, Any, Optional, List
import json


def generate_insights_openai(summary: Dict[str, Any], df_sample: str, api_key: str) -> Dict[str, List[str]]:
    """
    Generate insights using OpenAI GPT-4.
    
    Args:
        summary: Dictionary of summary metrics
        df_sample: String representation of sample data
        api_key: OpenAI API key
        
    Returns:
        Dictionary with insights, trends, issues, and recommendations
    """
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key)
        
        # Create prompt
        prompt = f"""
You are an expert AdTech data analyst. Analyze the following campaign performance data and provide insights.

SUMMARY METRICS:
{json.dumps(summary, indent=2)}

SAMPLE DATA:
{df_sample}

Please provide:
1. **Top 5 Key Insights**: Identify the most important findings from the data
2. **Trend Analysis**: Describe any trends in CTR, spend, conversions, or revenue
3. **Performance Issues**: Highlight any red flags or areas of concern
4. **Actionable Recommendations**: Provide 5 specific, actionable recommendations to improve campaign performance

Format your response as JSON with these keys:
{{
    "key_insights": ["insight 1", "insight 2", ...],
    "trends": ["trend 1", "trend 2", ...],
    "issues": ["issue 1", "issue 2", ...],
    "recommendations": ["recommendation 1", "recommendation 2", ...]
}}
"""
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert AdTech analyst providing data-driven insights."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        print(f"Error generating OpenAI insights: {str(e)}")
        return generate_fallback_insights(summary)


def generate_insights_gemini(summary: Dict[str, Any], df_sample: str, api_key: str) -> Dict[str, List[str]]:
    """
    Generate insights using Google Gemini.
    
    Args:
        summary: Dictionary of summary metrics
        df_sample: String representation of sample data
        api_key: Google API key
        
    Returns:
        Dictionary with insights, trends, issues, and recommendations
    """
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # Create prompt
        prompt = f"""
You are an expert AdTech data analyst. Analyze the following campaign performance data and provide insights.

SUMMARY METRICS:
{json.dumps(summary, indent=2)}

SAMPLE DATA:
{df_sample}

Please provide:
1. **Top 5 Key Insights**: Identify the most important findings from the data
2. **Trend Analysis**: Describe any trends in CTR, spend, conversions, or revenue
3. **Performance Issues**: Highlight any red flags or areas of concern
4. **Actionable Recommendations**: Provide 5 specific, actionable recommendations to improve campaign performance

Format your response as JSON with these keys:
{{
    "key_insights": ["insight 1", "insight 2", ...],
    "trends": ["trend 1", "trend 2", ...],
    "issues": ["issue 1", "issue 2", ...],
    "recommendations": ["recommendation 1", "recommendation 2", ...]
}}

Return ONLY the JSON object, nothing else.
"""
        
        response = model.generate_content(prompt)
        
        # Extract JSON from response
        text = response.text.strip()
        # Remove markdown code blocks if present
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        result = json.loads(text.strip())
        return result
        
    except Exception as e:
        print(f"Error generating Gemini insights: {str(e)}")
        return generate_fallback_insights(summary)


def generate_fallback_insights(summary: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Generate basic rule-based insights when API is unavailable.
    
    Args:
        summary: Dictionary of summary metrics
        
    Returns:
        Dictionary with basic insights
    """
    insights = {
        "key_insights": [],
        "trends": [],
        "issues": [],
        "recommendations": []
    }
    
    # Basic insights based on metrics
    if 'overall_CTR' in summary:
        ctr = summary['overall_CTR']
        if ctr < 1.0:
            insights['issues'].append(f"Low CTR of {ctr:.2f}% indicates poor ad relevance or targeting")
            insights['recommendations'].append("Improve ad copy and creative to increase engagement")
        else:
            insights['key_insights'].append(f"CTR of {ctr:.2f}% shows good engagement")
    
    if 'overall_CPC' in summary:
        cpc = summary['overall_CPC']
        insights['key_insights'].append(f"Average CPC is ${cpc:.2f}")
        if cpc > 2.0:
            insights['issues'].append(f"High CPC of ${cpc:.2f} may impact profitability")
            insights['recommendations'].append("Optimize bidding strategy to reduce cost per click")
    
    if 'overall_ROAS' in summary:
        roas = summary['overall_ROAS']
        if roas < 2.0:
            insights['issues'].append(f"ROAS of {roas:.2f} is below target threshold")
            insights['recommendations'].append("Focus on high-converting audiences and reduce spend on underperforming segments")
        else:
            insights['key_insights'].append(f"Strong ROAS of {roas:.2f} indicates profitable campaigns")
    
    if 'overall_Conversion_Rate' in summary:
        cvr = summary['overall_Conversion_Rate']
        if cvr < 2.0:
            insights['issues'].append(f"Conversion rate of {cvr:.2f}% needs improvement")
            insights['recommendations'].append("Optimize landing pages and checkout flow")
        else:
            insights['key_insights'].append(f"Conversion rate of {cvr:.2f}% is performing well")
    
    # Add generic recommendations
    insights['recommendations'].extend([
        "Monitor performance daily and adjust bids based on ROI",
        "A/B test different ad creatives and messaging",
        "Analyze top-performing segments and allocate more budget there",
        "Set up automated rules for pause underperforming campaigns"
    ])
    
    # Ensure we have exactly 5 recommendations
    insights['recommendations'] = insights['recommendations'][:5]
    
    # Add default insights if needed
    if not insights['key_insights']:
        insights['key_insights'].append("Data analysis completed successfully")
    
    if not insights['trends']:
        insights['trends'].append("More data points needed for trend analysis")
    
    return insights


def format_insights_for_display(insights: Dict[str, List[str]]) -> str:
    """
    Format insights dictionary into readable text.
    
    Args:
        insights: Dictionary of insights
        
    Returns:
        Formatted string
    """
    output = []
    
    if insights.get('key_insights'):
        output.append("🔍 **KEY INSIGHTS**")
        for i, insight in enumerate(insights['key_insights'], 1):
            output.append(f"{i}. {insight}")
        output.append("")
    
    if insights.get('trends'):
        output.append("📈 **TREND ANALYSIS**")
        for i, trend in enumerate(insights['trends'], 1):
            output.append(f"{i}. {trend}")
        output.append("")
    
    if insights.get('issues'):
        output.append("⚠️ **PERFORMANCE ISSUES**")
        for i, issue in enumerate(insights['issues'], 1):
            output.append(f"{i}. {issue}")
        output.append("")
    
    if insights.get('recommendations'):
        output.append("💡 **RECOMMENDATIONS**")
        for i, rec in enumerate(insights['recommendations'], 1):
            output.append(f"{i}. {rec}")
    
    return "\n".join(output)
