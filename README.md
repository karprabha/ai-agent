# AI Agent

This project implements an AI agent that can interact with a local file system and execute code to accomplish tasks. The agent is powered by Google's Gemini API and is designed to be a helpful coding assistant.

## How it Works

The agent operates by receiving a prompt from the user. This prompt is then passed to the Gemini model along with a set of available tools (functions) that the agent can use. The model generates a plan of function calls to achieve the user's goal. The agent then executes these function calls and returns the result.

The core of the agent is in `main.py`. This script handles the interaction with the Gemini API, defines the available functions, and manages the conversation flow.

### Available Functions

The agent has access to the following functions:

- `get_files_info`: Lists files in a specified directory.
- `get_file_content`: Reads the content of a file.
- `write_file`: Writes or overwrites content to a file.
- `run_python_file`: Executes a Python file.

For security reasons, all file system operations are constrained to the `calculator` directory.

## The `calculator` Project

This repository includes a sample project, `calculator`, which the AI agent is designed to work with. The `calculator` is a simple command-line calculator implementation in Python. The agent can be prompted to perform tasks within this project, such as adding new features, writing tests, or fixing bugs.

## Setup

1.  **Clone the repository:**

    ```bash
    git clone git@github.com:karprabha/ai-agent.git
    cd ai-agent
    ```

2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up your API key:**
    Create a `.env` file in the root of the project and add your Gemini API key:
    ```
    GEMINI_API_KEY=your_api_key
    ```

## Usage

You can run the agent by executing the `main.py` script with a prompt:

```bash
python main.py "Your prompt here"
```

For example, to ask the agent to list the files in the calculator project, you would run:

```bash
python main.py "List the files in the project"
```

You can also run the agent in verbose mode to see the function calls and their results:

```bash
python main.py "Your prompt here" --verbose
```
