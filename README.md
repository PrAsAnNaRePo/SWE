# SWE Agent

## Overview
This project consists of a set of Python scripts that work together to create an intelligent agent capable of helping Software Engineers (SWE) to create projects, integrate features into existing projects, and debug issues.

## Key Features
- **Project Creation**: Easily set up new projects with essential configurations.
- **Feature Integration**: Seamlessly add new features to existing projects.
- **Debugging**: Assist with identifying and resolving issues in the codebase.
- **Browser Interaction**: Perform browser operations like opening URLs, refreshing pages, and taking screenshots.
- **Development Tools**: Utilize various development tools like executing terminal commands, writing to files, and performing Google searches.

## Getting Started
### Prerequisites
- Python 3.x
- Chrome WebDriver
- Necessary libraries installed via `pip` (see `requirements.txt`)

### Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/PrAsAnNaRePo/SWE.git
   cd https://github.com/PrAsAnNaRePo/SWE.git
   ```

3. Set up environment variables:
   - Create a `.env` file in the root directory and add the necessary environment variables (`FIRECRAWL_API_KEY`, `OPENAI_API_KEY`).

### Running the Project
To start the agent, execute the following command:
```sh
python main.py
```
This will open a browser and start the interaction loop with the agent.

## Contributing
Feel free to submit issues or pull requests for improvements and bug fixes. All contributions are welcome!