import streamlit as st
import requests
import xml.etree.ElementTree as ET
from openai import OpenAI
import time

# Page configuration
st.set_page_config(
    page_title="Research Paper Summarizer",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Academic Theme CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: transparent;
    }
    
    /* Main Container */
    .main-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        margin: 2rem auto;
        max-width: 1400px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        overflow: hidden;
    }
    
    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 50%, #581c87 100%);
        color: white;
        text-align: center;
        padding: 3rem 2rem;
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
        opacity: 0.3;
    }
    
    .hero-content {
        position: relative;
        z-index: 2;
        max-width: 800px;
        margin: 0 auto;
    }
    
    .hero-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        color: rgba(255, 255, 255, 0.9);
        padding: 0.5rem 1.5rem;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(10px);
    }
    
    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3.5rem;
        font-weight: 700;
        line-height: 1.1;
        margin-bottom: 1.5rem;
        background: linear-gradient(135deg, #ffffff 0%, #e0e7ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        line-height: 1.6;
        color: rgba(255, 255, 255, 0.9);
        font-weight: 400;
        max-width: 600px;
        margin: 0 auto;
    }
    
    /* Search Section */
    .search-section {
        background: white;
        padding: 3rem 2rem 2rem 2rem;
    }
    
    .search-container {
        max-width: 800px;
        margin: 0 auto;
    }
    
    .search-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .search-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.8rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    
    .search-description {
        color: #64748b;
        font-size: 1rem;
        line-height: 1.5;
    }
    
    .search-form {
        display: flex;
        gap: 1rem;
        margin-top: 2rem;
        background: #f8fafc;
        padding: 1rem;
        border-radius: 16px;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .search-form:focus-within {
        border-color: #3b82f6;
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
    }
    
    .search-input-wrapper {
        flex: 1;
    }
    
    .search-button-wrapper {
        flex-shrink: 0;
    }
    
    /* Paper Cards */
    .papers-section {
        background: #f8fafc;
        padding: 2rem;
        min-height: 200px;
    }
    
    .paper-card {
        background: white;
        border-radius: 20px;
        padding: 2.5rem;
        margin: 2rem auto;
        max-width: 1200px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .paper-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
    }
    
    .paper-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.12);
    }
    
    .paper-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
        padding-bottom: 1.5rem;
        border-bottom: 1px solid #f1f5f9;
    }
    
    .paper-number {
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 12px;
        font-size: 0.9rem;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    .paper-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.6rem;
        font-weight: 600;
        color: #1e293b;
        line-height: 1.4;
        margin-bottom: 1.5rem;
    }
    
    .paper-meta {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.75rem;
        color: #64748b;
        font-size: 0.95rem;
    }
    
    .paper-meta-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 24px;
        height: 24px;
        background: #f1f5f9;
        border-radius: 6px;
        font-size: 0.8rem;
    }
    
    .paper-meta strong {
        color: #374151;
        font-weight: 600;
    }
    
    /* Content Grid */
    .content-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2rem;
        margin-top: 2rem;
    }
    
    .content-box {
        background: #f8fafc;
        border-radius: 16px;
        padding: 2rem;
        border: 1px solid #e2e8f0;
        position: relative;
        transition: all 0.3s ease;
    }
    
    .content-box:hover {
        border-color: #cbd5e1;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    
    .abstract-box {
        border-left: 4px solid #3b82f6;
    }
    
    .summary-box {
        border-left: 4px solid #8b5cf6;
    }
    
    .warning-box {
        border-left: 4px solid #f59e0b;
        background: #fffbeb;
    }
    
    .content-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 1.5rem;
        font-size: 1.1rem;
    }
    
    .content-text {
        color: #475569;
        line-height: 1.7;
        font-size: 0.95rem;
        max-height: 300px;
        overflow-y: auto;
        padding-right: 0.5rem;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.875rem 2rem !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        height: 52px !important;
        box-shadow: 0 4px 16px rgba(59, 130, 246, 0.3) !important;
        cursor: pointer !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.4) !important;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input {
        background: white !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 12px !important;
        color: #1e293b !important;
        font-family: 'Inter', sans-serif !important;
        height: 52px !important;
        font-size: 1rem !important;
        padding: 0 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1) !important;
        outline: none !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #94a3b8 !important;
        font-weight: 400 !important;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #1e293b 0%, #334155 100%) !important;
        color: white !important;
    }
    
    .css-1d391kg .stMarkdown {
        color: white !important;
    }
    
    .css-1d391kg .stSelectbox label,
    .css-1d391kg .stTextInput label,
    .css-1d391kg .stTextArea label,
    .css-1d391kg .stSlider label {
        color: #e2e8f0 !important;
        font-weight: 500 !important;
    }
    
    /* Status Messages */
    .stSuccess {
        background: linear-gradient(135deg, #10b981, #059669) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        font-weight: 500 !important;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #f59e0b, #d97706) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        font-weight: 500 !important;
    }
    
    .stError {
        background: linear-gradient(135deg, #ef4444, #dc2626) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        font-weight: 500 !important;
    }
    
    /* Loading Spinner */
    .stSpinner {
        color: #3b82f6 !important;
    }
    
    /* Scrollbar */
    .content-text::-webkit-scrollbar {
        width: 8px;
    }
    
    .content-text::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 4px;
    }
    
    .content-text::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 4px;
    }
    
    .content-text::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
    
    /* Empty State */
    .empty-state {
        text-align: center;
        padding: 3rem 2rem;
        color: #64748b;
        background: white;
        border-radius: 20px;
        margin: 2rem auto;
        max-width: 600px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
    }
    
    .empty-state-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        opacity: 0.6;
    }
    
    .empty-state-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.5rem;
        font-weight: 600;
        color: #475569;
        margin-bottom: 0.5rem;
    }
    
    .empty-state-description {
        font-size: 1rem;
        line-height: 1.6;
        max-width: 400px;
        margin: 0 auto;
    }
    
    /* Results container */
    .results-container {
        background: #f8fafc;
        min-height: auto;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.5rem;
        }
        
        .content-grid {
            grid-template-columns: 1fr;
            gap: 1.5rem;
        }
        
        .search-form {
            flex-direction: column;
        }
        
        .main-container {
            margin: 1rem;
            border-radius: 16px;
        }
        
        .paper-card {
            margin: 1rem auto;
            padding: 1.5rem;
        }
        
        .hero-section {
            padding: 2rem 1rem;
        }
        
        .search-section {
            padding: 2rem 1rem 1.5rem 1rem;
        }
        
        .papers-section {
            padding: 1.5rem 1rem;
        }
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .paper-card {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* Hide Streamlit default elements */
    .stApp > header {
        display: none;
    }
    
    .stApp > div[data-testid="stDecoration"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# Main Container Start
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="hero-section">
    <div class="hero-content">
        <div class="hero-badge">✨ AI-Powered Research Assistant</div>
        <h1 class="hero-title">Research Paper Summarizer</h1>
        <p class="hero-subtitle">Transform complex academic research into clear, actionable insights using advanced AI technology. Discover, analyze, and understand scientific literature more efficiently than ever before.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar Configuration
st.sidebar.markdown("### ⚙️ Configuration")

# API Key input
api_key = st.sidebar.text_input(
    "OpenRouter API Key", 
    type="password",
    help="Enter your OpenRouter API key for AI analysis"
)

# Model selection
model_options = [
    "google/gemma-2-9b-it",
    "anthropic/claude-3-haiku",
    "openai/gpt-3.5-turbo",
    "meta-llama/llama-3-8b-instruct"
]
selected_model = st.sidebar.selectbox("AI Model", model_options, index=1)

# Number of papers
max_results = st.sidebar.slider("Papers to Analyze", 1, 10, 3)

# Custom instructions
instruction_prompt = st.sidebar.text_area(
    "Analysis Instructions",
    value="You are an expert research analyst. Provide a clear, comprehensive summary under 100 words highlighting key findings, methodology, and significance.",
    height=100
)

# Search Section
st.markdown("""
<div class="search-section">
    <div class="search-container">
        <div class="search-header">
            <h2 class="search-title">Search Research Papers</h2>
            <p class="search-description">Enter your research topic to discover and analyze relevant academic papers from arXiv</p>
        </div>
        <div class="search-form">
""", unsafe_allow_html=True)

col1, col2 = st.columns([4, 1])

with col1:
    topic = st.text_input(
        "",
        placeholder="Enter research topic (e.g., machine learning, quantum computing, biotechnology...)",
        label_visibility="collapsed"
    )

with col2:
    search_button = st.button("🔍 Search", type="primary")

st.markdown("""
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Functions
@st.cache_data(ttl=300)
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
        response = requests.get(base_url, params=params, timeout=15)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        papers = []
        for entry in root.findall('atom:entry', ns):
            title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
            authors = [author.find('atom:name', ns).text for author in entry.findall('atom:author', ns)]
            summary = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
            arxiv_id = entry.find('atom:id', ns).text
            
            # Extract publication date
            published = entry.find('atom:published', ns)
            pub_date = published.text[:10] if published is not None else "Unknown"
            
            papers.append({
                'title': title,
                'authors': authors,
                'summary': summary,
                'arxiv_id': arxiv_id,
                'published': pub_date
            })
        
        return papers
    except Exception as e:
        st.error(f"Error fetching papers: {str(e)}")
        return []

def summarize_paper(summary_text, instruction_prompt, api_key, model):
    """Summarize paper using AI"""
    if not api_key:
        return "Please provide an API key to generate summaries."
    
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        
        enhanced_prompt = f"""
        {instruction_prompt}
        
        Research Paper Abstract:
        {summary_text}
        
        Please provide a structured analysis covering:
        1. Main contribution and novelty
        2. Methodology used
        3. Key findings
        4. Potential impact
        """
        
        completion = client.chat.completions.create(
            model=model,
            messages=[{
                "role": "user",
                "content": enhanced_prompt
            }],
            temperature=0.7,
            max_tokens=500
        )
        
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error generating summary: {str(e)}"

# Results Container
results_container = st.container()

# Main Logic
if search_button and topic:
    if not api_key:
        st.warning("⚠️ Please enter your OpenRouter API key in the sidebar to generate AI summaries.")
    
    with st.spinner(f"🔍 Searching for papers on '{topic}'..."):
        time.sleep(1)
        papers = scrape_papers(topic, max_results)
    
    if papers:
        st.success(f"✅ Found {len(papers)} paper(s) matching your search!")
        
        # Papers Section
        st.markdown('<div class="results-container">', unsafe_allow_html=True)
        
        for i, paper in enumerate(papers, 1):
            # Paper Card
            st.markdown(f"""
            <div class="paper-card">
                <div class="paper-header">
                    <div>
                        <span style="color: #64748b; font-size: 0.9rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em;">Research Paper</span>
                    </div>
                    <div class="paper-number">#{i:02d}</div>
                </div>
                <h2 class="paper-title">{paper['title']}</h2>
                <div class="paper-meta">
                    <div class="paper-meta-icon">👥</div>
                    <strong>Authors:</strong> {', '.join(paper['authors'][:3])}{'...' if len(paper['authors']) > 3 else ''}
                </div>
                <div class="paper-meta">
                    <div class="paper-meta-icon">📅</div>
                    <strong>Published:</strong> {paper['published']}
                </div>
                <div class="paper-meta">
                    <div class="paper-meta-icon">🔗</div>
                    <strong>ArXiv ID:</strong> {paper['arxiv_id'].split('/')[-1]}
                </div>
            """, unsafe_allow_html=True)
            
            # Content Grid
            st.markdown('<div class="content-grid">', unsafe_allow_html=True)
            
            # Original Abstract
            st.markdown(f"""
            <div class="content-box abstract-box">
                <div class="content-header">
                    📄 Original Abstract
                </div>
                <div class="content-text">
                    {paper['summary']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # AI Summary
            if api_key:
                with st.spinner("🤖 Generating AI analysis..."):
                    summary = summarize_paper(
                        paper['summary'], 
                        instruction_prompt, 
                        api_key, 
                        selected_model
                    )
                
                st.markdown(f"""
                <div class="content-box summary-box">
                    <div class="content-header">
                        🤖 AI Analysis
                    </div>
                    <div class="content-text">
                        {summary}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="content-box warning-box">
                    <div class="content-header">
                        ⚠️ API Key Required
                    </div>
                    <div class="content-text">
                        <div style="text-align: center; padding: 2rem;">
                            <div style="font-size: 3rem; margin-bottom: 1rem; color: #f59e0b;">🔐</div>
                            <strong style="color: #374151; display: block; margin-bottom: 1rem;">API Key Required</strong>
                            <span style="color: #6b7280;">Please add your OpenRouter API key in the sidebar to generate AI-powered summaries and analysis.</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)  # Close content-grid
            st.markdown('</div>', unsafe_allow_html=True)  # Close paper-card
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close results-container
    
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">🔍</div>
            <div class="empty-state-title">No Papers Found</div>
            <div class="empty-state-description">We couldn't find any papers matching your search terms. Try using different keywords or broader search terms.</div>
        </div>
        """, unsafe_allow_html=True)

elif search_button and not topic:
    st.warning("⚠️ Please enter a research topic to search for.")

else:
    # Default empty state - only show when no search has been performed
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-icon">📚</div>
        <div class="empty-state-title">Ready to Explore Research</div>
        <div class="empty-state-description">Enter a research topic above to discover and analyze academic papers with AI-powered insights.</div>
    </div>
    """, unsafe_allow_html=True)

# Sidebar Instructions
st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 Quick Start")
st.sidebar.markdown("""
**1.** Add your OpenRouter API key above  
**2.** Choose your preferred AI model  
**3.** Enter a research topic  
**4.** Click search to analyze papers  
""")

st.sidebar.markdown("### ✨ Features")
st.sidebar.markdown("""
🔍 **Smart Search** - Advanced arXiv integration  
🤖 **AI Analysis** - Multiple model support  
⚡ **Fast Results** - Optimized performance  
📱 **Responsive** - Works on all devices  
🔒 **Secure** - Safe API key handling  
""")

st.sidebar.markdown("### 💡 Pro Tips")
st.sidebar.markdown("""
• Use specific keywords for better results  
• Try different AI models for varied insights  
• Adjust the number of papers to analyze  
• Customize analysis instructions  
""")

st.markdown('</div>', unsafe_allow_html=True)  # Close main-container
