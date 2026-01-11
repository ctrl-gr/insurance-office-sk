# Insurance Office Assistant with Semantic Kernel

An AI-powered insurance office management system built with Semantic Kernel and OpenAI. This application helps manage insurance policies, analyze policy conditions from PDF documents, and provides intelligent conversational assistance for insurance-related tasks.

## Features

### 📋 Insurance Policy Management

- **Add Insurance Policies**: Create new insurance policies with automatic conditions assignment based on policy type
- **List All Policies**: View all insurance policies with expiration dates and guarantees
- **Track Expirations**: Monitor upcoming policy expirations
- **Database Status**: Check MongoDB connection and policy count
- **Smart Conditions Assignment**: Automatically retrieves policy conditions from database based on category (case-insensitive)

### 📄 Policy Conditions Analysis

- **Database-driven Document Loading**: Automatically loads policy conditions PDFs from database storage by category
- **Smart Search**: Search through policy conditions using natural language queries
- **Chunk-based Retrieval**: Efficient text chunking for better context understanding
- **Policy Conditions Analysis**: Extract and analyze specific clauses from insurance conditions

## Prerequisites

- Python 3.8+
- MongoDB database
- OpenAI API key
- Virtual environment (recommended)

## Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd insurance-office-sk
   ```

2. **Create and activate virtual environment**

   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\Activate.ps1
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install semantic-kernel pymongo python-dotenv PyPDF2 openai
   ```

4. **Configure environment variables**

   Create a `.env` file in the root directory with the following variables:

   ```env
   OPENAI_API_KEY=your_openai_api_key
   OPENAI_MODEL=gpt-4
   MONGODB_CONNECTION_STRING=your_mongodb_connection_string
   DB_NAME=insurance_db
   COLLECTIONS=insurances
   ```

## Database Setup

### MongoDB Collections

The application uses two MongoDB collections:

1. **insurances** (configurable via `COLLECTIONS` env variable)

   - Stores insurance policy records

   ```json
   {
     "policy_holder": "John Doe",
     "policy_type": "Auto",
     "provider": "Insurance Company",
     "guarantees": "Comprehensive coverage",
     "expiration_date": ISODate("2026-12-31"),
     "conditions": "CarSafe26.1",
     "created_at": ISODate("2026-01-11")
   }
   ```

2. **policy_conditions**
   - Stores policy conditions templates by category
   ```json
   {
     "id": 1,
     "category": "Car",
     "name_conditions": "CarSafe26.1",
     "storage_url": "path/to/conditions.pdf"
   }
   ```

### Sample Policy Conditions Setup

Insert policy conditions into MongoDB:

```javascript
db.policy_conditions.insertMany([
  {
    id: 1,
    category: "Car",
    name_conditions: "CarSafe26.1",
    storage_url: "conditions/car_safe_26_1.pdf",
  },
  {
    id: 2,
    category: "Injuries",
    name_conditions: "BeSafe26.3",
    storage_url: "conditions/be_safe_26_3.pdf",
  },
  {
    id: 3,
    category: "Home",
    name_conditions: "HomeSafe26.2",
    storage_url: "conditions/home_safe_26_2.pdf",
  },
]);
```

## Usage

1. **Start the application**

   ```bash
   python app.py
   ```

2. **Interact with the assistant**

   The application provides a conversational interface. You can:

   - **Add a new insurance policy:**

     ```
     User > Add a new auto insurance for Mario Rossi with Allianz, comprehensive coverage, expiring on 2026-12-31
     ```

   - **List all policies:**

     ```
     User > Show me all insurance policies
     ```

   - **Check next expiration:**

     ```
     User > When is the next policy expiring?
     ```

   - **Load and analyze policy conditions:**

     ```
     User > Load the conditions for Car policies
     User > What are the coverage limits for property damage?
     User > Search for deductible information in the conditions
     ```

   - **Check database status:**
     ```
     User > What's the database status?
     ```

3. **Exit the application**
   ```
   User > exit
   ```

## Project Structure

```
insurance-office-sk/
├── app.py                          # Main application entry point
├── plugins/
│   ├── insurance_position_plugin.py # Insurance policy management
│   └── conditions_plugin.py         # PDF document analysis
├── .env                            # Environment configuration
├── .gitignore                      # Git ignore rules
└── README.md                       # This file
```

## Plugins

### Insurance Position Plugin

Manages insurance policies with the following functions:

- `get_next_policy_exp`: Get the next expiring policy
- `list_all_insurances`: List all policies with details
- `add_insurance`: Add a new insurance policy
- `get_db_status`: Check database connection and stats

### Conditions Plugin

Analyzes policy conditions documents retrieved from database storage:

- `load_conditions_by_category`: Automatically loads policy conditions PDF from database storage based on category (e.g., Car, Home, Injuries)
- `search_pdf_content`: Search for specific content in loaded conditions document
- `get_pdf_info`: Get information about the loaded conditions document

## How It Works

1. **Semantic Kernel Integration**: Uses Microsoft's Semantic Kernel to orchestrate AI functions
2. **Function Calling**: OpenAI automatically selects and executes the appropriate plugin functions based on user requests
3. **MongoDB Integration**: Stores and retrieves insurance data and policy conditions efficiently
4. **Smart Conditions Matching**: Uses case-insensitive regex matching to find policy conditions regardless of capitalization
5. **Database-driven PDF Retrieval**: Automatically retrieves policy conditions PDFs from storage paths defined in the database
6. **PDF Analysis**: Chunks PDF documents for efficient searching and retrieval of specific information

## Environment Variables Reference

| Variable                    | Description                  | Example                     |
| --------------------------- | ---------------------------- | --------------------------- |
| `OPENAI_API_KEY`            | Your OpenAI API key          | `sk-...`                    |
| `OPENAI_MODEL`              | OpenAI model to use          | `gpt-4` or `gpt-5.2`        |
| `MONGODB_CONNECTION_STRING` | MongoDB connection string    | `mongodb://localhost:27017` |
| `DB_NAME`                   | Database name                | `insurance_db`              |
| `COLLECTIONS`               | Collection name for policies | `insurances`                |

## Troubleshooting

- **Database connection failed**: Check your MongoDB connection string and ensure MongoDB is running
- **OpenAI API errors**: Verify your API key is valid and has sufficient credits
- **Conditions PDF not loading**: Ensure the `storage_url` in the `policy_conditions` collection points to a valid, accessible PDF file path
- **Conditions not saving**: Make sure the `policy_conditions` collection exists and contains matching categories
- **Category not found**: Check that the category name in the database matches your request (matching is case-insensitive)

## Future Enhancements

- Web interface for easier interaction
- Advanced reporting and analytics
- Document generation for policy renewals
- Integration with insurance provider APIs

## License

This project is for educational and portfolio purposes.

## Author

Developed using Microsoft Semantic Kernel and OpenAI GPT models.
