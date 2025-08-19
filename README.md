# **AIDA: AI-Driven Assistant**

AIDAは、対話形式でソフトウェア開発タスクを自動化する、自律型AIアシスタントです。ユーザーからの自然言語による指示に基づき、プロジェクトの設計、計画、コーディング、テスト、デバッグ、リファクタリングまでを自律的に実行します。

## **🚀 特徴**

* **自律的なタスク実行**: ユーザーの指示を解釈し、必要なアクション（設計、コーディング、テスト、リント、リファクタリング、コマンド実行など）を自ら計画し、実行します。  
* **自己修正・改善ループ**: テストや静的解析（Lint）で問題が発見された場合、自動的にデバッグエージェントと連携し、コードを修正します。  
* **対話による協調**: ユーザーの指示が曖昧な場合は質問で意図を確認し、大規模な開発の前にはアーキテクチャを設計・提案して承認を求めます。  
* **長期記憶**: 対話の履歴を記憶し、将来のタスク計画に活かします。  
* **安全なサンドボックス環境**: コードの実行やファイル変更は、まず隔離されたサンドボックス環境で行われ、タスク完了後に実際のワークスペースに反映されるため安全です。  
* **クリーンなアーキテクチャ**: DIコンテナ（dependency-injector）を導入し、保守性と拡張性の高い設計になっています。

## **🏁 利用開始までの流れ**

### **1\. 前提条件**

