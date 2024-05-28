import os
import subprocess
from firecrawl import FirecrawlApp
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

search_client = FirecrawlApp(api_key=os.environ['FIRECRAWL_API_KEY'])
search_llm_client = OpenAI()

dev_tools = [
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write the given content in the given file. Use this to write the code in the file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path of the file to write the content in. Eg: components/main.tsx. Make sure give the full relative path."
                    },
                    "content": {
                        "type": "string",
                        "description": "The correct content or code to write in the file"
                    },
                },
                "required": ["file_path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "terminal",
            "description": "Terminal is the tool to execute commands in the terminal.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The command to execute"
                    },
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "google_search",
            "description": "Search Google for a given query, Use this for reference whem you have doubt in creating application or whatever.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query to search for"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_url",
            "description": "Returns the current url in live browser.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "refrech_page",
            "description": "Used to refresh the page in the live browser.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "take_screenshot",
            "description": "Used to take a screenshot of the current page in the browser.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_logs",
            "description": "Used to read the logs in the browser if there is any errors. You can solve them later.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_url",
            "description": "Opens the given url in the live browser.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to enter."
                    }
                },
                "required": ["url"]
            }
        }
    },
]


def write_in_file(file_path, content):
    try:
        with open(file_path, "w") as f:
            f.write(content)
        return "Wrote the content in the file " + file_path + " successfully."
    except Exception as e:
        return str(e)

def terminal(command):
    output = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
    return output

def google_search(query):
    search_result = search_client.search(query, {
        'pageOptions': {
            'onlyMainContent': True,
            'fetchPageContent': True
        },
        'searchOptions': {
            'limit': 4
        }
    })

    confined_result = ''
    for result in search_result:
        response = search_llm_client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": f"Here is the raw scrapped contents, try to remove only the unwanted contents in them and make it relevent for query: {query}\n\n{result['markdown'][:14000] if len(result['markdown']) > 14000 else result['markdown']}"
                    }
                ],
                model="gpt-3.5-turbo",
            )
        confined_result += response.choices[0].message.content + "\n\n\n"

    return confined_result