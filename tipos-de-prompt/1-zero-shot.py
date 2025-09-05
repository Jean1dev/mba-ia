from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from utils import print_llm_result

load_dotenv()
msg1 = "What's Brazil's capital?"

msg2 = """
Find the user intent in the following text: 
I'm looking for a restaurant around São Paulo who has a good rating for Japanese food.
"""

msg3 = "What's Brazil's capital? Respond only with the city name."



llm = ChatOpenAI(model="gpt-3.5-turbo")
response1 = llm.invoke(msg1)
response2 = llm.invoke(msg2)
response3 = llm.invoke(msg3)

print_llm_result(msg1, response1)
print_llm_result(msg2, response2)
print_llm_result(msg3, response3)