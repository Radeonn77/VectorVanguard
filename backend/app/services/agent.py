from langgraph.prebuilt import create_react_agent

from app.services.llm import llm
from app.services.agent_tools import retrieve_evidence


tools = [retrieve_evidence]


agent = create_react_agent(
    model=llm,
    tools=tools,
)


def run_agent(query: str):
    """
    Execute LangGraph agent with user query.
    """

    response = agent.invoke(
        {
            "messages": [
                (
                    "human",
                    query,
                )
            ]
        }
    )

    # Last AI message contains final answer
    return response["messages"][-1].content