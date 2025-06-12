# main.py
import logging
from utils import youtube_api
from utils import llm_handler

# Configure basic logging for the application
# This will show logs from all modules (utils.youtube_api, utils.llm_handler, and main)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Get a logger for this module
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting YouTube Subscriber Report Generator...")

    # --- YouTube API Interaction ---
    youtube_api_key = "YOUR_PLACEHOLDER_YOUTUBE_API_KEY"
    if youtube_api_key == "YOUR_PLACEHOLDER_YOUTUBE_API_KEY":
        logger.warning("Using a placeholder YouTube API key. YouTube data will be placeholder data.")

    subscriber_updates = youtube_api.get_subscriber_updates(youtube_api_key)

    # --- Data Preparation for LLM ---
    logger.info("Processing fetched subscriber updates...")
    updates_text_block = ""
    if subscriber_updates:
        for update in subscriber_updates:
            channel_name = update.get('channel_name', 'N/A')
            update_title = update.get('update_title', 'N/A')
            update_type = update.get('type', 'N/A')
            update_line = f"- Channel: {channel_name}, Title: {update_title} (Type: {update_type})"
            # Still print this to console for now as it's part of the "raw" output before summary
            print(update_line)
            updates_text_block += update_line + "\n"

    if not updates_text_block.strip():
        updates_text_block = "No new updates were found from your subscriptions to summarize."
        logger.info("No textual content generated from updates. LLM will receive a default message.")
        print(updates_text_block) # Also print this status to console

    # --- LLM Interaction ---
    llm_api_key = "YOUR_PLACEHOLDER_LLM_API_KEY"
    if llm_api_key == "YOUR_PLACEHOLDER_LLM_API_KEY":
        logger.warning("Using a placeholder LLM API key. Summary will be a placeholder.")

    summary = llm_handler.summarize_text_with_llm(updates_text_block, llm_api_key)

    # --- Presenting the Summary ---
    # Using print for the final report is fine.
    print("\n---Generated Report Summary---")
    print(summary if summary else "Failed to generate summary or no summary was returned.")
    print("---End of Report---")

    logger.info("Report generation process complete.")

if __name__ == "__main__":
    main()
