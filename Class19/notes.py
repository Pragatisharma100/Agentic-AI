# MCP lifecycle
# Create MCP Servers -


# STDIO- standard input/output
# 3 step process
# client launches the server as a subprocess
# server reads from stdin and writes to stdout- 

# we already have terminal(Client) and have python file (subprocess) that we want to run as a server.

# benefit of stdio
# fast and simple communication between client and server, presenet on the same system
# secure - both are running on the same system
# Simple connection
# private by construction


# STREAMABLE HTTP
# -HTTP protocol of exchanging the data
# -HTTP allows my host to reach out to server running anywhere on the internet
# - it send POST request to the server 

# - one endpoint (commonly /mcp) , post +get
# -plain JSON or upgrades to SSE for long calls
# -optional Mcp-Session-id 


