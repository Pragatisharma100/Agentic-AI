"""
Class 7 quick notes

1. setup_check.ipynb
   - Loads OPENAI_API_KEY from .env
   - Creates a simple LangChain agent with create_agent()
   - Uses a placeholder tool get_weather()
   - Invokes the agent and prints the response content_blocks

2. 04_05_prompt_templates_structured_output_student_notes.ipynb
   - Part 4: Prompt templates
     * Use ChatPromptTemplate.from_messages()
     * Keep the prompt structure fixed
     * Fill variables like {tone} and {topic}
   - Part 5: Structured output
     * Use Pydantic BaseModel for strict output shape
     * Use with_structured_output(SupportTicket)
     * ProviderStrategy uses provider JSON schema
     * ToolStrategy uses a fake tool schema

3. Important terminology
   - LangGraph: low-level orchestration engine
   - LangChain: create_agent harness built on LangGraph
   - Deep Agents: batteries-included layer on top of create_agent
   - LangSmith: observability / tracing, not just print statements

4. Git notes
   - .gitignore only stops new untracked files from being added
   - If a file is already tracked, .gitignore does not make it private
   - To stop tracking a committed file:
     git rm --cached path/to/file
"""