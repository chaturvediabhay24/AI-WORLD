from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import get_db
from app.models.models import ModelProvider
from app.schemas.schemas import ToolExecuteRequest, ToolExecuteResponse, ToolListResponse
from app.tools.registry import ToolRegistry
from app.tools.base import ToolDefinition

router = APIRouter()


@router.get("/tools", response_model=ToolListResponse)
async def list_available_tools():
    """List all available tools that can be enabled for providers."""
    tools = []
    for tool_class in ToolRegistry.get_available_tools():
        # Create temporary instance to get definition
        temp_instance = tool_class.create(provider_id=0)
        tools.append(temp_instance.get_definition())
    return ToolListResponse(tools=tools)


@router.get("/tools/{provider_id}", response_model=List[ToolDefinition])
async def get_provider_tools(
    provider_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all tools enabled for a specific provider."""
    # Verify provider exists
    from sqlalchemy import select
    stmt = select(ModelProvider).where(ModelProvider.id == provider_id)
    result = await db.execute(stmt)
    provider = result.scalar_one_or_none()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    return ToolRegistry.get_provider_tools(provider_id)


@router.post("/tools/{provider_id}/execute", response_model=ToolExecuteResponse)
async def execute_tool(
    provider_id: int,
    request: ToolExecuteRequest,
    db: AsyncSession = Depends(get_db)
):
    """Execute a tool for a specific provider."""
    # Verify provider exists and has the tool enabled
    from sqlalchemy import select
    stmt = select(ModelProvider).where(ModelProvider.id == provider_id)
    result = await db.execute(stmt)
    provider = result.scalar_one_or_none()
    
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    if request.tool_id not in (provider.tool_ids or []):
        raise HTTPException(status_code=400, detail="Tool not enabled for this provider")
    
    try:
        # Get tool instance and execute
        tool = ToolRegistry.get_tool_instance(request.tool_id, provider_id)
        result = await tool.execute(request.parameters)
        
        return ToolExecuteResponse(
            result=result,
            tool_id=request.tool_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
