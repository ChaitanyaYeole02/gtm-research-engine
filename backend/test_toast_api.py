#!/usr/bin/env python3
"""
Test script to call the Toast API and search for job positions using TF-IDF matching.

This script fetches job listings from Toast's API and uses TF-IDF (Term Frequency-Inverse
Document Frequency) search to find positions related to a search term. TF-IDF is fast,
lightweight, and very effective for job matching.

Features:
- 📊 TF-IDF search: Fast, accurate job matching using keyword similarity
- 🎯 Similarity scoring: Shows how well each job matches your search
- ⚙️ Configurable thresholds: Filter by match quality
- ⚡ Lightning fast: Sub-second performance, no heavy dependencies

Usage:
    python test_toast_api.py [SEARCH_TERM] [THRESHOLD]
    
Examples:
    python test_toast_api.py "software engineer"
    python test_toast_api.py "data scientist" 0.4
    python test_toast_api.py "backend engineer" 0.2
"""

import json
import urllib.request
import urllib.error
import sys
import time
import re
from typing import List, Dict, Any, Tuple

print("⏳ Loading libraries...")
import_start = time.perf_counter()

# Import TF-IDF dependencies
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import_time = time.perf_counter() - import_start
print(f"✅ Libraries loaded in {import_time:.2f}s")
print("📊 Using TF-IDF search (fast & reliable)")

# Initialize TF-IDF vectorizer globally for efficiency
_tfidf_vectorizer = None

def get_tfidf_model():
    """Get or initialize the TF-IDF vectorizer."""
    global _tfidf_vectorizer
    if _tfidf_vectorizer is None:
        _tfidf_vectorizer = TfidfVectorizer(
            max_features=2000,           # More features for richer content
            stop_words='english',
            ngram_range=(1, 3),          # Include trigrams for better phrase matching
            lowercase=True,
            min_df=1,                    # Include rare terms (good for specialized roles)
            max_df=0.95,                 # Remove very common terms
            token_pattern=r'\b[a-zA-Z]+\b'  # Only alphabetic tokens
        )
    return _tfidf_vectorizer

def search_jobs(jobs: List[Dict], search_term: str, threshold: float = 0.2) -> Tuple[List[Tuple[Dict, float]], Dict[str, float]]:
    """
    TF-IDF based job search with similarity scoring.
    Returns list of (job, similarity_score) tuples sorted by relevance and timing info.
    
    Args:
        jobs: List of job dictionaries from the API
        search_term: The job role/title to search for
        threshold: Minimum similarity score (0.0 to 1.0)
        
    Returns:
        Tuple of (matches, timing_info) where:
        - matches: List of (job, similarity_score) tuples sorted by highest similarity first
        - timing_info: Dict with timing details for each step
    """
    timing = {}
    total_start = time.perf_counter()
    
    if not jobs:
        return [], {'total_time': 0.0}
    
    # Model loading time
    model_start = time.perf_counter()
    vectorizer = get_tfidf_model()
    timing['model_ready_time'] = time.perf_counter() - model_start
    
    matches = []
    
    # Prepare job texts for comparison (title + content for better matching)
    prep_start = time.perf_counter()
    job_texts = []
    for job in jobs:
        title = job.get('title', '')
        content = job.get('content', '')
        
        # Clean HTML tags from content if present
        content_clean = re.sub(r'<[^>]+>', ' ', content) if content else ''
        
        # Combine title and content (weight title higher by repeating it)
        combined_text = f"{title} {title} {content_clean}".strip()
        job_texts.append(combined_text)
    
    # Add search term to fit the vectorizer
    all_texts = job_texts + [search_term]
    timing['data_prep_time'] = time.perf_counter() - prep_start
    
    # Generate TF-IDF vectors
    embedding_start = time.perf_counter()
    tfidf_matrix = vectorizer.fit_transform(all_texts)
    search_vector = tfidf_matrix[-1]  # Last item is search term
    job_vectors = tfidf_matrix[:-1]   # All except last
    timing['vectorization_time'] = time.perf_counter() - embedding_start
    
    # Calculate TF-IDF similarities
    similarity_start = time.perf_counter()
    similarities = cosine_similarity(search_vector, job_vectors)[0]
    timing['similarity_time'] = time.perf_counter() - similarity_start
    
    # Filter and collect matches
    filter_start = time.perf_counter()
    for job, similarity in zip(jobs, similarities):
        if similarity >= threshold:
            matches.append((job, float(similarity)))
    
    # Sort by similarity score (descending)
    matches = sorted(matches, key=lambda x: x[1], reverse=True)
    timing['filter_sort_time'] = time.perf_counter() - filter_start
    
    timing['total_time'] = time.perf_counter() - total_start
    
    return matches, timing

