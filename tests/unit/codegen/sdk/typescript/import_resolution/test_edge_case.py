from typing import TYPE_CHECKING

from codegen.sdk.codebase.factory.get_session import get_codebase_session
from codegen.sdk.enums import ProgrammingLanguage
if TYPE_CHECKING:
    from codegen.sdk.typescript.file import TSFile

def test_import_edge_case(tmpdir) -> None:
    # language=typescript
    content = """
import './module.js'

const require = () => 'result'
const __dirname = 'something'
const __filename = 'something/else'

it('should allow declaring CJS globals in ESM', () => {
  expect(require()).toBe('result')
  expect(__dirname).toBe('something')
  expect(__filename).toBe('something/else')
})
    """
    with get_codebase_session(tmpdir=tmpdir, files={"file.ts": content}, programming_language=ProgrammingLanguage.TYPESCRIPT) as codebase:
        file: TSFile = codebase.get_file("file.ts")
        assert len(file.imports) == 1