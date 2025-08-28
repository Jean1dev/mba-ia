from langchain.prompts import PromptTemplate

template = PromptTemplate(
    input_variables=["name"],
    template="Hi, I'm {name}! Tell me a joke with my name!"
)

text = template.format(name="Wesley")
print(text)