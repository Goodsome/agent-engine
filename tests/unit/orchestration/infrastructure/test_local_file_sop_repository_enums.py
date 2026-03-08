import pytest
from pathlib import Path
import os
from agent_engine.orchestration.infrastructure.adapters.local_file_sop_repository import LocalFileSopRepository
from agent_engine.orchestration.domain.enums import PlanningLevel, TaskStatus

@pytest.mark.asyncio
async def test_get_sop_with_enums(tmp_path):
    # 创建模拟的 SOP 目录
    sop_dir = tmp_path / "sops"
    sop_dir.mkdir()
    
    # 创建一个符合 atomic_ready.md 格式的文件
    sop_file = sop_dir / "atomic_ready.md"
    sop_file.write_text("""---
name: "Atomic Executor"
description: "Executes atomic tasks"
---
# Instructions
Do the task.""")

    repo = LocalFileSopRepository(base_dir=str(sop_dir))
    
    # 显式传入枚举成员，测试是否能正确映射到 atomic_ready.md
    sop_content = await repo.get_sop(PlanningLevel.ATOMIC, TaskStatus.READY)
    
    assert "Atomic Executor" in sop_content
    assert "Do the task." in sop_content

@pytest.mark.asyncio
async def test_get_sop_file_not_found_message(tmp_path):
    repo = LocalFileSopRepository(base_dir=str(tmp_path))
    
    with pytest.raises(FileNotFoundError) as excinfo:
        await repo.get_sop(PlanningLevel.FEATURE, TaskStatus.READY)
    
    # 验证错误消息中是否包含原始参数，以便调试
    assert "planning_level=feature" in str(excinfo.value)
    assert "status=ready" in str(excinfo.value)
