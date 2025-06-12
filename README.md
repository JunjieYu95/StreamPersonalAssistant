# YouTube Subscriber Activity Reporter

## Description

This project aims to connect to a YouTube account, fetch recent activity or video uploads from subscribed channels, and then use a Large Language Model (LLM) to generate a concise summary report of these updates.

**Note:** This project is currently under development. Core functionalities like YouTube API calls and LLM summarization are implemented with placeholders.

## Features

*   Fetches updates from YouTube subscriptions (currently placeholder data).
*   Summarizes the fetched updates using an LLM (currently placeholder summarization).
*   Basic logging of operations.

## Project Structure

```
.
├── main.py            # Main application script
├── utils/             # Utility modules
│   ├── __init__.py
│   ├── youtube_api.py # Handles YouTube API interactions (placeholder)
│   └── llm_handler.py # Handles LLM interactions (placeholder)
├── .gitignore         # Specifies intentionally untracked files
└── README.md          # This file
```

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Python Environment (Recommended):**
    It's recommended to use a virtual environment.
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install Dependencies:**
    *(Currently, no external libraries are required beyond standard Python. A `requirements.txt` file will be added as the project develops.)*

4.  **Configure API Keys:**
    The application requires API keys for both the YouTube Data API and an LLM service. Currently, these are set as placeholders directly in the code:
    *   `main.py`:
        *   `youtube_api_key`: Replace `"YOUR_PLACEHOLDER_YOUTUBE_API_KEY"` with your actual YouTube Data API key. You can obtain one from the [Google Cloud Console](https://console.cloud.google.com/).
        *   `llm_api_key`: Replace `"YOUR_PLACEHOLDER_LLM_API_KEY"` with the API key for your chosen LLM service.
    *   **Important Security Note:** For a real application, API keys should **not** be hardcoded. They should be loaded securely, for example, from environment variables or a dedicated, git-ignored configuration file. The TODOs in the code reflect this.

## How to Run

Once the setup (especially API keys, eventually) is complete, you can run the application using:

```bash
python3 main.py
```

The script will output logs to the console, the (placeholder) fetched updates, and finally, the (placeholder) summary report.

## TODO / Future Work

*   Implement actual YouTube Data API calls:
    *   OAuth 2.0 for user authentication to fetch their subscriptions.
    *   Fetch recent activities/uploads from subscriptions.
*   Select and integrate a specific LLM provider API.
*   Implement secure loading of API keys.
*   Add a `requirements.txt` file for dependencies (e.g., `google-api-python-client`, `requests`, or LLM-specific SDKs).
*   Enhance error handling and user feedback.
*   Develop a more structured output for the report.
*   Add unit tests.
