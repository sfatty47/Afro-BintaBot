import requests
import wikipedia
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import streamlit as st
import re
import time
from typing import Dict, List, Optional

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

def search_wikipedia(query: str, max_results: int = 3) -> List[Dict]:
    """
    Search Wikipedia for African-related content with proper error handling
    """
    try:
        # Simple Wikipedia search using the API
        search_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": f"{query} Africa",
            "srlimit": max_results
        }
        
        response = requests.get(search_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        if "query" in data and "search" in data["query"]:
            for item in data["query"]["search"]:
                results.append({
                    "title": item["title"],
                    "snippet": item["snippet"],
                    "url": f"https://en.wikipedia.org/wiki/{item['title'].replace(' ', '_')}"
                })
        
        return results
        
    except Exception as e:
        st.warning(f"Could not search Wikipedia: {str(e)}")
        return []

def search_web(query: str, max_results: int = 3) -> List[Dict]:
    """
    Simple web search with proper error handling
    """
    try:
        # For now, return empty results to avoid external dependencies
        # In production, you could use DuckDuckGo, SerpAPI, or other search services
        return []
        
    except Exception as e:
        st.warning(f"Could not search web: {str(e)}")
        return []

def get_enhanced_african_knowledge(query, max_results=5):
    """
    Enhanced knowledge retrieval with better African content filtering and error handling
    """
    try:
        # Clean and enhance the query for better African-focused results
        enhanced_query = enhance_query_for_africa(query)
        
        # Get Wikipedia results with error handling
        wiki_results = search_wikipedia(enhanced_query, max_results)
        
        # Get web search results with error handling
        web_results = search_web(enhanced_query, max_results)
        
        # Filter and combine results
        filtered_results = {
            'wikipedia': filter_african_content(wiki_results),
            'web_results': filter_african_content(web_results)
        }
        
        return filtered_results
        
    except Exception as e:
        st.error(f"Error retrieving knowledge: {str(e)}")
        return None

def enhance_query_for_africa(query):
    """
    Enhance query to get better African-focused results
    """
    query_lower = query.lower()
    
    # Add African context for general topics
    if any(word in query_lower for word in ['slavery', 'slave', 'enslavement']):
        return f"African slavery history transatlantic slave trade"
    elif any(word in query_lower for word in ['culture', 'cultural']):
        return f"African culture traditions {query}"
    elif any(word in query_lower for word in ['history', 'historical']):
        return f"African history {query}"
    elif any(word in query_lower for word in ['story', 'stories', 'tale']):
        return f"African stories folktales {query}"
    elif any(word in query_lower for word in ['tribe', 'ethnic', 'people']):
        return f"African ethnic groups tribes {query}"
    elif any(word in query_lower for word in ['language', 'languages']):
        return f"African languages {query}"
    elif any(word in query_lower for word in ['music', 'dance', 'art']):
        return f"African music dance art {query}"
    elif any(word in query_lower for word in ['food', 'cuisine', 'dish']):
        return f"African food cuisine {query}"
    elif any(word in query_lower for word in ['religion', 'spiritual', 'belief']):
        return f"African religion spirituality {query}"
    elif any(word in query_lower for word in ['kingdom', 'empire', 'dynasty']):
        return f"African kingdoms empires {query}"
    elif any(word in query_lower for word in ['leader', 'king', 'queen', 'chief']):
        return f"African leaders kings queens {query}"
    else:
        # For general queries, add African context
        return f"Africa African {query}"

def format_knowledge_response(knowledge_data):
    """Format knowledge data into a readable response with reduced duplication"""
    if not knowledge_data:
        return None
    
    response_parts = []
    
    # Add Wikipedia content if available
    if knowledge_data.get('wikipedia'):
        wiki_content = knowledge_data['wikipedia']
        if isinstance(wiki_content, str) and len(wiki_content) > 50:
            # Clean and summarize Wikipedia content
            cleaned_wiki = clean_content(wiki_content)
            if cleaned_wiki:
                response_parts.append(f"**From our shared knowledge:** {cleaned_wiki}")
    
    # Add web results if available (avoid duplicates with Wikipedia)
    if knowledge_data.get('web_results'):
        web_results = knowledge_data['web_results']
        if isinstance(web_results, list) and web_results:
            # Take only the first 2 web results to avoid overwhelming
            for i, result in enumerate(web_results[:2]):
                if isinstance(result, dict):
                    title = result.get('title', '')
                    snippet = result.get('snippet', '')
                    
                    # Clean the snippet
                    cleaned_snippet = clean_content(snippet)
                    if cleaned_snippet and not is_duplicate_content(cleaned_snippet, response_parts):
                        response_parts.append(f"**Additional insight:** {cleaned_snippet}")
    
    if response_parts:
        return " ".join(response_parts)
    
    return None

def clean_content(content):
    """Clean and summarize content to reduce length and repetition"""
    if not content:
        return ""
    
    # Remove extra whitespace
    content = re.sub(r'\s+', ' ', content.strip())
    
    # Limit length to avoid overwhelming responses
    if len(content) > 300:
        # Try to find a good breaking point
        sentences = re.split(r'(?<=[.!?]) +', content)
        if len(sentences) > 2:
            content = " ".join(sentences[:2]) + "."
    
    return content

def is_duplicate_content(new_content, existing_parts):
    """Check if new content is too similar to existing parts"""
    if not existing_parts:
        return False
    
    new_words = set(new_content.lower().split())
    
    for part in existing_parts:
        existing_words = set(part.lower().split())
        # If more than 50% of words overlap, consider it duplicate
        if len(new_words.intersection(existing_words)) / len(new_words) > 0.5:
            return True
    
    return False

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

def filter_african_content(results):
    """
    Filter results to prioritize African content and remove irrelevant results
    """
    if not results:
        return []
    
    african_keywords = [
        'africa', 'african', 'west africa', 'east africa', 'south africa', 'north africa',
        'sub-saharan', 'sahel', 'sahara', 'niger', 'senegal', 'gambia', 'ghana', 'mali',
        'nigeria', 'kenya', 'ethiopia', 'somalia', 'sudan', 'egypt', 'morocco', 'tunisia',
        'algeria', 'libya', 'chad', 'cameroon', 'congo', 'zimbabwe', 'zambia', 'tanzania',
        'uganda', 'rwanda', 'burundi', 'angola', 'mozambique', 'namibia', 'botswana',
        'lesotho', 'eswatini', 'madagascar', 'mauritius', 'seychelles', 'comoros',
        'guinea', 'guinea-bissau', 'sierra leone', 'liberia', 'ivory coast', 'togo',
        'benin', 'burkina faso', 'niger', 'chad', 'central african republic',
        'equatorial guinea', 'gabon', 'republic of congo', 'democratic republic of congo',
        'south sudan', 'eritrea', 'djibouti', 'cape verde', 'sao tome and principe'
    ]
    
    # Keywords that indicate non-African content to exclude
    exclude_keywords = [
        'american', 'united states', 'usa', 'european', 'europe', 'asian', 'asia',
        'latin american', 'caribbean', 'australian', 'australia', 'canadian', 'canada'
    ]
    
    filtered_results = []
    
    for result in results:
        if isinstance(result, dict):
            title = result.get('title', '').lower()
            snippet = result.get('snippet', '').lower()
            content = f"{title} {snippet}"
        else:
            content = str(result).lower()
        
        # Check if content contains African keywords
        has_african_content = any(keyword in content for keyword in african_keywords)
        
        # Check if content should be excluded
        should_exclude = any(keyword in content for keyword in exclude_keywords)
        
        # Include if it has African content and shouldn't be excluded
        if has_african_content and not should_exclude:
            filtered_results.append(result)
    
    # If no African content found, return original results but limit to 3
    if not filtered_results and results:
        return results[:3]
    
    return filtered_results 