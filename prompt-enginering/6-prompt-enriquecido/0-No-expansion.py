from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = init_chat_model("openai:gpt-4o-mini", temperature=0.7)

prompt = PromptTemplate(
    input_variables=["question"],
    template=(
        "You are a technology assistant.\n"
        "Answer the following question:\n\n"
        "{question}"
    ),
)

chain = prompt | llm | StrOutputParser()

question = (
        "Explain about the LangChain and LangGraph"
    )

    # Get answer
answer = chain.invoke({"question": question})

print(answer)
print(len(answer))