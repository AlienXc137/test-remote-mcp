import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.messages import ToolMessage

load_dotenv()

SERVERS={
    "calculator": {
        "transport":"stdio",
        "command": "C:\\Users\\azhar\\.local\\bin\\uv",
        "args": [
            "run",
            "fastmcp",
            "run",
            "C:\\Azhar\\mcp\\expense_tracker\\Local-MCP-Server\\calculator_mcp.py"
        ]
    },
    "expense": {
        "transport":"streaming_http",
        "url": "https://marvelsaz-mcp.fastmcp.app/mcp"
    }
}

async def main():
    client=MultiServerMCPClient(SERVERS)
    tools=await client.get_tools()
    named_tools={}
    for tool in tools:
        named_tools[tool.name]=tool
       # print(named_tools)
    
    llm =  ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    llm_with_tools=llm.bind_tools(tools)
    prompt="product of 20 and 4 using calculator tool if not able to use then tell me it isn't working"
    response=await llm_with_tools.ainvoke(prompt)

    if not getattr(response, "tool_calls", None):
        print("Response:", response.content)
        return

    #print("Response:", response)
    tool_message=[]
    for tc in response.tool_calls:
        slected_tool=tc["name"]
        slected_tool_args=tc.get("args") or {}
        slected_tool_id=tc["id"]
        print(f"Selected Tool: {slected_tool}")
        print(f"Tool Arguments: {slected_tool_args}")

        tool_result=await named_tools[slected_tool].ainvoke(slected_tool_args)
        #print(f"Tool Result: {tool_result}")
        tool_message.append(ToolMessage(content=tool_result, tool_call_id=slected_tool_id))

    final_response=await llm_with_tools.ainvoke([prompt,response,tool_message])
    print("Final Response:", final_response.content)

if __name__ == "__main__":
    asyncio.run(main())