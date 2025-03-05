from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

from app.core.config import settings, ModelType
from app.core.function_templates.functions import functions

model = ChatOpenAI(
    model=ModelType.GPT4O,
    openai_api_key=settings.OPENAI_API_KEY
)

def function_call(prompt, function_name):
    model_ = model.bind_tools(functions, tool_choice=function_name)
    messages = [SystemMessage(prompt)]
    function_call = model_.invoke(messages).tool_calls
    result = function_call[0]['args']

    return result
