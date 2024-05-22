import re
import subprocess
from openai import OpenAI
import json
import json
import questionary
from tools import dev_tools, terminal, write_in_file, google_search
from utils import *


class Agent:
    def __init__(
            self,
            sys_prompt: str,
            browser_driver = None,
            verbose: bool = False
    ) -> None:
        
        self.client = OpenAI()
        self.browser_driver = browser_driver
        self.verbose = verbose
        self.messages = [
            {
                "role": 'system',
                "content": sys_prompt
            }
        ]

    async def get_user_inp(self):
        user_input = await questionary.text(
                    "Enter your message:",
                    multiline=True,
                    qmark=">",
                ).ask_async()
        matches = re.findall(r'<img>(.*?)<img>', user_input)
        clear_line()
        if len(matches) > 0:
            return user_input.split("<img>")[0].strip(), matches[0]
        return user_input, None

    def display_token_usage(self, response):
        internal_monologue(f"\ntoken usage:\nprompt tokens: {response.usage.prompt_tokens}  |  generated_token: {response.usage.completion_tokens}  |  total tokens: {response.usage.total_tokens}\n\n")

    async def start(self):
        user_inp, img = await self.get_user_inp()
        if img is not None:
            self.messages.append(
                {
                    "role": 'user',
                    'content': [
                        {
                            "type": "text",
                            "text": user_inp
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encode_image(img)}"
                            }
                        }
                    ]
                }
            )
        else:
            self.messages.append(
                {
                    'role': 'user',
                    'content': user_inp
                }
            )

        response = self.client.chat.completions.create(
            messages=self.messages,
            model="gpt-4o",
            tools=dev_tools
        )
        self.messages.append(response.choices[0].message)
        if self.verbose:
            self.display_token_usage(response)

        while True:
            if response.choices[0].message.tool_calls:
                for tool_call in response.choices[0].message.tool_calls:
                    fn_name = tool_call.function.name
                    fn_args = json.loads(tool_call.function.arguments)
                    if fn_name == 'terminal':
                        inp = input(f"Executing terminal action for file '{fn_args.get('command')}' Y? ")
                        if 'Y' == inp or 'y' == inp:
                            try:
                                tool_response = terminal(fn_args.get('command'))
                                if tool_response.returncode == 0:
                                    tool_inp = "Output from the tool action:\n" + tool_response.stdout
                                else:
                                    tool_inp = "Output from the tool action:\n" + tool_response.stderr + "\nSeems like there is a problem try to fix it."
                            except subprocess.TimeoutExpired as e:
                                tool_inp = "Timed out after 20 seconds. Ask user to try or check what's wrong."
                            self.messages.append(
                                {
                                    "tool_call_id": tool_call.id,
                                    "role": "tool",
                                    "name": fn_name,
                                    "content": tool_inp,
                                }
                            )

                        else:
                            tool_inp = "User didn't allow you to use terminal. Check with user. Probably they want to say something."
                            self.messages.append(
                                {
                                    "tool_call_id": tool_call.id,
                                    "role": "tool",
                                    "name": fn_name,
                                    "content": tool_inp,
                                }
                            )

                    elif fn_name == 'write_file':
                        inp = input(f"Executing writeFile action for file '{fn_args.get('file_path')}' Y? ")
                        if 'Y' == inp or 'y' == inp:
                            tool_inp = write_in_file(fn_args.get('file_path'), fn_args.get('content'))
                            self.messages.append(
                                {
                                    "tool_call_id": tool_call.id,
                                    "role": "tool",
                                    "name": fn_name,
                                    "content": tool_inp,
                                }
                            )

                        else:
                            tool_inp = "User cancelled the request to write contents in the specified file."
                            self.messages.append(
                                {
                                    "tool_call_id": tool_call.id,
                                    "role": "tool",
                                    "name": fn_name,
                                    "content": tool_inp,
                                }
                            )

                    elif fn_name == 'google_search':
                        query = fn_args.get('query')
                        internal_monologue(f"searching for {query}...")
                        tool_inp = google_search(query)
                        self.messages.append(
                            {
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": fn_name,
                                "content": tool_inp,
                            }
                        )

                    elif fn_name == 'get_current_url':
                        internal_monologue("Reading current url")
                        tool_inp = self.browser_driver.current_url
                        self.messages.append(
                            {
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": fn_name,
                                "content": tool_inp,
                            }
                        )

                    elif fn_name == 'refrech_page':
                        internal_monologue("Refreshing page.")
                        self.browser_driver.refresh()
                        tool_inp = "Refreshed the page."
                        self.messages.append(
                            {
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": fn_name,
                                "content": tool_inp,
                            }
                        )

                    elif fn_name == 'open_url':
                        internal_monologue("Opening url in the browser")
                        try:
                            self.browser_driver.get(fn_args.get('url'))
                            tool_inp = "opened " + fn_args.get('url')
                        except Exception as e:
                            tool_inp = "Caught this exception: " + str(e)

                        self.messages.append(
                            {
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": fn_name,
                                "content": tool_inp,
                            }
                        )

                    elif fn_name == 'read_logs':
                        internal_monologue("Reading logs")
                        tool_inp = self.browser_driver.get_log('browser')
                        if len(tool_inp) == 0:
                            tool_inp = "No logs found."
                        self.messages.append(
                            {
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": fn_name,
                                "content": tool_inp,
                            }
                        )
                    
                    elif fn_name == 'take_screenshot':
                        internal_monologue("taking screenshot")
                        self.messages.append(
                            {
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": fn_name,
                                "content": "The screenshot'll be in the next turn."
                            }
                        )
                        self.messages.append(
                            {
                                'role': 'user',
                                'content': [
                                    {
                                        "type": "text",
                                        "text": "This is screenshot of the current page."
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{self.browser_driver.get_screenshot_as_base64()}"
                                        }
                                    }
                                ],
                            }
                        )

                    else:
                        print("NO function found...")
                        exit()

                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=self.messages,
                    tools=dev_tools,
                )
                self.messages.append(response.choices[0].message)
                if self.verbose:
                    self.display_token_usage(response)

            else:
                assistant_message(response.choices[0].message.content)
                user_inp, img = await self.get_user_inp()
                if img is not None:
                    self.messages.append(
                        {
                            "role": 'user',
                            'content': [
                                {
                                    "type": "text",
                                    "text": user_inp
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{encode_image(img)}"
                                    }
                                }
                            ]
                        }
                    )

                else:
                    self.messages.append(
                        {
                            'role': 'user',
                            'content': user_inp
                        }
                    )

                response = self.client.chat.completions.create(
                    messages=self.messages,
                    model="gpt-4o",
                    tools=dev_tools
                )
                self.messages.append(response.choices[0].message)
                if self.verbose:
                    self.display_token_usage(response)
