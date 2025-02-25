# Web Deep Research

ウェブ全体の詳細検索とChain-of-Thought（CoT）による仮説検証思考を行うツールです。

## 概要

Web Deep Researchは、特定のトピックに関する詳細な調査を自動化するツールです。Google Gemini APIを活用して、ウェブ検索結果を分析し、Chain-of-Thought（CoT）推論によって複数の仮説を検証します。

## 機能

- **ウェブクローリング**: 指定されたクエリに基づいてウェブ検索を行い、結果を収集します。
- **テキスト分析**: Google Gemini APIを使用して、収集したテキストを分析します。
- **Chain-of-Thought推論**: 複数の仮説を立て、検証するプロセスを実行します。
- **結果の保存**: 分析結果をJSON形式で保存します。
- **Webインターフェース**: Next.jsとChakra UIを使用したモダンなWebインターフェースを提供します。

### Chain-of-Thought Deep Research

Chain-of-Thought（CoT）Deep Researchは、通常のDeep Researchをさらに強化し、以下のステップで詳細な分析を行います：

1. **検索結果の整理**: 情報源の信頼性、関連性、最新性を評価
2. **主要な事実の抽出**: 各検索結果から事実、主張、データポイントを抽出
3. **複数の仮説の形成**: 抽出した事実に基づいて複数の仮説を形成
4. **仮説の検証**: 各仮説について支持する証拠と反証する証拠を評価
5. **最も可能性の高い結論**: 証拠の評価に基づいて結論を導出
6. **追加調査が必要な領域**: 結論を強化するために必要な追加調査を特定

分析の深さは3段階（基本、詳細、高度）から選択可能で、より深い分析では情報源のバイアスや視点の違い、時系列的な変化、複数の視点からの検討なども行います。

## プロジェクト構成

```
web-deep-research/
├─ .env.example                   ← 環境変数定義ファイルのサンプル
├─ .gitignore                     ← Gitの除外ファイル設定
├─ README.md                      ← プロジェクトの説明書
├─ docker-compose.yml             ← Dockerコンテナ設定
├─ package.json                   ← プロジェクト全体の依存関係
├─ start-all.bat                  ← Windows用起動スクリプト
├─ start-all.ps1                  ← PowerShell用起動スクリプト
├─ backend/                       ← バックエンド関連のコード
│  ├─ __init__.py
│  ├─ main.py                     ← FastAPIサーバーのエントリーポイント
│  ├─ requirements.txt            ← バックエンド依存関係
│  ├─ Dockerfile                  ← バックエンドのDockerfile
│  ├─ routes/                     ← FastAPIルーターなどのエンドポイント定義
│  └─ services/                   ← 各サービス（crawler, gemini, graph, orchestratorなど）
│     ├─ crawler.py               ← ウェブクローリングサービス
│     ├─ gemini.py                ← Google Gemini API連携サービス
│     ├─ graph.py                 ← グラフ生成サービス
│     ├─ cot_deepresearch.py      ← Chain-of-Thought分析サービス
│     └─ orchestrator.py          ← サービス間連携
├─ frontend/                      ← フロントエンド関連のコード
│  ├─ package.json                ← フロントエンド依存関係
│  ├─ next.config.js              ← Next.js設定ファイル
│  ├─ tsconfig.json               ← TypeScript設定ファイル
│  ├─ .env.example                ← フロントエンド環境変数のサンプル
│  ├─ Dockerfile                  ← フロントエンドのDockerfile
│  ├─ public/                     ← 静的ファイル
│  ├─ pages/                      ← Next.jsのページコンポーネント
│  │  ├─ _app.tsx                 ← Next.jsアプリケーションのルート
│  │  └─ index.tsx                ← トップページ
│  └─ src/                        ← ソースコード
│     ├─ components/              ← Reactコンポーネント
│     │  ├─ ApiHealthCheck.tsx    ← APIヘルスチェックコンポーネント
│     │  ├─ DeepResearch.tsx      ← 深層リサーチコンポーネント
│     │  ├─ Footer.tsx            ← フッターコンポーネント
│     │  ├─ Header.tsx            ← ヘッダーコンポーネント
│     │  └─ ResultsDisplay.tsx    ← 結果表示コンポーネント
│     ├─ services/                ← APIサービス
│     │  └─ api.ts                ← バックエンドAPI連携
│     └─ types/                   ← TypeScript型定義
│        ├─ research.ts           ← リサーチ関連の型定義
│        └─ search.ts             ← 検索関連の型定義
├─ scripts/                       ← ユーティリティスクリプト
│  ├─ cot_deepresearch.py         ← CoT深層リサーチスクリプト
│  ├─ deepresearch.py             ← 深層リサーチスクリプト
│  └─ run_integration_python.py   ← 統合実行スクリプト
└─ docs/                          ← ドキュメント
   ├─ api/                        ← API仕様書
   └─ setup/                      ← セットアップガイド
```

## セットアップ

### 前提条件

- Node.js 18.x以上
- Python 3.8以上
- Google Gemini API キー

### 環境変数の設定

1. プロジェクトのルートディレクトリに`.env`ファイルを作成し、以下の内容を設定します：

```
# API Keys
GOOGLE_AISTUDIO_API_KEY=your_gemini_api_key_here

# Backend Settings
BACKEND_PORT=8002
ENABLE_CORS=true
LOG_LEVEL=INFO

# Frontend Settings
NEXT_PUBLIC_API_URL=http://localhost:8002
```

2. フロントエンドディレクトリに`.env.local`ファイルを作成し、以下の内容を設定します：

```
NEXT_PUBLIC_API_URL=http://localhost:8002
NODE_ENV=development
```

### インストール

1. プロジェクト全体の依存関係をインストールします：

```bash
npm install
```

2. バックエンドの依存関係をインストールします：

```bash
cd backend
pip install -r requirements.txt
```

3. フロントエンドの依存関係をインストールします：

```bash
cd frontend
npm install
```

## 実行方法

### 開発環境での実行

1. バックエンドサーバーを起動します：

```bash
cd backend
python main.py
```

2. フロントエンドの開発サーバーを起動します：

```bash
cd frontend
npm run dev
```

3. ブラウザで http://localhost:3005 にアクセスして、アプリケーションを使用します。

### 統合スクリプトを使用した実行（Windows）

Windowsでは、以下のスクリプトを使用して両方のサーバーを同時に起動できます：

```bash
# PowerShellスクリプト
.\start-all.ps1

# または、バッチファイル
start-all.bat
```

### Docker Composeを使用した実行

```bash
docker-compose up -d
```

## トラブルシューティング

### ポートが既に使用されている場合

バックエンドサーバーの起動時に「ポートが既に使用されています」というエラーが表示される場合は、以下のコマンドを実行して該当するプロセスを終了してください：

```bash
# Windowsの場合
netstat -ano | findstr :8002
taskkill /F /PID <プロセスID>

# PowerShellの場合
Get-NetTCPConnection -LocalPort 8002 | Select-Object -Property OwningProcess
Stop-Process -Id <プロセスID> -Force

# Linuxの場合
lsof -i :8002
kill -9 <プロセスID>
```

### フロントエンドの依存関係エラー

フロントエンドの依存関係に関するエラーが発生した場合は、以下のコマンドを実行してください：

```bash
cd frontend
npm install --force
```

### Gemini APIのエラー

Gemini APIに関するエラーが発生した場合は、`.env`ファイルの`GOOGLE_AISTUDIO_API_KEY`が正しく設定されていることを確認してください。

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 貢献

バグ報告や機能リクエストは、GitHubのIssueを通じてお願いします。プルリクエストも歓迎します。 