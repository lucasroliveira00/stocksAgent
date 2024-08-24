#import das libs
import json
import os
from datetime import datetime

import yfinance as yf

from crewai import Agent, Task, Crew, Process

from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchResults

import streamlit as st 

#criando yahoo finance tool
def fetch_stock__price (ticket):
    stock = yf.download(ticket, start="2023-08-08", end="2024-08-08")
    return stock

yahoo__finance_tool = Tool(
    name = "Yahoo Finance Tool",
    description = "Fetches stock prices for {ticket} from the last year about a specific company from Yahoo Finance API",
    func= lambda ticket: fetch_stock__price(ticket)
)


#importando openai llm - GPT
os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY'] #colocar código da API do chatGPT gerado direto na OPEN AI
llm = ChatOpenAI(model="gpt-3.5-turbo")


#criando um agente para analisar preço
stockPriceAnalyst = Agent(
    role = "Senior stock price Analyst",
    goal = "Find the {ticket} stock price and alyses trends",
    backstory = """You're highly experienced in analyzing the price of an specific stock and make predictions about its future price.""",
    verbose = True,
    llm = llm,
    max_iter = 5,
    memory = True,
    allow_delegation = True,
    tools = [yahoo__finance_tool]
)


#criando uma task para pegar o preço da ação
getStockPrice = Task(
    description = "Analyze the stock {ticket} price history and create a trend analyses of up, down or sideways",
    expected_output = """Specify the currente trend stock price - up, down or sideways.
    eg. stock='AAPL, price up'""",
    agent = stockPriceAnalyst
)


#importantando a tool de search
search_tool = DuckDuckGoSearchResults(backend='news', num_results=10)


#criando um agente para analisar notícias
newsAnalyst = Agent(
    role = "Stock News Analyst",
    goal = """Create a shot summary of the market news related to the stock {ticket} company. 
    Specify the current trend - up, down or sideways with the news context. For each request stock asset,
    specify a number between 0 anda 100, where 0 is extremely fear and 100 is extreme greed""",
    backstory = """You're highly experienced in analyzing the market trends and news and have tracked asset for more then 10 years.
    You're also master level analysts in the tradicional markets and have deep understandign of human psychology.
    You understand news, theirs titles and information, but you look at those with a health dose of skepticism.
    You consider also the source of the news articles""",
    verbose = True,
    llm = llm,
    max_iter = 5,
    memory = True,
    allow_delegation = True,
    tools = [search_tool]

)


#criando uma task do agente para pegar notícias
get_news = Task(
    description = """Take the stock and always include BTC to it (if not request).
    Use the search tool to search each one individually.

    The current date is {datetime.now()}.

    Compose the results into a helpfull report""",
expected_output = """A summary of the overall market and one sentence summary for each request asset.
Include a fear/greed score for each asset based in the news. Use format:
<STOCK ASSET> 
<SUMMARY BASED ON NEWS>
<TREND PREDICTION>
<FEAR/GREED SCORE>""",
agent = newsAnalyst

)


#criando um analista para avaliar a ação
stockAnalystWrite = Agent(
    role = "Senior Stock Analyst Writer",
    goal = """Analyze the trends price and news and write insighfull compelling and informative 3 paragraph long newsletter based on the stock report and price trend""",
    backstory = """You're widely accepted as the best stock analyst in the market. 
    You understand complex concepts and create compelling stories and narratives that resonate with wider audiences.
    
    You understand macro factors and combine multiple theories - eg. cycle theory and fundamental analyses.
    You're able to hold multiple opinions when analyzing anything""",
    verbose = True,
    llm = llm,
    max_iter = 5,
    memory = True,
    allow_delegation = True
)


writeAnalyses = Task (
    descripption = """Use the stock price trend and the stock news report to create an analyses and write
    the newsletter about te {ticket} cimpany that is brief and highlights the most important points.
    Focus on the sotck price trend, news and fear/greed score. What are the near future considerations?
    Include the previous analyses of stock trend and news summary.""",
    expected_output = """An eloquent 3 paragraphs newsletter formated as markdown in an easy readable manner. It should contain:
    - 3 bullets executive summary
    - Introduction - set the overall picture and spike up the interest
    - main part provides the meat of the analysis including the news summary and fear/greed scores
    - summary - key facts and concrete futute trend prediction - up, down or sideways.""",
    agent = stockAnalystWrite,
    context = [getStockPrice,get_news]

)


crew = Crew(
    agents = [stockPriceAnalyst, newsAnalyst, stockAnalystWrite],
    tasks = [getStockPrice,get_news, writeAnalyses],
    verbose = 2,
    process=Process.hierarchical,
    full_output= True,
    share_crew= False,
    manager_llm= llm,
    max_iter= 15

)


results= crew.kickoff(inputs={'ticket':'AAPL'})


results['final_output']

with st.sidebar:
    st.header('Enter the ticket stock')

    with st.form(key='research_form'):
        topic = st.text_input("Select the ticket")
        submit_button = st.form_submit_button(label="Run Research")

if submit_button:
    if not topic:
        st.error("Please fill the ticket field")

    else:
        results= crew.kickoff(inputs={'ticket': topic})

        st.subheader("Results of your research:")
        st.write(results['final_output'])


echo "# stocksAgent" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/lucasroliveira00/stocksAgent.git
git push -u origin main

git add .
git commit -m "first commit"