def fetch_toast_jobs() -> Tuple[Dict[str, Any], float]:
    """
    Fetch job listings from the Toast API.
    
    Returns:
        Tuple of (API response data, fetch_time_seconds)
        
    Raises:
        urllib.error.URLError: If the API request fails
    """
    url = "https://boards-api.greenhouse.io/v1/boards/toast/jobs?content=true"
    
    try:
        print(f"📡 Fetching jobs from: {url}")
        start_time = time.perf_counter()
        
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        fetch_time = time.perf_counter() - start_time
        print(f"✅ Successfully fetched {len(data.get('jobs', []))} total jobs ({fetch_time:.2f}s)")
        return data, fetch_time
    except urllib.error.URLError as e:
        print(f"Error fetching data from API: {e}")
        raise
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        raise


def search_jobs_by_term(jobs_data: Dict[str, Any], search_term: str, threshold: float = 0.2) -> Tuple[List[Tuple[Dict[str, Any], float]], Dict[str, float]]:
    """
    Search job listings using TF-IDF matching for a specific term.
    
    Args:
        jobs_data: Dictionary containing the API response with job listings
        search_term: The term to search for in job titles
        threshold: Minimum similarity score (0.0 to 1.0)
        
    Returns:
        Tuple of (matches, timing_info) where:
        - matches: List of (job, similarity_score) tuples sorted by relevance
        - timing_info: Dict with timing details for each step
    """
    jobs = jobs_data.get('jobs', [])
    return search_jobs(jobs, search_term, threshold)


def display_job_summary(job: Dict[str, Any], similarity_score: float = None) -> None:
    """
    Display a formatted summary of a job listing.
    
    Args:
        job: Dictionary containing job information
        similarity_score: Optional similarity score for fuzzy search results
    """
    title = job.get('title', 'N/A')
    location = job.get('location', {}).get('name', 'N/A')
    job_id = job.get('id', 'N/A')
    requisition_id = job.get('requisition_id', 'N/A')
    updated_at = job.get('updated_at', 'N/A')
    url = job.get('absolute_url', 'N/A')
    
    score_display = f"\nSimilarity Score: {similarity_score:.2%}" if similarity_score is not None else ""
    
    print(f"""
{'='*60}
Title: {title}
Location: {location}
Job ID: {job_id}
Requisition ID: {requisition_id}
Last Updated: {updated_at}{score_display}
Apply URL: {url}
{'='*60}
    """.strip())


def display_performance_summary(api_time: float, search_timing: Dict[str, float], total_jobs: int):
    """Display performance metrics in a nice format."""
    print(f"\n⚡ Performance Summary:")
    print("=" * 80)
    print(f"   📡 API Fetch Time:      {api_time:.3f}s")
    print(f"   🔧 Model Ready Time:    {search_timing.get('model_ready_time', 0):.3f}s")
    print(f"   📝 Data Prep Time:      {search_timing.get('data_prep_time', 0):.3f}s")
    print(f"   🎯 Vectorization Time:  {search_timing.get('vectorization_time', 0):.3f}s")
    print(f"   🔢 Similarity Calc:     {search_timing.get('similarity_time', 0):.3f}s")
    print(f"   🔍 Filter & Sort:       {search_timing.get('filter_sort_time', 0):.3f}s")
    print(f"   ⏱️  Total Search Time:   {search_timing.get('total_time', 0):.3f}s")
    
    total_time = api_time + search_timing.get('total_time', 0)
    print(f"   🚀 Total Runtime:       {total_time:.3f}s")
    
    if total_jobs > 0:
        jobs_per_second = total_jobs / search_timing.get('total_time', 1)
        print(f"   📊 Processing Rate:     {jobs_per_second:.0f} jobs/second")

