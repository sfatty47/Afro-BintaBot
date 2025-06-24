import requests
import wikipedia
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import streamlit as st
import re
import time

# Configure Wikipedia for African content
wikipedia.set_lang("en")

def search_african_knowledge(query, max_results=3):
    """Search for African knowledge from multiple online sources"""
    try:
        # Add "Africa" context to queries if not present
        if "africa" not in query.lower():
            search_query = f"{query} Africa"
        else:
            search_query = query
            
        # Search DuckDuckGo for recent information
        with DDGS() as ddgs:
            ddg_results = list(ddgs.text(search_query, max_results=max_results))
        
        # Search Wikipedia for academic information
        try:
            wiki_results = wikipedia.search(search_query, results=max_results)
        except:
            wiki_results = []
        
        return {
            'ddg_results': ddg_results,
            'wiki_results': wiki_results,
            'query': search_query
        }
    except Exception as e:
        st.warning(f"Search error: {str(e)}")
        return None

def get_wikipedia_content(topic):
    """Get detailed content from Wikipedia"""
    try:
        # Search for the topic
        search_results = wikipedia.search(topic, results=3)
        if not search_results:
            return None
            
        # Get the most relevant page
        page = wikipedia.page(search_results[0])
        
        # Extract and clean content
        content = page.content
        # Get first 1000 characters for summary
        summary = content[:1000] + "..." if len(content) > 1000 else content
        
        return {
            'title': page.title,
            'summary': summary,
            'url': page.url,
            'full_content': content
        }
    except Exception as e:
        st.warning(f"Wikipedia error: {str(e)}")
        return None

def extract_african_context(text):
    """Extract African-specific information from text"""
    # Keywords that indicate African content
    african_keywords = [
        'africa', 'african', 'mali', 'ghana', 'songhai', 'ethiopia', 'kenya', 'nigeria',
        'south africa', 'egypt', 'morocco', 'tunisia', 'algeria', 'libya', 'sudan',
        'sundiata', 'mansa musa', 'timbuktu', 'griot', 'ubuntu', 'mandinka', 'yoruba',
        'zulu', 'swahili', 'hausa', 'fulani', 'igbo', 'ashanti', 'bambara', 'wolof'
    ]
    
    # Check if text contains African keywords
    text_lower = text.lower()
    african_relevance = sum(1 for keyword in african_keywords if keyword in text_lower)
    
    return african_relevance > 0

def get_enhanced_african_knowledge(query):
    """Get enhanced knowledge about Africa from online sources"""
    try:
        # Search for information
        search_results = search_african_knowledge(query)
        if not search_results:
            return None
            
        # Get Wikipedia content if available
        wiki_content = None
        if search_results['wiki_results']:
            wiki_content = get_wikipedia_content(search_results['wiki_results'][0])
        
        # Process DuckDuckGo results
        ddg_info = []
        for result in search_results['ddg_results']:
            if extract_african_context(result.get('body', '')):
                ddg_info.append({
                    'title': result.get('title', ''),
                    'snippet': result.get('body', ''),
                    'link': result.get('link', '')
                })
        
        return {
            'wikipedia': wiki_content,
            'web_results': ddg_info,
            'query': search_results['query']
        }
        
    except Exception as e:
        st.error(f"Knowledge retrieval error: {str(e)}")
        return None

def format_knowledge_response(knowledge_data):
    """Format knowledge data into a readable response"""
    if not knowledge_data:
        return None
        
    response_parts = []
    
    # Add Wikipedia information
    if knowledge_data.get('wikipedia'):
        wiki = knowledge_data['wikipedia']
        response_parts.append(f"📚 **{wiki['title']}** (from Wikipedia)")
        response_parts.append(wiki['summary'])
        response_parts.append(f"Learn more: {wiki['url']}")
    
    # Add web search results
    if knowledge_data.get('web_results'):
        response_parts.append("\n🌐 **Additional Information:**")
        for i, result in enumerate(knowledge_data['web_results'][:2], 1):
            response_parts.append(f"{i}. **{result['title']}**")
            response_parts.append(f"   {result['snippet'][:200]}...")
    
    return "\n\n".join(response_parts)

# African knowledge sources
AFRICAN_KNOWLEDGE_SOURCES = {
    'history': [
        'African empires and kingdoms',
        'Trans-Saharan trade routes',
        'African civilizations',
        'Colonial history of Africa',
        'African independence movements'
    ],
    'culture': [
        'African traditional religions',
        'African music and dance',
        'African art and architecture',
        'African languages and literature',
        'African festivals and celebrations'
    ],
    'philosophy': [
        'Ubuntu philosophy',
        'African traditional wisdom',
        'African proverbs and sayings',
        'African moral values',
        'African community philosophy'
    ],
    'geography': [
        'African geography and climate',
        'African natural resources',
        'African wildlife and ecosystems',
        'African rivers and mountains',
        'African cities and landmarks'
    ]
}

def get_african_topic_suggestions(category=None):
    """Get suggestions for African topics to explore"""
    if category and category in AFRICAN_KNOWLEDGE_SOURCES:
        return AFRICAN_KNOWLEDGE_SOURCES[category]
    else:
        all_topics = []
        for topics in AFRICAN_KNOWLEDGE_SOURCES.values():
            all_topics.extend(topics)
        return all_topics 