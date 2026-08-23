# MCP (https://ai-automation-with-mayank.netlify.app/#home )
# model context protocol
# -open source standard protocol
# -created by anthropic

#         just a next word /token
# code -------------> terminal
#         model


# LLm is a black box it is a brain that only give output, to the things that is store in your LLM storage

# all the llm have training data cutoff date
# MCP is not giving our llm intelligent , it is about giving it an ability to see more. 
# context- the information that is provided to the LLM to help it generate a response
# -it is everthing that your llm/model can see when it ans your question
# -better context better ans
# mcp is the tool that enables the llm to access more information and context
# mcp allow application llm with hands so that they can work

# mcp components
#         host
# MCP client -----------> MCP server
#            <------------


# 2 kind of mcp server
# -stdio
# -streamable HTTP


# LLM <----> MCp client -------------> MCP server (tools,prompt, resource)
# LLM AND MCPclient are host(claude desktop, agentic, cursor)

# if i have my server , then i have to maintain it

# before mcp v/s after the mcp

# host- claude desktop, vscode,cursor,ai or chatbot, codex
# server- github,tools,gmail,drive,slack, your own mcp server , canva
# host ------------> server
# mcpclient +host -----> sever
# the host never talk to a server directly -it delegates entirely


# server- tools, resoucsre, prompts