def main(search_term: str = "software engineer", threshold: float = 0.2):
    """
    Main function to execute the API test and display results.
    
    Args:
        search_term: The job title/role to search for (default: "software engineer")
        threshold: Minimum similarity score for matches (default: 0.2)
    """
    total_start_time = time.perf_counter()
    
    try:
        print(f"🔍 Searching for: '{search_term}' (threshold: {threshold:.1%})")
        print(f"🔧 Search method: 📊 TF-IDF")
        print("=" * 80)
        
        # Fetch jobs from Toast API
        jobs_data, api_time = fetch_toast_jobs()
        
        # Search for jobs using TF-IDF search
        job_matches, search_timing = search_jobs_by_term(jobs_data, search_term, threshold)
        
        print(f"\n🎯 Found {len(job_matches)} matching positions:")
        print("=" * 80)
        
        if job_matches:
            for i, (job, similarity_score) in enumerate(job_matches, 1):
                print(f"\n📋 Job #{i} (Match: {similarity_score:.2%}):")
                display_job_summary(job, similarity_score)
        else:
            print(f"No positions found matching '{search_term}' with threshold {threshold:.1%}")
            
        # Display some statistics
        total_jobs = len(jobs_data.get('jobs', []))
        total_meta = jobs_data.get('meta', {}).get('total', 'Unknown')
        
        print(f"\n📊 Results Summary:")
        print("=" * 80)
        print(f"   • Total jobs in response: {total_jobs}")
        print(f"   • Total jobs available (API meta): {total_meta}")
        print(f"   • Search matches: {len(job_matches)}")
        print(f"   • Match percentage: {(len(job_matches) / total_jobs * 100):.1f}%" if total_jobs > 0 else "   • Match percentage: 0.0%")
        
        if job_matches:
            avg_score = sum(score for _, score in job_matches) / len(job_matches)
            top_score = job_matches[0][1] if job_matches else 0
            print(f"   • Average similarity: {avg_score:.2%}")
            print(f"   • Top match score: {top_score:.2%}")
        
        # Display performance metrics
        display_performance_summary(api_time, search_timing, total_jobs)
        
        total_runtime = time.perf_counter() - total_start_time
        print(f"\n🏁 Total Program Runtime: {total_runtime:.3f}s")
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    # Parse command line arguments
    search_term = "software engineer"
    threshold = 0.2
    
    # Show usage if help requested
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        print("""
Usage: python test_toast_api.py [SEARCH_TERM] [THRESHOLD]

Arguments:
  SEARCH_TERM    Job title/role to search for (default: "software engineer")
  THRESHOLD      Minimum similarity score 0.0-1.0 (default: 0.2)

Examples:
  python test_toast_api.py "software engineer"
  python test_toast_api.py "data scientist" 0.4
  python test_toast_api.py "backend engineer" 0.2
  python test_toast_api.py "product manager" 0.3

TF-IDF Search Features:
  - 📊 Fast keyword-based matching using TF-IDF vectors
  - 🎯 Excellent for job title matching and role similarity
  - ⚡ Lightning fast performance (sub-second)
  - 📈 Similarity scoring for ranking results
  - 🔧 No heavy dependencies, works reliably everywhere
  - ⏱️ Performance monitoring with detailed timing breakdowns
        """.strip())
        sys.exit(0)
    
    # Parse remaining arguments
    if len(sys.argv) > 1:
        search_term = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            threshold = float(sys.argv[2])
            if not 0.0 <= threshold <= 1.0:
                print("❌ Threshold must be between 0.0 and 1.0")
                sys.exit(1)
        except ValueError:
            print("❌ Threshold must be a number between 0.0 and 1.0")
            sys.exit(1)
    
    exit(main(search_term, threshold))
