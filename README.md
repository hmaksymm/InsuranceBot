# Car Insurance Sales Telegram Bot

A Telegram bot that helps users purchase car insurance by processing their documents and providing AI-driven communication using Google's Gemini API.

## Features

- Document processing using Mindee API
- AI-powered conversations using Google's Gemini API (free tier)
- SQLite database for chat history and document storage
- Step-by-step insurance purchase workflow
- Error handling and data validation

## Prerequisites

- Python 3.8 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Mindee API Key (from [Mindee Platform](https://platform.mindee.com/))
- Google Gemini API Key (from [Google AI Studio](https://makersuite.google.com/app/apikey))

## Installation

1. Clone the repository or download the source code
2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your API keys:
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
MINDEE_API_KEY=your_mindee_api_key
GOOGLE_GEMINI_API_KEY=your_gemini_api_key
INSURANCE_PRICE_USD=100
MINDEE_ENDPOINT=https://api.mindee.net/v1/products/mindee/driver_license/v1/predict
```

## Usage

1. Start the bot:
```bash
python main.py
```

2. Open your Telegram app and search for your bot using the username you set with BotFather

3. Start a conversation with `/start`

## Bot Workflow

1. **Start**: Bot introduces itself and explains its purpose
2. **Document Submission**: User submits photos of required documents
3. **Data Processing**: Mindee API extracts information from documents
4. **Confirmation**: User verifies extracted data
5. **Price Quote**: Bot provides fixed price (100 USD)
6. **Completion**: Transaction confirmation

## Error Handling

- Document processing errors are handled gracefully
- Users can resubmit photos if data extraction fails
- API errors are caught and appropriate messages are shown
- Database operations are protected with try-catch blocks

## Project Structure

```
├── main.py                 # Bot entry point
├── InsuranceBot.py        # Main bot logic
├── gemini_client.py       # Gemini API integration
├── mindee_api.py          # Mindee API integration
├── database.py            # Database operations
├── config.py              # Configuration and environment variables
├── requirements.txt       # Python dependencies
└── .env                   # Environment variables (not in repo)
```

## Dependencies

- python-telegram-bot: Telegram Bot API wrapper
- mindee: Document processing API
- google-generativeai: Google's Gemini AI API
- python-dotenv: Environment variable management
- databases: Async database operations
- sqlalchemy: Database ORM
- aiosqlite: Async SQLite support

## Troubleshooting

1. **Mindee API Errors**:
   - Ensure your API key is correct
   - Check if you've reached the free tier limit
   - Try with a clearer photo if document recognition fails

2. **Gemini API Errors**:
   - Verify your API key is correct
   - Check your request quota
   - Ensure you're using the correct model name (gemini-pro)

3. **Database Issues**:
   - Check if the chat_history.db file has correct permissions
   - Delete the database file and restart if schema changes

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details.
