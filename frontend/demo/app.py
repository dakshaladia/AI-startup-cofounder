"""
Streamlit demo for AI Startup Co-Founder.
"""

import streamlit as st
import requests
import json
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from typing import Dict, List, Any

# Page configuration
st.set_page_config(
    page_title="AI Startup Co-Founder",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API configuration
API_BASE_URL = "http://localhost:8000"

def main():
    """Main Streamlit application."""
    
    # Header
    st.title("AI Startup Co-Founder")
    st.markdown("Multimodal AI Startup Co-Founder with Multi-Agent Pipeline")
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        page = st.selectbox(
            "Choose a page",
            ["Generate Ideas", "Upload Data", "View Ideas", "Analytics", "Settings"]
        )
    
    # Main content based on selected page
    if page == "Generate Ideas":
        generate_ideas_page()
    elif page == "Upload Data":
        upload_data_page()
    elif page == "View Ideas":
        view_ideas_page()
    elif page == "Analytics":
        analytics_page()
    elif page == "Settings":
        settings_page()

def generate_ideas_page():
    """Idea generation page."""
    st.header("Generate Startup Ideas")
    
    # Idea generation form
    with st.form("idea_generation_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            topic = st.text_input(
                "What startup idea would you like to explore?",
                placeholder="e.g., AI-powered personal finance, sustainable transportation..."
            )
            
            market_focus = st.selectbox(
                "Market Focus",
                ["Any", "Fintech", "Healthcare", "Education", "Sustainability", "Entertainment"]
            )
            
            target_audience = st.text_input(
                "Target Audience",
                placeholder="e.g., small businesses, millennials, healthcare professionals..."
            )
        
        with col2:
            technology_stack = st.multiselect(
                "Technology Stack",
                ["AI/ML", "Blockchain", "Web3", "IoT", "AR/VR", "Cloud", "Mobile", "Web"]
            )
            
            budget_range = st.selectbox(
                "Budget Range",
                ["Any", "Bootstrap ($0-10K)", "Seed ($10K-100K)", "Series A ($100K-1M)", "Enterprise ($1M+)"]
            )
            
            timeline = st.selectbox(
                "Implementation Timeline",
                ["Any", "3 months", "6 months", "1 year", "2+ years"]
            )
        
        # Advanced options
        with st.expander("Advanced Options"):
            num_ideas = st.slider("Number of ideas to generate", 1, 10, 3)
            temperature = st.slider("Creativity level", 0.1, 1.0, 0.7)
            focus_areas = st.multiselect(
                "Focus Areas",
                ["Innovation", "Market Fit", "Feasibility", "Scalability", "Profitability"]
            )
        
        submitted = st.form_submit_button("Generate Ideas", use_container_width=True)
    
    if submitted and topic:
        # Generate ideas
        with st.spinner("Generating ideas..."):
            ideas = generate_ideas(
                topic=topic,
                market_focus=market_focus,
                target_audience=target_audience,
                technology_stack=technology_stack,
                budget_range=budget_range,
                timeline=timeline,
                num_ideas=num_ideas,
                temperature=temperature,
                focus_areas=focus_areas
            )
        
        if ideas:
            st.success(f"Generated {len(ideas)} ideas!")
            
            # Display ideas
            for i, idea in enumerate(ideas, 1):
                with st.expander(f"Idea {i}: {idea.get('title', 'Untitled')}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write("**Description:**", idea.get('description', 'No description'))
                        st.write("**Problem:**", idea.get('problem', 'No problem statement'))
                        st.write("**Solution:**", idea.get('solution', 'No solution'))
                        st.write("**Target Market:**", idea.get('target_market', 'No target market'))
                        st.write("**Business Model:**", idea.get('business_model', 'No business model'))
                    
                    with col2:
                        # Scores
                        scores = idea.get('scores', {})
                        if scores:
                            st.metric("Overall Score", f"{scores.get('overall_score', 0):.2f}")
                            st.metric("Feasibility", f"{scores.get('feasibility_score', 0):.2f}")
                            st.metric("Novelty", f"{scores.get('novelty_score', 0):.2f}")
                            st.metric("Market Potential", f"{scores.get('market_potential_score', 0):.2f}")
                        
                        # Actions
                        if st.button(f"View Details", key=f"details_{i}"):
                            st.session_state.selected_idea = idea
                            st.rerun()
                        
                        if st.button(f"Export", key=f"export_{i}"):
                            export_idea(idea)
    
    # Display selected idea details if any
    if st.session_state.get('selected_idea'):
        display_idea_details(st.session_state.selected_idea)

def upload_data_page():
    """Data upload page."""
    st.header("Upload Data")
    
    # File upload
    uploaded_files = st.file_uploader(
        "Upload files to enhance idea generation",
        type=['pdf', 'png', 'jpg', 'jpeg', 'txt', 'docx'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.success(f"Uploaded {len(uploaded_files)} files")
        
        # Process files
        for file in uploaded_files:
            with st.expander(f"{file.name}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Size:** {file.size / 1024:.1f} KB")
                    st.write(f"**Type:** {file.type}")
                    st.write(f"**Last Modified:** {datetime.fromtimestamp(file.last_modified)}")
                
                with col2:
                    if st.button(f"Process {file.name}", key=f"process_{file.name}"):
                        with st.spinner(f"Processing {file.name}..."):
                            result = process_file(file)
                            if result:
                                st.success("File processed successfully!")
                                st.json(result)
                            else:
                                st.error("Failed to process file")

def view_ideas_page():
    """View ideas page."""
    st.header("View Ideas")
    
    # Get ideas from session state or API
    ideas = st.session_state.get('ideas', [])
    
    if not ideas:
        st.info("No ideas generated yet. Go to 'Generate Ideas' to create some!")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        score_filter = st.slider("Minimum Score", 0.0, 1.0, 0.0)
    
    with col2:
        date_filter = st.date_input("Created After", value=None)
    
    with col3:
        sort_by = st.selectbox("Sort By", ["Score", "Date", "Title"])
    
    # Filter and sort ideas
    filtered_ideas = ideas.copy()
    
    if score_filter > 0:
        filtered_ideas = [idea for idea in filtered_ideas 
                         if idea.get('scores', {}).get('overall_score', 0) >= score_filter]
    
    if date_filter:
        filtered_ideas = [idea for idea in filtered_ideas 
                         if datetime.fromisoformat(idea.get('created_at', '')).date() >= date_filter]
    
    if sort_by == "Score":
        filtered_ideas.sort(key=lambda x: x.get('scores', {}).get('overall_score', 0), reverse=True)
    elif sort_by == "Date":
        filtered_ideas.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    elif sort_by == "Title":
        filtered_ideas.sort(key=lambda x: x.get('title', ''))
    
    # Display ideas
    st.write(f"Showing {len(filtered_ideas)} ideas")
    
    for i, idea in enumerate(filtered_ideas):
        with st.expander(f"{idea.get('title', 'Untitled')}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("**Description:**", idea.get('description', 'No description'))
                st.write("**Created:**", idea.get('created_at', 'Unknown'))
            
            with col2:
                scores = idea.get('scores', {})
                if scores:
                    st.metric("Overall Score", f"{scores.get('overall_score', 0):.2f}")
                    st.metric("Feasibility", f"{scores.get('feasibility_score', 0):.2f}")
                    st.metric("Novelty", f"{scores.get('novelty_score', 0):.2f}")
                
                if st.button(f"View Details", key=f"view_{i}"):
                    st.session_state.selected_idea = idea
                    st.rerun()
    
    # Display selected idea details if any
    if st.session_state.get('selected_idea'):
        display_idea_details(st.session_state.selected_idea)

def display_idea_details(idea):
    """Display detailed information about a selected idea."""
    st.header("Idea Details")
    
    # Close button
    if st.button("Close Details"):
        st.session_state.selected_idea = None
        st.rerun()
    
    # Idea information
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(idea.get('title', 'Untitled Idea'))
        st.write("**Description:**", idea.get('description', 'No description available'))
        
        # Market analysis
        if 'market_analysis' in idea:
            st.subheader("Market Analysis")
            market_analysis = idea['market_analysis']
            if isinstance(market_analysis, dict):
                for key, value in market_analysis.items():
                    st.write(f"**{key.replace('_', ' ').title()}:**", value)
            else:
                st.write(market_analysis)
        
        # Tags
        if idea.get('tags'):
            st.write("**Tags:**", ", ".join(idea['tags']))
    
    with col2:
        st.subheader("Scores")
        scores = idea.get('scores', {})
        if scores:
            st.metric("Overall Score", f"{scores.get('overall_score', 0):.2f}")
            st.metric("Feasibility", f"{scores.get('feasibility_score', 0):.2f}")
            st.metric("Novelty", f"{scores.get('novelty_score', 0):.2f}")
            st.metric("Market Signal", f"{scores.get('market_signal_score', 0):.2f}")
        
        st.write("**Created:**", idea.get('created_at', 'Unknown'))
        st.write("**Status:**", idea.get('status', 'Unknown'))
    
    # Agent outputs
    st.subheader("Agent Analysis")
    
    agent_outputs = [
        ('market_analyst_output', 'Market Analyst'),
        ('idea_generator_output', 'Idea Generator'),
        ('critic_output', 'Critic'),
        ('pm_refiner_output', 'PM Refiner'),
        ('synthesizer_output', 'Synthesizer')
    ]
    
    for output_key, agent_name in agent_outputs:
        if idea.get(output_key):
            with st.expander(f"🔍 {agent_name} Analysis"):
                output = idea[output_key]
                if isinstance(output, dict):
                    for key, value in output.items():
                        st.write(f"**{key.replace('_', ' ').title()}:**", value)
                else:
                    st.write(output)
    
    # Actions
    st.subheader("Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Iterate Idea"):
            st.info("Iteration feature coming soon!")
    
    with col2:
        if st.button("Export Idea"):
            st.info("Export feature coming soon!")
    
    with col3:
        if st.button("Add Feedback"):
            st.info("Feedback feature coming soon!")

def analytics_page():
    """Analytics page."""
    st.header("Analytics")
    
    # Get ideas from session state
    ideas = st.session_state.get('ideas', [])
    
    if not ideas:
        st.info("No ideas to analyze. Generate some ideas first!")
        return
    
    # Analytics tabs
    tab1, tab2, tab3 = st.tabs(["Overview", "Scores", "Trends"])
    
    with tab1:
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Ideas", len(ideas))
        
        with col2:
            avg_score = sum(idea.get('scores', {}).get('overall_score', 0) for idea in ideas) / len(ideas)
            st.metric("Average Score", f"{avg_score:.2f}")
        
        with col3:
            high_score_ideas = [idea for idea in ideas 
                              if idea.get('scores', {}).get('overall_score', 0) >= 0.8]
            st.metric("High Score Ideas", len(high_score_ideas))
        
        with col4:
            recent_ideas = [idea for idea in ideas 
                          if datetime.fromisoformat(idea.get('created_at', '')).date() == datetime.now().date()]
            st.metric("Today's Ideas", len(recent_ideas))
    
    with tab2:
        # Score distribution
        scores = [idea.get('scores', {}).get('overall_score', 0) for idea in ideas]
        
        if scores:
            fig = px.histogram(
                x=scores,
                nbins=20,
                title="Score Distribution",
                labels={'x': 'Score', 'y': 'Count'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Score breakdown
            feasibility_scores = [idea.get('scores', {}).get('feasibility_score', 0) for idea in ideas]
            novelty_scores = [idea.get('scores', {}).get('novelty_score', 0) for idea in ideas]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=feasibility_scores,
                y=novelty_scores,
                mode='markers',
                text=[idea.get('title', 'Untitled') for idea in ideas],
                hovertemplate='<b>%{text}</b><br>Feasibility: %{x}<br>Novelty: %{y}<extra></extra>'
            ))
            fig.update_layout(
                title="Feasibility vs Novelty",
                xaxis_title="Feasibility Score",
                yaxis_title="Novelty Score"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Trends over time
        if len(ideas) > 1:
            dates = [datetime.fromisoformat(idea.get('created_at', '')) for idea in ideas]
            scores = [idea.get('scores', {}).get('overall_score', 0) for idea in ideas]
            
            df = pd.DataFrame({
                'Date': dates,
                'Score': scores
            })
            df = df.sort_values('Date')
            
            fig = px.line(
                df,
                x='Date',
                y='Score',
                title="Score Trends Over Time"
            )
            st.plotly_chart(fig, use_container_width=True)

def settings_page():
    """Settings page."""
    st.header("Settings")
    
    # API Configuration
    st.subheader("API Configuration")
    
    api_url = st.text_input(
        "API Base URL",
        value=API_BASE_URL,
        help="Base URL for the AI Startup Co-Founder API"
    )
    
    # Model Configuration
    st.subheader("Model Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        model_provider = st.selectbox(
            "LLM Provider",
            ["OpenAI", "Local", "Anthropic"]
        )
        
        model_name = st.selectbox(
            "Model Name",
            ["gpt-4", "gpt-3.5-turbo", "claude-3", "llama2"]
        )
    
    with col2:
        temperature = st.slider(
            "Temperature",
            min_value=0.1,
            max_value=1.0,
            value=0.7,
            step=0.1
        )
        
        max_tokens = st.number_input(
            "Max Tokens",
            min_value=100,
            max_value=4000,
            value=2000
        )
    
    # Vector Database Configuration
    st.subheader("Vector Database")
    
    vector_db_type = st.selectbox(
        "Vector Database Type",
        ["FAISS", "Pinecone", "Weaviate"]
    )
    
    if vector_db_type == "Pinecone":
        pinecone_api_key = st.text_input("Pinecone API Key", type="password")
        pinecone_environment = st.text_input("Pinecone Environment")
    
    # Save settings
    if st.button("Save Settings"):
        st.success("Settings saved successfully!")
        
        # Store settings in session state
        st.session_state.settings = {
            'api_url': api_url,
            'model_provider': model_provider,
            'model_name': model_name,
            'temperature': temperature,
            'max_tokens': max_tokens,
            'vector_db_type': vector_db_type
        }

def generate_ideas(topic: str, **kwargs) -> List[Dict[str, Any]]:
    """Generate ideas using the API."""
    try:
        # Mock implementation - replace with actual API call
        time.sleep(2)  # Simulate API call
        
        ideas = [
            {
                'id': '1',
                'title': f'AI-Powered {topic} Solution',
                'description': f'An intelligent solution for {topic} that leverages AI to provide personalized recommendations.',
                'problem': f'Current {topic} solutions lack personalization and intelligence.',
                'solution': f'Our AI-powered platform provides intelligent, personalized {topic} solutions.',
                'target_market': 'Small to medium businesses',
                'business_model': 'SaaS subscription',
                'scores': {
                    'overall_score': 0.85,
                    'feasibility_score': 0.8,
                    'novelty_score': 0.9,
                    'market_potential_score': 0.85
                },
                'created_at': datetime.now().isoformat()
            },
            {
                'id': '2',
                'title': f'Blockchain-Based {topic} Platform',
                'description': f'A decentralized platform for {topic} that ensures transparency and security.',
                'problem': f'Trust and transparency issues in {topic} industry.',
                'solution': f'Blockchain-based platform that provides transparent, secure {topic} solutions.',
                'target_market': 'Enterprise customers',
                'business_model': 'Transaction fees',
                'scores': {
                    'overall_score': 0.75,
                    'feasibility_score': 0.7,
                    'novelty_score': 0.8,
                    'market_potential_score': 0.75
                },
                'created_at': datetime.now().isoformat()
            }
        ]
        
        # Store ideas in session state
        if 'ideas' not in st.session_state:
            st.session_state.ideas = []
        st.session_state.ideas.extend(ideas)
        
        return ideas
        
    except Exception as e:
        st.error(f"Failed to generate ideas: {e}")
        return []

def process_file(file) -> Dict[str, Any]:
    """Process uploaded file."""
    try:
        # Mock file processing
        time.sleep(1)
        
        result = {
            'filename': file.name,
            'size': file.size,
            'type': file.type,
            'chunks': 15,
            'embeddings': 8,
            'extracted_text': 'Sample extracted text from the file...',
            'metadata': {
                'pages': 5,
                'language': 'en',
                'confidence': 0.85
            }
        }
        
        return result
        
    except Exception as e:
        st.error(f"Failed to process file: {e}")
        return None

def export_idea(idea: Dict[str, Any]):
    """Export idea to various formats."""
    st.success("Idea exported successfully!")
    # Implementation would export to PDF, PowerPoint, etc.

if __name__ == "__main__":
    main()
