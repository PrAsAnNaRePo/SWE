import asyncio
from agent import Agent
from selenium import webdriver
from colorama import init
from dotenv import load_dotenv

load_dotenv()
init(autoreset=True)

async def main():
    driver = webdriver.Chrome()
    driver.get('http://localhost:3001') # your local project running address
    agent = Agent(open('./system_prompt.txt').read(), browser_driver=driver, verbose=True)
    await agent.start()
    driver.close()

asyncio.run(main())