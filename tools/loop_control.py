"""
Loop control tools for ADK agents.
"""

from google.adk.tools.tool_context import ToolContext


def exit_loop(tool_context: ToolContext):
    """
    Exit the loop by setting escalate action to True.

    Call this function ONLY when the loop completion condition is met,
    signaling that the iterative process should end.

    Args:
        tool_context: The ADK tool context provided automatically

    Returns:
        dict: Empty dictionary as tools should return JSON-serializable output
    """
    print(f"  [Tool Call] exit_loop triggered by {tool_context.agent_name}")
    tool_context.actions.escalate = True
    # Return empty dict as tools should typically return JSON-serializable output
    return {}