* Python 3.10以上  
* [Ollama](https://ollama.com/)がローカルで実行されていること

Ollamaをインストール後、ターミナルで以下のコマンドを実行して、サーバーを起動し、使用するモデルをダウンロードしてください。

\# Ollamaサーバーを起動 (ターミナルは起動したままにします)  
ollama serve

\# 別のターミナルを開き、モデルをダウンロード  
ollama pull gemma3:latest  
ollama pull nomic-embed-text:latest

### **2\. インストール**

1. プロジェクトの準備:  
   このプロジェクト（aidaディレクトリ）を任意の場所に配置します。  
2. **仮想環境の作成**:  
   python3 \-m venv .venv  
   source .venv/bin/activate  \# Linux/macOS  
   \# または  
   .venv\\Scripts\\activate     \# Windows

3. 依存関係のインストール:  
   プロジェクトルートにあるrequirements.txtを使ってインストールします。  
   pip install \-r requirements.txt

### **3\. 実行方法**

プロジェクトのルートディレクトリ（aidaディレクトリの親）で、以下のコマンドを実行します。

python main.py

実行すると、--- AIDA: AI-Driven Assistant \---というメッセージと共にプロンプトが表示されます。

## **📁 プロジェクト構造**

.  
├── aida/  
│   ├── agents/         \# 各機能担当のエージェント  
│   │   ├── architecture\_agent.py  
│   │   ├── coding\_agent.py  
│   │   ├── debugging\_agent.py  
│   │   ├── dependency\_agent.py  
│   │   ├── execution\_agent.py  
│   │   ├── git\_agent.py  
│   │   ├── linting\_agent.py  
│   │   ├── planning\_agent.py  
│   │   ├── refactoring\_agent.py  
│   │   └── testing\_agent.py  
│   ├── analysis/       \# プロジェクト分析関連  
│   ├── rag/            \# RAG (Retrieval-Augmented Generation) 関連  
│   ├── services/       \# 履歴管理などの共通サービス  
│   ├── workspace/      \# AIDAが作業する対象のプロジェクト  
│   ├── config.yml      \# 設定ファイル  
│   ├── container.py    \# DIコンテナ  
│   ├── llm\_client.py   \# LLM通信クライアント  
│   ├── main.py         \# アプリケーションのエントリーポイント  
│   ├── orchestrator.py \# 全体を統括するオーケストレーター  
│   └── schemas.py      \# データ構造の定義  
└── requirements.txt    \# 依存ライブラリ

## **📄 詳細設計仕様書**

### **1\. アーキテクチャ概要**

本システムは、**エージェントベースアーキテクチャ**を採用しています。中心的な役割を担うOrchestratorが、ユーザーの指示に基づき、各専門分野を担当するAgent群を協調させてタスクを遂行します。クラス間の依存関係は、**DI（Dependency Injection）コンテナ**によって管理されており、各コンポーネントの疎結合性とテスト容易性を高めています。

```Mermaid
graph TD
    subgraph "User Interface"
        UI["main.py Chat Interface"]
    end

    subgraph "Core System"
        Container["DI Container container.py"]
        Orchestrator["Orchestrator"]
    end

    subgraph "Agents"
        Planning["PlanningAgent"]
        Architecture["ArchitectureAgent"]
        Coding["CodingAgent"]
        Refactoring["RefactoringAgent"]
        Linting["LintingAgent"]
        Testing["TestingAgent"]
        Debugging["DebuggingAgent"]
        Execution["ExecutionAgent"]
        Dependency["DependencyAgent"]
        Git["GitAgent"]
        WebSearch["WebSearchAgent"]
    end

    subgraph "Services & LLM"
        History["HistoryManager"]
        LLMClient["LLMClient"]
        Ollama["Ollama gemma3:latest"]
    end

    UI --> Orchestrator
    Container -.-> Orchestrator
    Container -.-> Planning
    Container -.-> Architecture
    Container -.-> Coding
    Container -.-> Refactoring
    Container -.-> Linting
    Container -.-> Testing
    Container -.-> Debugging
    Container -.-> Execution
    Container -.-> Dependency
    Container -.-> Git
    Container -.-> WebSearch
    Container -.-> History

    Orchestrator --> Planning
    Orchestrator --> Architecture
    Orchestrator --> Coding
    Orchestrator --> Refactoring
    Orchestrator --> Linting
    Orchestrator --> Testing
    Orchestrator --> Debugging
    Orchestrator --> Execution
    Orchestrator --> Dependency
    Orchestrator --> Git
    Orchestrator --> WebSearch
    Orchestrator --> History

    Planning --> LLMClient
    Architecture --> LLMClient
    Coding --> LLMClient
    Refactoring --> LLMClient
    Debugging --> LLMClient

    LLMClient --> Ollama
```

### **2\. コンポーネント詳細**

* **main.py**: アプリケーションの起動、DIコンテナの初期化、ユーザーとの対話ループを担当します。  
* **container.py**: システム全体のクラスのインスタンス生成と依存関係の注入を一元管理します。  
* **orchestrator.py**: ユーザーの指示に基づき、PlanningAgentが立てた計画を実行する司令塔。アクションの種類に応じて適切なエージェントを呼び出し、自己修正ループを含む全体のワークフローを制御します。  
* **llm\_client.py**: Ollamaサーバーとの通信をカプセル化するクライアントです。  
* **schemas.py**: エージェント間で交換されるデータ構造（Action, CodeChangeなど）を厳密に定義します。  
* **agents/**:  
  * **planning\_agent.py**: ユーザーの要求とプロジェクトの状態、対話履歴を基に、実行すべきアクションの計画を生成します。  
  * **architecture\_agent.py**: 抽象的な要求に対し、プロジェクトのファイル構造を設計し、ユーザーに提案します。  
  * **coding\_agent.py**: コードの生成・修正案を作成します。  
  * **refactoring\_agent.py**: 既存のコードを分析し、品質を向上させるためのリファクタリング案を生成します。  
  * **linting\_agent.py**: flake8を実行し、コードのスタイルや品質を静的に解析します。  
  * **testing\_agent.py**: pytestを実行し、テスト結果を評価します。  
  * **debugging\_agent.py**: テストやLintのエラーを分析し、自動で修正案を生成します。  
  * **execution\_agent.py**: シェルコマンドを安全なサンドボックス内で実行します。  
  * **dependency\_agent.py**: pipを使い、プロジェクトの依存関係を管理します。  
  * **git\_agent.py**: gitコマンドを実行し、バージョン管理を行います。  
  * **web\_search\_agent.py**: Webを検索し、外部情報を収集します。  
* **services/**:  
  * **history\_manager.py**: 対話履歴の永続化を管理します。

## **🌟 今後のロードマップ**

AIDAは、さらなる自律性と能力の向上を目指し、以下の機能開発を計画しています。

* **自己改善能力の強化**:  
  * **メタ学習**: 過去のタスク成功・失敗パターンを分析し、計画立案能力（プロンプト）を自己改善します。  
  * **知識ベースの構築**: 成功したコードや設計パターンを学習し、新しい問題解決に再利用します。  
* **高度なコード分析**:  
  * **パフォーマンス・セキュリティ分析**: cProfileやbanditのような専門ツールと連携し、パフォーマンスのボトルネックやセキュリティ脆弱性を自動で発見・修正します。  
  * **自動ドキュメント生成**: コード変更に基づき、README.mdやdocstringを自動で更新します。  
* **DevOps自動化**:  
  * **コンテナ化・CI/CD**: DockerfileやGitHub Actionsの設定を自動生成し、開発環境の構築からデプロイまでを自動化します。  
* **高度な協調開発**:  
  * **マルチエージェント・シミュレーション**: 複数の専門エージェント（フロントエンド担当、バックエンド担当など）が協調し、大規模なプロジェクトを並行して開発するシミュレーションを行います。

## **🤝 貢献**

プロジェクトへの貢献を歓迎します。プルリクエストを送信する前に、まずIssueで議論してください。

## **📝 ライセンス**

このプロジェクトは[MIT License](https://www.google.com/search?q=LICENSE)の下で公開されています。
