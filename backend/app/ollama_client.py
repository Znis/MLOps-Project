"""Ollama chat client with streaming and tool-calling support, compatible with the RAG assistant."""
import json
from uuid import uuid4
from ollama import AsyncClient
from app.config import settings
from app.assistants.tools import QueryKnowledgeBaseTool


def _tool_schema_from_pydantic():
    """Build Ollama tools list from QueryKnowledgeBaseTool."""
    schema = QueryKnowledgeBaseTool.model_json_schema()
    props = schema.get("properties", {})
    tool_desc = (QueryKnowledgeBaseTool.__doc__ or "Query the document knowledge base.").strip()
    return [
        {
            "type": "function",
            "function": {
                "name": "QueryKnowledgeBaseTool",
                "description": f"{tool_desc}\n\nIMPORTANT: You MUST call this tool for ANY question about document content, facts, summaries, or information from indexed documents. Extract 2-5 key search terms from the user's question and use them as query_input.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        k: {
                            "type": "string",
                            "description": (v.get("description") or "")
                        }
                        for k, v in props.items()
                    },
                    "required": schema.get("required", ["query_input"]),
                },
            },
        }
    ]


def _get_msg(m, key, default=None):
    if isinstance(m, dict):
        return m.get(key, default)
    return getattr(m, key, default)


def _openai_to_ollama_messages(messages: list) -> list[dict]:
    """Convert OpenAI-format messages to Ollama format (tool messages use tool_name, not tool_call_id)."""
    ollama = []
    tool_call_id_to_name = {}
    for m in messages:
        role = _get_msg(m, "role")
        if role == "system":
            ollama.append({"role": "system", "content": _get_msg(m, "content", "")})
        elif role == "user":
            ollama.append({"role": "user", "content": _get_msg(m, "content", "")})
        elif role == "assistant":
            content = _get_msg(m, "content") or ""
            msg = {"role": "assistant", "content": content}
            tcs = _get_msg(m, "tool_calls") or []
            if tcs:
                tool_calls = []
                for i, tc in enumerate(tcs):
                    name = tc.get("name") if isinstance(tc, dict) else getattr(getattr(tc, "function", None), "name", "QueryKnowledgeBaseTool")
                    args = tc.get("arguments") if isinstance(tc, dict) else getattr(getattr(tc, "function", None), "arguments", "{}")
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except json.JSONDecodeError:
                            args = {}
                    tid = tc.get("id") if isinstance(tc, dict) else getattr(tc, "id", str(uuid4()))
                    tool_call_id_to_name[tid] = name
                    tool_calls.append({"type": "function", "function": {"index": i, "name": name, "arguments": args}})
                msg["tool_calls"] = tool_calls
            ollama.append(msg)
        elif role == "tool":
            tid = _get_msg(m, "tool_call_id")
            name = tool_call_id_to_name.get(tid, "QueryKnowledgeBaseTool")
            ollama.append({"role": "tool", "tool_name": name, "content": _get_msg(m, "content", "")})
    return ollama


class _DeltaEvent:
    type = "content.delta"
    def __init__(self, delta: str):
        self.delta = delta


class _MockMessage:
    def __init__(self, content: str, tool_calls: list | None = None):
        self.content = content or ""
        self.tool_calls = tool_calls or []


class _MockCompletion:
    def __init__(self, message: _MockMessage):
        self.choices = [_MockChoice(message)]


class _MockChoice:
    def __init__(self, message: _MockMessage):
        self.message = message


