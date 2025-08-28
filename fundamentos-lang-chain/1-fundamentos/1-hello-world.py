from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

model = ChatOpenAI(model="gpt-5-nano", temperature=0.5)
message = model.invoke("Hello World")

print(message.content)