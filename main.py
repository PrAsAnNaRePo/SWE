import asyncio
from agent import Agent
from selenium import webdriver
from colorama import init
from dotenv import load_dotenv

load_dotenv()
init(autoreset=True)

async def main():
    driver = webdriver.Chrome()
    driver.get('http://localhost:3001')
    # driver.save_screenshot()
    # driver.refresh()
    # driver.current_url
    # driver.get('url')
    # print(driver.get_log('browser'))
    agent = Agent(open('./system_prompt.txt').read(), browser_driver=driver, verbose=True)
    await agent.start()
    driver.close()

asyncio.run(main())