class _OllamaStreamContext:
    """Context manager that runs Ollama stream and provides get_final_completion()."""

    def __init__(self, messages: list[dict], tools: list | None = None):
        self._client = AsyncClient(host=settings.OLLAMA_HOST)
        self._messages = messages
        self._tools = _tool_schema_from_pydantic()
        self._content: list[str] = []
        self._tool_calls_accum: list[dict] = []
        self._final_message: _MockMessage | None = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def _run_stream(self):
        ollama_messages = _openai_to_ollama_messages(self._messages)
        print(f"\n[Ollama] Sending request with {len(self._tools)} tool(s):")
        for tool in self._tools:
            fn = tool.get("function", {})
            print(f"  - Tool: {fn.get('name', 'unknown')}")
            print(f"    Description: {fn.get('description', '')[:100]}...")
            print(f"    Parameters: {list(fn.get('parameters', {}).get('properties', {}).keys())}")
        
        # Try to encourage tool usage - some Ollama models support tool_choice
        chat_kwargs = {
            "model": settings.OLLAMA_MODEL,
            "messages": ollama_messages,
            "tools": self._tools,
            "stream": True,
            "think": False
        }
        # Some models support tool_choice='required' or tool_choice={'type': 'function', 'function': {'name': 'QueryKnowledgeBaseTool'}}
        # But not all models support it, so we'll try without first
        
        stream = await self._client.chat(**chat_kwargs)
        tool_calls_received = False
        async for chunk in stream:
            if chunk.message.content:
                self._content.append(chunk.message.content)
                yield _DeltaEvent(chunk.message.content)
            if getattr(chunk.message, "tool_calls", None):
                tool_calls_received = True
                print(f"\n[Ollama] Received tool_calls in chunk: {len(chunk.message.tool_calls)}")
                for tc in chunk.message.tool_calls:
                    print(f"  - Tool call type: {type(tc)}")
                    print(f"    Has 'function': {hasattr(tc, 'function')}")
                    if hasattr(tc, 'function'):
                        fn = tc.function
                        print(f"    Function name: {getattr(fn, 'name', 'N/A')}")
                        print(f"    Function arguments: {getattr(fn, 'arguments', 'N/A')}")
                    self._tool_calls_accum.append(tc)
        
        if not tool_calls_received and self._tool_calls_accum:
            print(f"[Ollama] Accumulated {len(self._tool_calls_accum)} tool call(s) from stream")
        elif not tool_calls_received:
            print(f"[Ollama] No tool calls received in stream")

    def build_final_completion(self):
        """Build final message with content and tool_calls (OpenAI-style) for the assistant."""
        content = "".join(self._content)
        tool_calls = []
        print(f"\n[Ollama] Building final completion from {len(self._tool_calls_accum)} accumulated tool call(s)")
        for i, tc in enumerate(self._tool_calls_accum, 1):
            print(f"  Processing tool call {i}: type={type(tc)}")
            # Handle both Ollama's native tool call objects and dicts
            if hasattr(tc, "function"):
                # Real Ollama tool call object
                fn = tc.function
                name = getattr(fn, "name", None)
                args = getattr(fn, "arguments", None)
                print(f"    ✓ Real Ollama tool call: {name}")
            elif isinstance(tc, dict):
                # Dict format
                fn = tc.get("function", tc)
                name = fn.get("name") if isinstance(fn, dict) else "QueryKnowledgeBaseTool"
                args = fn.get("arguments", {}) if isinstance(fn, dict) else {}
                print(f"    ✓ Dict format tool call: {name}")
            else:
                # Fallback
                name = "QueryKnowledgeBaseTool"
                args = {}
                print(f"    ⚠ Unknown format, using defaults")
            
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except json.JSONDecodeError:
                    args = {}
            
            print(f"    Arguments: {args}")
            try:
                parsed = QueryKnowledgeBaseTool.model_validate(args)
                print(f"    ✓ Successfully parsed as QueryKnowledgeBaseTool")
            except Exception as e:
                print(f"    ⚠ Parse error: {e}, using fallback")
                parsed = QueryKnowledgeBaseTool(query_input=args.get("query_input", ""))
            
            mock_tc = _MockToolCall(id=str(uuid4()), name=name, arguments=args, parsed_arguments=parsed)
            tool_calls.append(mock_tc)
        
        self._final_message = _MockMessage(content=content, tool_calls=tool_calls)
        return _MockCompletion(self._final_message)


class _MockToolCall:
    def __init__(self, id: str, name: str, arguments: dict, parsed_arguments: QueryKnowledgeBaseTool):
        self.id = id
        self.function = _MockFunction(name=name, arguments=arguments, parsed_arguments=parsed_arguments)


class _MockFunction:
    def __init__(self, name: str, arguments: dict, parsed_arguments: QueryKnowledgeBaseTool):
        self.name = name
        self.arguments = json.dumps(arguments) if isinstance(arguments, dict) else arguments
        self.parsed_arguments = parsed_arguments


def chat_stream(messages: list[dict], tools: list | None = None, **kwargs):
    """
    Returns an async context manager that streams Ollama chat and provides get_final_completion().
    Compatible with the RAG assistant's expected interface.
    """
    ctx = _OllamaStreamContext(messages, tools=tools)

    class _StreamAdapter:
        async def __aenter__(self):
            await ctx.__aenter__()
            return self

        async def __aexit__(self, *args):
            return await ctx.__aexit__(*args)

        def __aiter__(self):
            return self

        async def __anext__(self):
            if not hasattr(self, "_gen"):
                self._gen = ctx._run_stream()
            try:
                return await self._gen.__anext__()
            except StopAsyncIteration:
                if not hasattr(self, "_final"):
                    self._final = ctx.build_final_completion()
                raise

        async def get_final_completion(self):
            if not hasattr(self, "_final"):
                if hasattr(self, "_gen"):
                    try:
                        while True:
                            await self._gen.__anext__()
                    except StopAsyncIteration:
                        pass
                self._final = ctx.build_final_completion()
            return self._final

    return _StreamAdapter()
