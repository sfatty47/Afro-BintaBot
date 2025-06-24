import requests
import wikipedia
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import streamlit as st
import re
import time

# Configure Wikipedia for African content
wikipedia.set_lang("en")

def is_african_relevant(text, query):
    """Check if text is relevant to African topics"""
    # African keywords and context indicators
    african_keywords = [
        'africa', 'african', 'mali', 'ghana', 'songhai', 'ethiopia', 'kenya', 'nigeria',
        'south africa', 'egypt', 'morocco', 'tunisia', 'algeria', 'libya', 'sudan',
        'sundiata', 'mansa musa', 'timbuktu', 'griot', 'ubuntu', 'mandinka', 'yoruba',
        'zulu', 'swahili', 'hausa', 'fulani', 'igbo', 'ashanti', 'bambara', 'wolof',
        'empire', 'kingdom', 'west africa', 'east africa', 'north africa', 'southern africa',
        'sub-saharan', 'sahel', 'sahara', 'niger river', 'congo', 'nile', 'great zimbabwe',
        'benin', 'dahomey', 'yoruba', 'igbo', 'hausa', 'mandinka', 'bambara', 'wolof',
        'swahili coast', 'trans-saharan', 'gold trade', 'salt trade', 'oral tradition',
        'griot', 'storyteller', 'ancestral', 'traditional', 'indigenous', 'colonial',
        'independence', 'pan-african', 'african diaspora', 'african american'
    ]
    
    # Query-specific keywords
    query_lower = query.lower()
    if 'mansa musa' in query_lower:
        african_keywords.extend(['mansa', 'musa', 'mali empire', 'gold', 'pilgrimage', 'mecca'])
    elif 'sundiata' in query_lower:
        african_keywords.extend(['sundiata', 'keita', 'mali empire', 'lion king', 'mandinka'])
    elif 'mandinka' in query_lower or 'mandingo' in query_lower:
        african_keywords.extend(['mandinka', 'mandingo', 'language', 'culture', 'west africa'])
    elif 'ubuntu' in query_lower:
        african_keywords.extend(['ubuntu', 'philosophy', 'community', 'humanity', 'south africa'])
    elif 'griot' in query_lower:
        african_keywords.extend(['griot', 'storyteller', 'oral tradition', 'west africa'])
    
    text_lower = text.lower()
    relevance_score = sum(1 for keyword in african_keywords if keyword in text_lower)
    
    # Check for non-African indicators that might indicate irrelevant results
    non_african_indicators = [
        'american', 'united states', 'us', 'usa', 'canada', 'europe', 'european',
        'british', 'french', 'german', 'spanish', 'italian', 'dutch', 'portuguese',
        'hollywood', 'new york', 'los angeles', 'chicago', 'boston', 'philadelphia',
        'actor', 'actress', 'movie', 'film', 'television', 'tv show', 'celebrity',
        'rapper', 'singer', 'musician', 'artist', 'painter', 'illustrator'
    ]
    
    non_african_score = sum(1 for indicator in non_african_indicators if indicator in text_lower)
    
    # Return True if African relevance is high and non-African indicators are low
    return relevance_score >= 2 and non_african_score <= 1

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
        
        # Filter results for African relevance
        filtered_ddg_results = []
        for result in ddg_results:
            if is_african_relevant(result.get('body', ''), query):
                filtered_ddg_results.append(result)
        
        # Search Wikipedia for academic information
        try:
            wiki_results = wikipedia.search(search_query, results=max_results)
            # Filter Wikipedia results for African relevance
            filtered_wiki_results = []
            for wiki_title in wiki_results:
                try:
                    page = wikipedia.page(wiki_title)
                    if is_african_relevant(page.content[:1000], query):
                        filtered_wiki_results.append(wiki_title)
                except:
                    continue
        except:
            filtered_wiki_results = []
        
        return {
            'ddg_results': filtered_ddg_results,
            'wiki_results': filtered_wiki_results,
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
            
        # Get the most relevant page that's African-focused
        for wiki_title in search_results:
            try:
                page = wikipedia.page(wiki_title)
                if is_african_relevant(page.content[:1000], topic):
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
            except:
                continue
                
        return None
    except Exception as e:
        st.warning(f"Wikipedia error: {str(e)}")
        return None

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