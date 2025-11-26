"""
Home - MCP Client for querying data using AI
"""
import streamlit as st
import sys
import os
import json
import logging
from typing import List, Dict, Any
import requests

# Add parent directory to path for imports (now in pages/ subdirectory, need 4 levels up)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
import config
from src.database.mongodb_client import test_connection
from src.database.settings_manager import save_llm_settings, load_llm_settings

# Import MCP server functions directly
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'mcp_server'))
from mongodb_mcp_server import (
    get_available_fields,
    advanced_query,
    aggregate_by_any_field,
    cost_analysis_by_field,
    multi_dimensional_analysis,
    get_database_schema,
    query_resources,
    get_statistics,
    get_total_cost,
    aggregate_by_field
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="🏠 AI Assistant",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for taller chat input
st.markdown("""
<style>
    /* Make chat input taller (5 lines) */
    .stChatInputContainer textarea {
        min-height: 125px !important;
        height: 125px !important;
    }

    /* Adjust placeholder text */
    .stChatInputContainer textarea::placeholder {
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

# Available MCP tools
AVAILABLE_TOOLS = [
    {
        "name": "get_available_fields",
        "description": "Get a list of ALL queryable fields in the database, including all dynamically extracted tag fields",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "advanced_query",
        "description": "Query resources using ANY combination of fields. Pass field names and values as filters",
        "parameters": {
            "type": "object",
            "properties": {
                "filters": {
                    "type": "object",
                    "description": "Dictionary of field:value pairs to filter by"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results (default: 100)"
                }
            },
            "required": ["filters"]
        }
    },
    {
        "name": "aggregate_by_any_field",
        "description": "Count and aggregate documents grouped by ANY field in the database",
        "parameters": {
            "type": "object",
            "properties": {
                "group_by_field": {
                    "type": "string",
                    "description": "Field to group by"
                },
                "aggregation_type": {
                    "type": "string",
                    "enum": ["count", "sum", "avg"],
                    "description": "Type of aggregation"
                },
                "value_field": {
                    "type": "string",
                    "description": "Field to sum/avg (required for sum/avg)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of groups (default: 20)"
                }
            },
            "required": ["group_by_field"]
        }
    },
    {
        "name": "cost_analysis_by_field",
        "description": "Analyze total cost grouped by any field with detailed breakdown",
        "parameters": {
            "type": "object",
            "properties": {
                "group_by_field": {
                    "type": "string",
                    "description": "Field to group costs by"
                },
                "filters": {
                    "type": "object",
                    "description": "Optional filters to apply before grouping"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of groups (default: 20)"
                }
            },
            "required": ["group_by_field"]
        }
    },
    {
        "name": "get_statistics",
        "description": "Get overall statistics about the database",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_total_cost",
        "description": "Calculate total cost with optional filters",
        "parameters": {
            "type": "object",
            "properties": {
                "applicationName": {"type": "string"},
                "environment": {"type": "string"},
                "owner": {"type": "string"},
                "date": {"type": "string"}
            }
        }
    }
]


def truncate_large_response(data: Any, max_tokens: int = 2000) -> Any:
    """Truncate large responses to prevent context overflow"""
    # Convert to JSON string to check size
    json_str = json.dumps(data)

    # Rough estimate: 1 token ≈ 4 characters
    estimated_tokens = len(json_str) / 4

    if estimated_tokens > max_tokens:
        logger.warning(f"Response too large ({estimated_tokens:.0f} tokens), truncating...")

        # If it's a dict with a list of results, truncate the list
        if isinstance(data, dict):
            for key in ['results', 'data', 'resources', 'documents', 'records']:
                if key in data and isinstance(data[key], list):
                    original_count = len(data[key])
                    data[key] = data[key][:5]  # Keep only first 5 items
                    data['_truncated'] = f"Showing 5 of {original_count} items (response was too large)"
                    break

        # If it's a list, truncate it
        elif isinstance(data, list):
            original_count = len(data)
            data = data[:5]
            data = {
                "results": data,
                "_truncated": f"Showing 5 of {original_count} items (response was too large)"
            }

    return data


def call_mcp_tool(tool_name: str, parameters: Dict[str, Any]) -> Any:
    """Call an MCP tool function"""
    try:
        if tool_name == "get_available_fields":
            import asyncio
            result = asyncio.run(get_available_fields())
            return json.loads(result[0].text)

        elif tool_name == "advanced_query":
            import asyncio
            # Limit query results to prevent overflow
            if parameters.get("limit", 100) > 50:
                parameters["limit"] = 50
                logger.info("Limited query results to 50 to prevent context overflow")

            result = asyncio.run(advanced_query(
                parameters.get("filters", {}),
                parameters.get("limit", 50),
                parameters.get("fields_to_return")
            ))
            data = json.loads(result[0].text)
            return truncate_large_response(data, max_tokens=2000)

        elif tool_name == "aggregate_by_any_field":
            import asyncio
            result = asyncio.run(aggregate_by_any_field(
                parameters["group_by_field"],
                parameters.get("aggregation_type", "count"),
                parameters.get("value_field"),
                parameters.get("limit", 20),
                parameters.get("sort_order", "desc")
            ))
            return json.loads(result[0].text)

        elif tool_name == "cost_analysis_by_field":
            import asyncio
            result = asyncio.run(cost_analysis_by_field(
                parameters["group_by_field"],
                parameters.get("filters"),
                parameters.get("limit", 20)
            ))
            return json.loads(result[0].text)

        elif tool_name == "get_statistics":
            import asyncio
            result = asyncio.run(get_statistics())
            data = json.loads(result[0].text)
            # Statistics can be large, truncate if needed
            return truncate_large_response(data, max_tokens=3000)

        elif tool_name == "get_total_cost":
            import asyncio
            result = asyncio.run(get_total_cost(
                parameters.get("applicationName"),
                parameters.get("environment"),
                parameters.get("owner"),
                parameters.get("date")
            ))
            return json.loads(result[0].text)

        else:
            return {"error": f"Unknown tool: {tool_name}"}

    except Exception as e:
        logger.error(f"Error calling tool {tool_name}: {e}")
        return {"error": str(e)}


def call_openrouter(messages: List[Dict], api_key: str, model: str, tools: List[Dict]) -> Dict:
    """Call OpenRouter API with tool support"""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/mudakara/excel-tags-parser-mongodb",
            "X-Title": "Excel Tags Parser"
        }

        data = {
            "model": model,
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto"
        }

        logger.info(f"Calling OpenRouter with model: {model}")
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )

        # Check for HTTP errors and return detailed error message
        if response.status_code != 200:
            error_detail = response.json() if response.text else {"message": "Unknown error"}
            logger.error(f"OpenRouter API error {response.status_code}: {error_detail}")
            return {
                "error": f"API Error ({response.status_code}): {error_detail.get('error', {}).get('message', error_detail)}\n\nModel: {model}\nCheck: 1) API key is valid, 2) Model name is correct, 3) Account has credits"
            }

        return response.json()

    except requests.exceptions.RequestException as e:
        logger.error(f"OpenRouter API request error: {e}")
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        logger.error(f"OpenRouter API error: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


def call_claude(messages: List[Dict], api_key: str, model: str, tools: List[Dict]) -> Dict:
    """Call Claude API with tool support"""
    try:
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        # Convert messages to Claude format
        system_msg = ""
        claude_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                claude_messages.append(msg)

        data = {
            "model": model,
            "max_tokens": 4096,
            "messages": claude_messages,
            "tools": tools
        }

        if system_msg:
            data["system"] = system_msg

        logger.info(f"Calling Claude API with model: {model}")
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data,
            timeout=60
        )

        # Check for HTTP errors and return detailed error message
        if response.status_code != 200:
            error_detail = response.json() if response.text else {"message": "Unknown error"}
            logger.error(f"Claude API error {response.status_code}: {error_detail}")
            return {
                "error": f"API Error ({response.status_code}): {error_detail.get('error', {}).get('message', error_detail)}\n\nModel: {model}\nCheck: 1) API key is valid, 2) Model name is correct, 3) Account has credits, 4) API access is enabled"
            }

        return response.json()

    except requests.exceptions.RequestException as e:
        logger.error(f"Claude API request error: {e}")
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        logger.error(f"Claude API error: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


def format_tools_for_openai(tools: List[Dict]) -> List[Dict]:
    """Format tools for OpenAI/OpenRouter format"""
    formatted_tools = []
    for tool in tools:
        formatted_tools.append({
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool.get("parameters", {"type": "object", "properties": {}})
            }
        })
    return formatted_tools


def format_tools_for_claude(tools: List[Dict]) -> List[Dict]:
    """Format tools for Claude format"""
    formatted_tools = []
    for tool in tools:
        # Get parameters and ensure "type" is always set
        params = tool.get("parameters", {})
        if "type" not in params:
            params = {"type": "object", "properties": {}, "required": []}

        formatted_tools.append({
            "name": tool["name"],
            "description": tool["description"],
            "input_schema": params
        })
    return formatted_tools


def main():
    """Main home page function"""

    st.title("🤖 AI Assistant")
    st.markdown("Ask questions about Azure cost and Infrastructure related data.")

    # Load saved LLM settings on first run
    if "settings_loaded" not in st.session_state:
        saved_settings = load_llm_settings()
        if saved_settings:
            st.session_state.llm_provider = saved_settings.get("provider", "OpenRouter")
            st.session_state.llm_api_key = saved_settings.get("api_key", "")
            saved_model = saved_settings.get("model")

            # Set default model based on provider
            if saved_settings.get("provider") == "Claude":
                # If no model saved or it's not a Claude model, use default
                if not saved_model or not saved_model.startswith("claude-"):
                    saved_model = "claude-3-5-sonnet-20241022"
            elif not saved_model:
                # Default for OpenRouter
                saved_model = "anthropic/claude-3.5-sonnet"

            st.session_state.llm_model = saved_model
        else:
            st.session_state.llm_provider = "OpenRouter"
            st.session_state.llm_api_key = ""
            st.session_state.llm_model = "anthropic/claude-3.5-sonnet"
        st.session_state.settings_loaded = True

    # Sidebar - LLM Configuration
    with st.sidebar:
        st.header("🤖 LLM Configuration")

        # Available model options
        model_options = [
            "anthropic/claude-3.5-sonnet",
            "anthropic/claude-3-opus",
            "anthropic/claude-3-sonnet",
            "openai/gpt-4-turbo",
            "openai/gpt-4",
            "openai/gpt-3.5-turbo",
            "meta-llama/llama-3.1-70b-instruct",
            "google/gemini-pro-1.5",
            "mistralai/mistral-large"
        ]

        # Provider selection - using session state key for persistence
        provider_options = ["OpenRouter", "Claude", "Custom"]

        # Ensure provider is in session state
        if "llm_provider" not in st.session_state:
            st.session_state.llm_provider = "OpenRouter"

        default_provider_index = provider_options.index(st.session_state.llm_provider) if st.session_state.llm_provider in provider_options else 0

        llm_provider = st.selectbox(
            "Select LLM Provider",
            options=provider_options,
            index=default_provider_index,
            help="Choose which LLM provider to use",
            key="provider_selector"
        )

        # Update session state if changed
        if llm_provider != st.session_state.llm_provider:
            st.session_state.llm_provider = llm_provider

        # API Key input - using session state key for persistence
        if "llm_api_key" not in st.session_state:
            st.session_state.llm_api_key = ""

        api_key = ""
        if llm_provider in ["OpenRouter", "Claude"]:
            api_key = st.text_input(
                "API Key",
                value=st.session_state.llm_api_key,
                type="password",
                help="Enter your API key",
                key="api_key_input"
            )

        # Model selection for OpenRouter
        model = st.session_state.get("llm_model", "anthropic/claude-3.5-sonnet")
        if llm_provider == "OpenRouter":
            # Ensure model is valid for OpenRouter
            if model not in model_options:
                model = "anthropic/claude-3.5-sonnet"

            default_model_index = model_options.index(model) if model in model_options else 0

            model = st.selectbox(
                "Select Model",
                options=model_options,
                index=default_model_index,
                help="Choose which model to use",
                key="openrouter_model_selector"
            )

        # Model selection for Claude
        elif llm_provider == "Claude":
            claude_model_options = [
                "claude-3-5-sonnet-20241022",  # Latest Claude 3.5 Sonnet
                "claude-3-5-sonnet-20240620",  # Claude 3.5 Sonnet (June 2024)
                "claude-3-opus-20240229",      # Claude 3 Opus
                "claude-3-haiku-20240307"      # Claude 3 Haiku
            ]

            st.info("💡 If you get a 404 error, your API key might not have access to that model. Try a different one!")

            # Ensure model is valid for Claude
            if model not in claude_model_options:
                model = "claude-3-5-sonnet-20241022"

            default_claude_model_index = claude_model_options.index(model) if model in claude_model_options else 0

            model = st.selectbox(
                "Select Claude Model",
                options=claude_model_options,
                index=default_claude_model_index,
                help="Choose which Claude model to use. If you get 404 errors, try claude-3-haiku-20240307 (most widely available)",
                key="claude_model_selector"
            )
        else:
            # Default for Custom provider (not yet implemented)
            model = "custom-model"

        # Update session state with current model selection
        st.session_state.llm_model = model

        st.markdown("---")

        # Manual Save Button
        if st.button("💾 Save Settings", type="primary", use_container_width=True):
            save_result = save_llm_settings(
                provider=llm_provider,
                api_key=api_key if api_key else st.session_state.llm_api_key,
                model=model
            )

            if save_result:
                st.success("✅ Settings saved successfully!")
                # Update session state with saved values
                st.session_state.llm_provider = llm_provider
                st.session_state.llm_api_key = api_key if api_key else st.session_state.llm_api_key
                st.session_state.llm_model = model
            else:
                st.error("❌ Failed to save settings")

        st.markdown("---")

        # MongoDB status
        st.markdown("**MongoDB Status:**")
        if test_connection():
            st.success("✅ Connected")
        else:
            st.error("❌ Disconnected")

        st.markdown("---")

        # Available tools
        with st.expander("📦 Available MCP Tools"):
            for tool in AVAILABLE_TOOLS:
                st.markdown(f"**{tool['name']}**")
                st.caption(tool['description'])

    # Main content - Chat Interface
    if llm_provider in ["OpenRouter", "Claude"] and not api_key:
        st.warning("⚠️ Please enter your API key in the sidebar to use the AI assistant")
        st.info(f"""
        **How to get an API key:**
        - **OpenRouter**: Sign up at https://openrouter.ai/ and get your API key from the dashboard
        - **Claude**: Get your API key from https://console.anthropic.com/
        """)
        return

    # Check MongoDB connection
    if not test_connection():
        st.error("❌ Cannot connect to MongoDB. Please start MongoDB to use the AI assistant.")
        st.info("Run: `brew services start mongodb-community` or `mongod`")
        return

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Automatic context management - keep only last 10 messages to prevent overflow
    MAX_MESSAGES = 10
    if len(st.session_state.messages) > MAX_MESSAGES:
        # Keep only the most recent messages
        st.session_state.messages = st.session_state.messages[-MAX_MESSAGES:]
        st.info(f"ℹ️ Chat history automatically trimmed to last {MAX_MESSAGES} messages to prevent context overflow")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Display tool calls if any
            if "tool_calls" in message and message["tool_calls"]:
                with st.expander("🔧 Tool Calls"):
                    for tool_call in message["tool_calls"]:
                        st.code(json.dumps(tool_call, indent=2))

    # Chat input
    if prompt := st.chat_input("Ask a question about your data..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Prepare messages for LLM
        messages = [
            {
                "role": "system",
                "content": """You are a helpful data analyst assistant. You have access to a MongoDB database with resource data.
                Use the available tools to answer user questions about the data. Always use tools to get accurate information
                rather than making assumptions. When presenting data, format it clearly and provide insights."""
            }
        ] + st.session_state.messages

        # Call LLM with tools
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                max_iterations = 5
                iteration = 0

                while iteration < max_iterations:
                    iteration += 1

                    # Format tools based on provider
                    if llm_provider == "OpenRouter":
                        formatted_tools = format_tools_for_openai(AVAILABLE_TOOLS)
                        response = call_openrouter(messages, api_key, model, formatted_tools)
                    elif llm_provider == "Claude":
                        formatted_tools = format_tools_for_claude(AVAILABLE_TOOLS)
                        response = call_claude(messages, api_key, model, formatted_tools)
                    else:
                        st.error("Custom LLM provider not yet implemented")
                        break

                    if "error" in response:
                        st.error(f"❌ Error: {response['error']}")
                        break

                    # Handle response based on provider
                    if llm_provider == "OpenRouter":
                        choice = response.get("choices", [{}])[0]
                        message = choice.get("message", {})
                        finish_reason = choice.get("finish_reason")

                        # Check for tool calls
                        tool_calls = message.get("tool_calls", [])

                        if tool_calls:
                            # Execute tool calls
                            tool_results = []

                            with st.expander("🔧 Executing Tools..."):
                                for tool_call in tool_calls:
                                    function = tool_call.get("function", {})
                                    tool_name = function.get("name")
                                    parameters = json.loads(function.get("arguments", "{}"))

                                    st.write(f"**Calling:** `{tool_name}`")
                                    st.json(parameters)

                                    # Call the tool
                                    result = call_mcp_tool(tool_name, parameters)
                                    tool_results.append({
                                        "tool_call_id": tool_call.get("id"),
                                        "role": "tool",
                                        "name": tool_name,
                                        "content": json.dumps(result)
                                    })

                                    st.write(f"**Result:**")
                                    st.json(result)

                            # Add assistant message with tool calls
                            messages.append({
                                "role": "assistant",
                                "content": message.get("content") or "",
                                "tool_calls": tool_calls
                            })

                            # Add tool results
                            for result in tool_results:
                                messages.append(result)

                            # Continue loop to get final response
                            continue

                        else:
                            # Final response
                            assistant_message = message.get("content", "")
                            st.markdown(assistant_message)
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": assistant_message
                            })
                            break

                    elif llm_provider == "Claude":
                        content = response.get("content", [])
                        stop_reason = response.get("stop_reason")

                        # Check for tool use
                        tool_uses = [c for c in content if c.get("type") == "tool_use"]

                        if tool_uses and stop_reason == "tool_use":
                            # Execute tool calls
                            tool_results = []

                            with st.expander("🔧 Executing Tools..."):
                                for tool_use in tool_uses:
                                    tool_name = tool_use.get("name")
                                    parameters = tool_use.get("input", {})
                                    tool_use_id = tool_use.get("id")

                                    st.write(f"**Calling:** `{tool_name}`")
                                    st.json(parameters)

                                    # Call the tool
                                    result = call_mcp_tool(tool_name, parameters)
                                    tool_results.append({
                                        "type": "tool_result",
                                        "tool_use_id": tool_use_id,
                                        "content": json.dumps(result)
                                    })

                                    st.write(f"**Result:**")
                                    st.json(result)

                            # Add assistant message with tool use
                            messages.append({
                                "role": "assistant",
                                "content": content
                            })

                            # Add tool results
                            messages.append({
                                "role": "user",
                                "content": tool_results
                            })

                            # Continue loop to get final response
                            continue

                        else:
                            # Final response
                            text_content = [c.get("text", "") for c in content if c.get("type") == "text"]
                            assistant_message = "\n".join(text_content)
                            st.markdown(assistant_message)
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": assistant_message
                            })
                            break

                    else:
                        break

    # Clear chat button
    if st.session_state.messages:
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()


if __name__ == "__main__":
    main()
