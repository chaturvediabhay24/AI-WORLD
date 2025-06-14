"""Tools module for AI World."""
from app.tools.registry import ToolRegistry
from app.tools.calculator import CalculatorTool

# Register available tools
ToolRegistry.register_tool(CalculatorTool)

# Export tools for easy access
__all__ = ['ToolRegistry', 'CalculatorTool']
