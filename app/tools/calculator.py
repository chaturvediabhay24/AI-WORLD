from typing import Any, Dict

from app.tools.base import BaseTool, ToolDefinition, ToolParameter


class CalculatorTool(BaseTool):
    """A simple calculator tool for basic arithmetic operations."""

    def __init__(self, provider_id: int):
        self.provider_id = provider_id

    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            id="calculator",
            name="Calculator",
            description="Perform basic arithmetic calculations",
            provider_id=self.provider_id,
            parameters=[
                ToolParameter(
                    name="operation",
                    type="string",
                    description="The arithmetic operation to perform (add, subtract, multiply, divide)",
                    required=True
                ),
                ToolParameter(
                    name="x",
                    type="number",
                    description="First number",
                    required=True
                ),
                ToolParameter(
                    name="y",
                    type="number",
                    description="Second number",
                    required=True
                )
            ]
        )

    async def execute(self, parameters: Dict[str, Any]) -> Any:
        """Execute the calculator operation."""
        operation = parameters["operation"]
        x = float(parameters["x"])
        y = float(parameters["y"])

        if operation == "add":
            return x + y
        elif operation == "subtract":
            return x - y
        elif operation == "multiply":
            return x * y
        elif operation == "divide":
            if y == 0:
                raise ValueError("Cannot divide by zero")
            return x / y
        else:
            raise ValueError(f"Unknown operation: {operation}")
