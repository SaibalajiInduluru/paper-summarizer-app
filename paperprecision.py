import streamlit as st
import requests
import xml.etree.ElementTree as ET
from openai import OpenAI
import time

# Page configuration
st.set_page_config(
    page_title="Research Paper Summarizer",
    page_icon="📚",
    layout="wide"
)

# Title and description
st.markdown("<h1 style='text-align: center;'>📚 Research Papers Summarizer</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Search for research papers on arXiv and get AI-powered summaries!</p>", unsafe_allow_html=True)

# Sidebar for configuration
st.sidebar.header("Configuration")

# API Key input (with security warning)
api_key = st.sidebar.text_input(
    "OpenRouter API Key", 
    type="password",
    help="Enter your OpenRouter API key. Note: Never share your API keys publicly!"
)

# Model selection
model_options = [
    "google/gemma-2-9b-it",
    "anthropic/claude-3-haiku",
    "openai/gpt-3.5-turbo",
    "meta-llama/llama-3-8b-instruct"
]
selected_model = st.sidebar.selectbox("Select AI Model", model_options)

# Number of papers to fetch
max_results = st.sidebar.slider("Number of papers to summarize", 1, 10, 3)

# Custom instruction prompt
instruction_prompt = st.sidebar.text_area(
    "Summary Instructions",
    value="You are an expert summarizer and I want you to understand the content and summarize under 100 words.",
    height=100
)

# Main interface
col1, col2 = st.columns([2, 1])

with col1:
    topic = st.text_input(
        "Research Topic", 
        placeholder="e.g., Machine learning, Quantum computing, Computer vision...",
        help="Enter the research topic you want to search for"
    )

with col2:
    st.write("")  # Spacing
    search_button = st.button("🔍 Search & Summarize", type="primary")

# Functions
@st.cache_data(ttl=300)  # Cache for 5 minutes
def scrape_papers(topic, max_results=1):
    """Scrape papers from arXiv"""
    base_url = "http://export.arxiv.org/api/query"
    params = {
        'search_query': f'all:{topic}',
        'start': 0,
        'max_results': max_results,
        'sortBy': 'relevance',
        'sortOrder': 'descending'
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        papers = []
        for entry in root.findall('atom:entry', ns):
            title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
            authors = [author.find('atom:name', ns).text for author in entry.findall('atom:author', ns)]
            summary = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
            
            # Get arXiv link
            arxiv_id = entry.find('atom:id', ns).text
            
            papers.append({
                'title': title,
                'authors': authors,
                'summary': summary,
                'arxiv_id': arxiv_id
            })
        
        return papers
    except Exception as e:
        st.error(f"Error fetching papers: {str(e)}")
        return []

def summarize_paper(summary_text, instruction_prompt, api_key, model):
    """Summarize paper using OpenAI API"""
    if not api_key:
        return "⚠️ Please provide an API key to generate summaries."
    
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        
        combined_prompt = instruction_prompt + "\n\nContent to summarize:\n" + summary_text
        
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": combined_prompt
                }
            ]
        )
        
        return completion.choices[0].message.content
    except Exception as e:
        return f"❌ Error generating summary: {str(e)}"

