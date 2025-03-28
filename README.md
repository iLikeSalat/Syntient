# Syntient AI Assistant Platform

A modular, extensible AI assistant platform designed to be evolved into a SaaS tool. This platform enables the creation of AI assistants that can plan, execute tasks, use tools, and maintain memory across interactions.

## 🔧 Tech Stack

- **Python**: Core programming language
- **Flask**: Web API framework
- **OpenAI**: GPT-3.5 integration for natural language processing
- **LangChain** (optional): For memory and tool orchestration
- **dotenv**: For configuration management

## 🧱 System Architecture

```
syntient/
├── app.py                 # Flask API with /ask endpoint
├── core/                  # Core assistant functionality
│   ├── __init__.py
│   └── assistant.py       # Handles prompts and model responses
├── tools/                 # Modular agent tools
│   ├── __init__.py
│   ├── telegram/          # Telegram bot integration
│   ├── trading/           # Trading capabilities
│   └── file_parser/       # File parsing utilities
├── memory/                # Long-term memory system
│   └── __init__.py
├── .env                   # API keys and configuration (not in repo)
├── .env.example           # Example configuration template
└── requirements.txt       # Project dependencies
```

## 🔄 Agent Behavior

The Syntient AI Assistant:

- Accepts user tasks through natural language
- Plans and executes across multiple steps
- Can retry or debug itself when encountering issues
- Calls internal tools as needed for specialized tasks
- Maintains memory of past interactions
- Is designed with future autonomy loop logic in mind

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- OpenAI API key

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/iLikeSalat/Syntient.git
   cd Syntient
   ```

2. (Optional) Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

### Usage

1. Start the Flask API:
   ```
   python app.py
   ```

2. Send requests to the `/ask` endpoint:
   ```
   curl -X POST http://localhost:5000/ask \
     -H "Content-Type: application/json" \
     -d '{"message": "What can you help me with?", "user_id": "user123"}'
   ```

## 🧩 Extending the Platform

### Adding New Tools

1. Create a new directory in the `tools/` folder
2. Implement the tool interface
3. Register the tool in the tools registry

### Customizing Memory

The memory system is designed to be modular. You can:
- Replace the default memory implementation
- Add new memory types
- Customize retrieval mechanisms

## 📄 Documentation

- [PROGRESS.md](PROGRESS.md): Development log
- [TODO.md](todo.md): Upcoming features and tasks
- [DECISIONS.md](DECISIONS.md): Technical design choices and tradeoffs
- [ROADMAP.md](ROADMAP.md): Future development plans

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
