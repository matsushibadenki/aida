# path: aida/conftest.py
# title: Pytest Configuration Fixtures
# role: Modifies Python's system path during test sessions to ensure modules are found.

import sys
from pathlib import Path

# プロジェクトのルートディレクトリを取得
# (conftest.pyが aida/ にあるので、その親ディレクトリ)
project_root = Path(__file__).parent.parent

# テスト実行時に、ワークスペースとサンドボックスのパスをsys.pathに追加する
# これにより、テストファイルは常にモジュールを正しくインポートできる
workspace_path = project_root / 'aida' / 'workspace'
sandbox_path = project_root / 'aida' / 'aida_sandbox'

sys.path.insert(0, str(workspace_path))
sys.path.insert(0, str(sandbox_path))