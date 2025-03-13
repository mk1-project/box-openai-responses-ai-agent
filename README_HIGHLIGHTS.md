# Box Agent with MK1 Highlights Integration

This extension to the Box Agent adds support for processing large files using the MK1 Highlights API. This solves the issue of hitting token limits when trying to process large documents directly with OpenAI.

## How It Works

1. **Text Chunking**: The system uses a sophisticated text chunking algorithm that preserves semantic units as much as possible. It applies increasingly fine-grained chunking strategies only when necessary:
   - First tries to split by paragraphs
   - Then by newlines
   - Then by sentences
   - Then by delimiters (commas, colons, etc.)
   - Then by spaces
   - Finally by character count if needed

2. **PDF Text Extraction**: For PDF files, the system extracts text using PyPDF2.

3. **Highlights API Integration**: The extracted and chunked text is sent to the MK1 Highlights API, which identifies the most relevant parts of the document based on the user's query.

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up your Highlights API key in the `.env` file:
   ```
   HIGHLIGHTS_API_KEY=your_highlights_api_key_here
   ```

3. Get your Highlights API key from [MK1 Highlights](https://console.highlights.mk1.ai).

## Usage

When dealing with large files, especially PDFs, the agent will automatically use the `get_highlights_from_file` tool instead of trying to process the entire document at once. This tool:

1. Extracts text from the file
2. Chunks the text into manageable pieces
3. Sends the chunks to the Highlights API with the user's query
4. Returns the most relevant highlights

## Example

```
User: Give me a summary of TSLA_2024-10k.pdf

Agent: I'll get the key highlights from Tesla's 2024 10-K report for you.

[Agent uses get_highlights_from_file tool]

Here are the key highlights from Tesla's 2024 10-K report:

1. Tesla reported total revenue of $96.8 billion for fiscal year 2024, a 19% increase from the previous year.
   Relevance: 0.92

2. The company delivered 1.8 million vehicles in 2024, representing a 38% year-over-year growth.
   Relevance: 0.89

...
```

## Architecture

- `box_agent/chunking/`: Contains the text chunking implementation
- `box_agent/pdf_extractor.py`: Handles PDF text extraction
- `box_agent/highlights_api.py`: Integrates with the MK1 Highlights API
- `box_agent/box.py`: Contains the Box tools, including the new `get_highlights_from_file` tool

## Troubleshooting

If you encounter issues with the Highlights API:

1. Verify your API key is correctly set in the `.env` file
2. Check the error logs in `error.log`
3. Ensure you have internet connectivity to reach the Highlights API
4. Verify the file exists and is accessible in Box