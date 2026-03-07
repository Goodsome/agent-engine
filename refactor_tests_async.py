import os
import re

for root, dirs, files in os.walk('tests'):
    for file in files:
        if file.startswith('test_') and file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r') as f:
                content = f.read()

            # Replace MagicMock with AsyncMock
            content = content.replace('MagicMock()', 'AsyncMock()')
            if 'AsyncMock' not in content and 'AsyncMock' not in content: # wait, AsyncMock is already imported in some
                pass
            
            # Make tests async and add pytest.mark.asyncio
            # We look for `def test_` and replace it
            lines = content.split('\n')
            new_lines = []
            for i, line in enumerate(lines):
                if line.strip().startswith('def test_'):
                    if i > 0 and '@pytest.mark.asyncio' not in lines[i-1]:
                        # add @pytest.mark.asyncio if it's not parameterized right before
                        pass
                    # If it's parameterized, let's just make it async def
                    line = line.replace('def test_', 'async def test_')
                new_lines.append(line)
            
            content = '\n'.join(new_lines)

            # Add await to use case/repository calls inside tests
            # Typical patterns: `result = use_case.execute(...)` -> `result = await use_case.execute(...)`
            content = re.sub(r'(result = )(use_case\.execute\()', r'\1await \2', content)
            content = re.sub(r'(result = )([a-z_]+\.run\()', r'\1await \2', content)
            content = re.sub(r'(result = )([a-z_]+\.save\()', r'\1await \2', content)
            content = re.sub(r'(result = )([a-z_]+\.delete\()', r'\1await \2', content)
            content = re.sub(r'(result = )([a-z_]+\.find_by_id\()', r'\1await \2', content)
            content = re.sub(r'(result = )([a-z_]+\.get_sop\()', r'\1await \2', content)
            content = re.sub(r'(result = )([a-z_]+\.trigger_session\()', r'\1await \2', content)
            content = re.sub(r'(result = )([a-z_]+\.fetch_ready_tasks\()', r'\1await \2', content)

            # ensure pytest import
            if 'import pytest' not in content:
                content = 'import pytest\n' + content

            with open(filepath, 'w') as f:
                f.write(content)