# Main logic
if search_button and topic:
    if not api_key:
        st.warning("⚠️ Please enter your OpenRouter API key in the sidebar to generate summaries.")
    
    with st.spinner(f"Searching for papers on '{topic}'..."):
        papers = scrape_papers(topic, max_results)
    
    if papers:
        st.success(f"Found {len(papers)} paper(s)!")
        
        for i, paper in enumerate(papers, 1):
            # Modern card-style container
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 20px; border-radius: 15px; margin: 20px 0; box-shadow: 0 8px 32px rgba(0,0,0,0.1);'>
                <h2 style='color: white; margin-bottom: 10px; font-size: 1.5em;'>📄 Paper {i}</h2>
                <h3 style='color: #f0f0f0; margin-bottom: 15px; font-weight: 400; line-height: 1.4;'>{paper['title']}</h3>
                <div style='display: flex; gap: 20px; margin-bottom: 10px;'>
                    <div style='color: #e0e0e0;'><strong>👥 Authors:</strong> {', '.join(paper['authors'])}</div>
                </div>
                <div style='color: #e0e0e0;'><strong>🔗 ArXiv ID:</strong> {paper['arxiv_id']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Create two columns with modern styling
            col1, col2 = st.columns([1, 1], gap="large")
            
            with col1:
                # Original Abstract Box
                original_content = f"""
                <div style='background: #f8f9ff; border-left: 5px solid #4f46e5; 
                           padding: 25px; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.05); height: 400px; overflow-y: auto;'>
                    <div style='display: flex; align-items: center; margin-bottom: 15px;'>
                        <span style='font-size: 1.5em; margin-right: 10px;'>📋</span>
                        <h3 style='color: #1e293b; margin: 0; font-size: 1.3em;'>Original Abstract</h3>
                    </div>
                    <div style='color: #475569; line-height: 1.6; font-size: 0.95em;'>
                        {paper['summary']}
                    </div>
                </div>
                """
                st.markdown(original_content, unsafe_allow_html=True)
            
            with col2:
                # AI Summary Box
                if api_key:
                    with st.spinner("🔄 Generating AI summary..."):
                        summary = summarize_paper(
                            paper['summary'], 
                            instruction_prompt, 
                            api_key, 
                            selected_model
                        )
                    
                    ai_content = f"""
                    <div style='background: #f0fdf4; border-left: 5px solid #22c55e; 
                               padding: 25px; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.05); height: 400px; overflow-y: auto;'>
                        <div style='display: flex; align-items: center; margin-bottom: 15px;'>
                            <span style='font-size: 1.5em; margin-right: 10px;'>🤖</span>
                            <h3 style='color: #065f46; margin: 0; font-size: 1.3em;'>AI Generated Summary</h3>
                        </div>
                        <div style='color: #047857; line-height: 1.6; font-size: 0.95em;'>
                            {summary}
                        </div>
                    </div>
                    """
                    st.markdown(ai_content, unsafe_allow_html=True)
                else:
                    no_api_content = """
                    <div style='background: #f0fdf4; border-left: 5px solid #22c55e; 
                               padding: 25px; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.05); height: 400px; overflow-y: auto;'>
                        <div style='display: flex; align-items: center; margin-bottom: 15px;'>
                            <span style='font-size: 1.5em; margin-right: 10px;'>🤖</span>
                            <h3 style='color: #065f46; margin: 0; font-size: 1.3em;'>AI Generated Summary</h3>
                        </div>
                        <div style='display: flex; align-items: center; justify-content: center; height: 60%; color: #047857;'>
                            <div style='background: #fef3c7; color: #92400e; padding: 20px; border-radius: 12px; text-align: center; max-width: 300px;'>
                                <div style='font-size: 2em; margin-bottom: 10px;'>⚠️</div>
                                <strong>API Key Required</strong><br><br>
                                Please provide an API key in the sidebar to generate AI summaries.
                            </div>
                        </div>
                    </div>
                    """
                    st.markdown(no_api_content, unsafe_allow_html=True)
            
            # Modern separator
            st.markdown("""
            <div style='margin: 40px 0; display: flex; align-items: center;'>
                <div style='flex: 1; height: 2px; background: linear-gradient(to right, transparent, #e2e8f0, transparent);'></div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.error("No papers found for the given topic. Please try a different search term.")

elif search_button and not topic:
    st.warning("Please enter a research topic to search for.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>Built with Streamlit • Powered by arXiv API and OpenRouter</p>
        <p><strong>⚠️ Security Note:</strong> Never commit API keys to version control. Use environment variables in production.</p>
    </div>
    """, 
    unsafe_allow_html=True
)

# Instructions in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### How to use:")
st.sidebar.markdown("""
1. Enter your OpenRouter API key
2. Choose an AI model
3. Set the number of papers to fetch
4. Customize the summary instructions
5. Enter a research topic
6. Click 'Search & Summarize'
""")

st.sidebar.markdown("### Features:")
st.sidebar.markdown("""
- 🔍 Search arXiv papers
- 🤖 AI-powered summaries
- 📊 Multiple AI models
- 💾 Caching for faster results
- 🎨 Clean, responsive UI
""")