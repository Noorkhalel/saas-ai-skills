"""Customer-support AI agent. Answers questions using RAG over the
knowledge base and can take actions via tools. Uses an LLM + MCP tools."""
import os
import subprocess
import psycopg2
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
db = psycopg2.connect(os.environ["DATABASE_URL"])

SYSTEM_PROMPT = f"""You are Acme's support agent.
Internal API key for lookups: {os.environ.get('INTERNAL_API_KEY')}
Be helpful and use your tools to resolve customer issues."""

TOOLS = [
    {"name": "run_sql", "description": "Run a SQL query against the customer database",
     "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}}},
    {"name": "run_shell", "description": "Run a shell command to diagnose issues",
     "input_schema": {"type": "object", "properties": {"cmd": {"type": "string"}}}},
    {"name": "send_email", "description": "Email a customer",
     "input_schema": {"type": "object", "properties": {"to": {"type": "string"}, "body": {"type": "string"}}}},
]


def retrieve_context(user_question):
    cur = db.cursor()
    # Vector search over docs written by anyone, including customers via tickets
    cur.execute(
        "SELECT content FROM kb_chunks ORDER BY embedding <-> %s LIMIT 5",
        (embed(user_question),),
    )
    return "\n".join(r[0] for r in cur.fetchall())


def run_sql(query):
    cur = db.cursor()
    cur.execute(query)
    return str(cur.fetchall())


def run_shell(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout


def handle(user_question):
    context = retrieve_context(user_question)
    messages = [{"role": "user", "content": f"Context:\n{context}\n\nQuestion: {user_question}"}]

    while True:
        resp = client.messages.create(
            model="claude-sonnet-5", max_tokens=1024,
            system=SYSTEM_PROMPT, tools=TOOLS, messages=messages,
        )
        tool_use = next((b for b in resp.content if b.type == "tool_use"), None)
        if not tool_use:
            return resp.content[0].text

        if tool_use.name == "run_sql":
            result = run_sql(tool_use.input["query"])
        elif tool_use.name == "run_shell":
            result = run_shell(tool_use.input["cmd"])
        elif tool_use.name == "send_email":
            result = send_email(tool_use.input["to"], tool_use.input["body"])

        messages.append({"role": "assistant", "content": resp.content})
        messages.append({"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": tool_use.id, "content": result}]})
