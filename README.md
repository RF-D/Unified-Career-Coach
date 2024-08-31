# Unified Career Coach: AI-Powered Career Assistant 🚀

Unified Career Coach is an interactive web application that provides personalized career guidance and insights using advanced AI models. This tool helps users explore career options, analyze their skills, and get tailored advice for their professional development.

## Features

- **Mood Analysis**: Evaluates the user's current emotional state and its potential impact on career decisions.
- **Job Market Alignment**: Analyzes how well the user's profile aligns with various job categories.
- **Career Path Analysis**: Provides short-term and long-term career prospects based on the user's input.
- **Skill Development Plan**: Creates a personalized plan for skill acquisition and improvement.
- **Industry Forecast**: Predicts trends and developments in relevant industries.
- **Interactive Visualizations**: Presents data and insights through charts and graphs.
- **Follow-up Chat**: Allows users to ask additional questions based on the analysis.

## Key Components

### UnifiedApis Class

The UnifiedApis class is a core component of this project, providing a unified interface to interact with multiple AI models. This abstraction allows for seamless integration of different AI providers and models, enhancing the flexibility and capabilities of the Career Coach.

Key features of the UnifiedApis class:

- **Multi-Provider Support**: Integrates with OpenAI, Anthropic, and Google (via OpenRouter) AI models.
- **Asynchronous Operations**: Utilizes async/await for efficient API calls.
- **JSON Mode**: Supports structured output in JSON format for easier parsing.
- **Model Flexibility**: Allows specifying different models for each provider.


## Technologies Used

- **Frontend**: Streamlit
- **Backend**: Python
- **AI Models**: 
  - OpenAI's GPT-4
  - Anthropic's Claude
  - Google's Gemini Pro
- **Data Visualization**: Plotly
- **Data Handling**: Pandas

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/unified-career-coach.git
   cd unified-career-coach
   ```

2. Set up a virtual environment:

   Option A: Using Python's venv
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

   Option B: Using Conda
   ```
   conda create --name career-coach python=3.9
   conda activate career-coach
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your API keys:
   - Create a `.env` file in the root directory
   - Add your API keys:
     ```
     OPENAI_API_KEY=your_openai_api_key
     ANTHROPIC_API_KEY=your_anthropic_api_key
     OPENROUTER_API_KEY=your_openrouter_api_key
     ```

5. Run the application:
   ```
   streamlit run main.py
   ```

## Usage

1. Enter your current feelings or state of mind, and career goals in the first text area.
2. List your current skills in the second text area.
3. Click "Submit" to generate a comprehensive career analysis.
4. Explore the various sections of the analysis, including visualizations.
5. Use the sidebar chat to ask follow-up questions based on the analysis.

## Contributing

Contributions to improve Unified Career Coach are welcome.

