import logging
import re
from typing import List, Dict, Optional
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

logger = logging.getLogger(__name__)

def extract_video_id(url: str) -> Optional[str]:
    """
    Extract video ID from various YouTube URL formats.
    
    Args:
        url: YouTube URL in various formats
        
    Returns:
        Video ID string or None if not found
    """
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/)([^&\n?#]+)',
        r'youtube\.com/watch\?.*v=([^&\n?#]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    # If it's already just a video ID
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
        return url
        
    return None

def get_video_transcript(video_url_or_id: str, languages: Optional[List[str]] = None) -> Dict:
    """
    Fetch transcript for a YouTube video.
    
    Args:
        video_url_or_id: YouTube URL or video ID
        languages: List of preferred languages (e.g., ['en', 'es', 'fr'])
                  If None, will try English first, then any available language
    
    Returns:
        Dictionary containing transcript data and metadata
    """
    logger.info(f"Attempting to fetch transcript for: {video_url_or_id}")
    
    # Extract video ID from URL
    video_id = extract_video_id(video_url_or_id)
    if not video_id:
        logger.error(f"Could not extract video ID from: {video_url_or_id}")
        return {
            "success": False,
            "error": "Invalid YouTube URL or video ID",
            "video_id": None,
            "transcript": None,
            "language": None
        }
    
    # Set default languages if none provided
    if languages is None:
        languages = ['en', 'en-US', 'en-GB']
    
    try:
        # Get available transcripts
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        logger.debug(f"Available transcripts for {video_id}: {[t.language_code for t in transcript_list]}")
        
        transcript = None
        used_language = None
        
        # Try to get transcript in preferred languages
        for lang in languages:
            try:
                transcript = transcript_list.find_transcript([lang])
                used_language = lang
                logger.info(f"Found transcript in language: {lang}")
                break
            except Exception as e:
                logger.debug(f"No transcript found for language {lang}: {e}")
                continue
        
        # If no preferred language found, try any available transcript
        if transcript is None:
            try:
                transcript = transcript_list.find_generated_transcript(['en'])
                used_language = 'en (auto-generated)'
                logger.info("Using auto-generated English transcript")
            except Exception:
                # Get any available transcript
                available_transcripts = list(transcript_list)
                if available_transcripts:
                    transcript = available_transcripts[0]
                    used_language = transcript.language_code
                    logger.info(f"Using available transcript in: {used_language}")
                else:
                    logger.error(f"No transcripts available for video {video_id}")
                    return {
                        "success": False,
                        "error": "No transcripts available for this video",
                        "video_id": video_id,
                        "transcript": None,
                        "language": None
                    }
        
        # Fetch the actual transcript data
        transcript_data = transcript.fetch()
        
        # Format transcript as plain text
        formatter = TextFormatter()
        formatted_text = formatter.format_transcript(transcript_data)
        
        # Also provide structured data with timestamps
        structured_transcript = []
        for entry in transcript_data:
            structured_transcript.append({
                "start": entry.get("start", 0),
                "duration": entry.get("duration", 0),
                "text": entry.get("text", "")
            })
        
        logger.info(f"Successfully fetched transcript for {video_id} (length: {len(formatted_text)} chars)")
        
        return {
            "success": True,
            "error": None,
            "video_id": video_id,
            "transcript": formatted_text,
            "structured_transcript": structured_transcript,
            "language": used_language,
            "length_chars": len(formatted_text),
            "length_entries": len(structured_transcript)
        }
        
    except Exception as e:
        logger.error(f"Error fetching transcript for {video_id}: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "video_id": video_id,
            "transcript": None,
            "language": None
        }

def get_multiple_video_transcripts(video_urls_or_ids: List[str], languages: Optional[List[str]] = None) -> List[Dict]:
    """
    Fetch transcripts for multiple YouTube videos.
    
    Args:
        video_urls_or_ids: List of YouTube URLs or video IDs
        languages: List of preferred languages
    
    Returns:
        List of transcript result dictionaries
    """
    logger.info(f"Fetching transcripts for {len(video_urls_or_ids)} videos")
    
    results = []
    for video in video_urls_or_ids:
        result = get_video_transcript(video, languages)
        results.append(result)
    
    successful_count = sum(1 for r in results if r["success"])
    logger.info(f"Successfully fetched {successful_count}/{len(video_urls_or_ids)} transcripts")
    
    return results

def summarize_transcript_metadata(transcript_result: Dict) -> str:
    """
    Create a summary of transcript metadata for logging/display.
    
    Args:
        transcript_result: Result dictionary from get_video_transcript
    
    Returns:
        Formatted summary string
    """
    if not transcript_result["success"]:
        return f"❌ Failed: {transcript_result['error']}"
    
    return (f"✅ Video ID: {transcript_result['video_id']} | "
            f"Language: {transcript_result['language']} | "
            f"Length: {transcript_result['length_chars']} chars | "
            f"Segments: {transcript_result['length_entries']}")

if __name__ == '__main__':
    # Test the transcript fetcher
    logging.basicConfig(level=logging.DEBUG)
    logger.info("Testing transcript_fetcher.py module...")
    
    # Test with a sample YouTube video (replace with actual video for testing)
    test_video = "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up
    
    result = get_video_transcript(test_video)
    print(f"\nResult: {summarize_transcript_metadata(result)}")
    
    if result["success"]:
        print(f"\nFirst 200 characters of transcript:")
        print(result["transcript"][:200] + "...")
    else:
        print(f"Error: {result['error']}")