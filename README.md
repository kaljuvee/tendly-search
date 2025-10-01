# Tendly Search

AI-powered tender database search and analysis platform built with Streamlit, LangChain, and OpenAI.

## Features

- **Natural Language Search**: Query Estonian tender database using plain English or Estonian
- **Interactive Chat Interface**: Chat with the database using AI-powered SQL generation
- **Pre-built Search Options**: Quick access to common searches like construction tenders and regional queries
- **Database Schema Introspection**: Automatic discovery and analysis of database structure
- **Real-time Results**: Instant search results with formatted data display

## Architecture

### Core Components

1. **Database Utility (`utils/db_util.py`)**
   - SQLAlchemy-based database connection and schema introspection
   - Support for PostgreSQL databases
   - Automatic table discovery and metadata extraction

2. **Search Utility (`utils/search_util.py`)**
   - LangChain text-to-SQL agent implementation
   - Custom prompts optimized for Estonian tender data
   - Predefined search functions for common queries

3. **SQL Chat (`utils/sql_chat.py`)**
   - Interactive chat interface for database queries
   - Context-aware AI responses
   - Support for both natural language and direct SQL queries

4. **Streamlit Interface**
   - **Home.py**: Main search interface with quick search options
   - **pages/0_Chat.py**: Interactive chat page for conversational queries

### Database Schema

The application works with Estonian tender data including:

- **estonian_tenders**: Main tender information
- **estonian_tender_details**: Detailed tender specifications
- **companies**: Organization information
- **tender_matches**: AI-generated tender matches
- Additional supporting tables for documents, results, and user data

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL database access
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/kaljuvee/tendly-search.git
   cd tendly-search
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   
   Create a `.env` file with:
   ```env
   DB_URL=postgresql://username:password@host:port/database
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Run the application**
   ```bash
   streamlit run Home.py
   ```

## Usage

### Quick Search

The main interface provides pre-built search buttons for common queries:

- 🏗️ **Construction Tenders**: Find building and construction related tenders
- 📍 **Tenders in Harjumaa**: Regional search for Harju County
- 🕒 **Recent Tenders**: Most recently published opportunities
- 💰 **High Value Tenders**: Tenders with highest estimated values
- 💻 **IT Tenders**: Technology-related procurement
- ✅ **Active Tenders**: Currently open opportunities

### Natural Language Search

Enter queries in English or Estonian:

- "Show me construction tenders in Tallinn"
- "Ehitus hanked Harjumaal"
- "IT tenders with value over 50000 euros"
- "Recent government procurement"

### Chat Interface

Navigate to the Chat page for interactive conversations:

- Ask follow-up questions
- Get explanations of results
- Explore data relationships
- Execute custom SQL queries

## Sample Queries

### Estonian Language
- "Näita mulle ehitus hankeid"
- "Hanked Harjumaal"
- "Kõrge väärtusega hanked"

### English Language
- "Show me construction tenders"
- "Tenders in Harjumaa"
- "High value procurement opportunities"
- "IT related tenders from government"

## API Integration

The application uses:

- **LangChain**: For text-to-SQL conversion and AI agent orchestration
- **OpenAI GPT-4**: For natural language understanding and SQL generation
- **SQLAlchemy**: For database connectivity and ORM functionality
- **Streamlit**: For web interface and user interaction

## Development

### Project Structure

```
tendly-search/
├── Home.py                 # Main Streamlit application
├── pages/
│   └── 0_Chat.py          # Interactive chat interface
├── utils/
│   ├── __init__.py
│   ├── db_util.py         # Database utilities
│   ├── search_util.py     # Search functionality
│   └── sql_chat.py        # Chat interface logic
├── requirements.txt        # Python dependencies
├── .env                   # Environment configuration
└── README.md              # This file
```

### Testing

Run the test application to verify setup:

```bash
streamlit run test_app.py
```

This will check:
- Database connectivity
- Environment variables
- Import functionality
- Sample data access

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the test application for debugging
- Verify environment configuration

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [LangChain](https://langchain.com/)
- AI capabilities from [OpenAI](https://openai.com/)
- Database connectivity via [SQLAlchemy](https://sqlalchemy.org/)
