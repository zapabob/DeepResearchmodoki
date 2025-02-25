# Web Deep Research System

Web上の情報を深層的にリサーチ・解析し、有用な知見を抽出するシステム。

## 技術スタック

### フロントエンド
- Next.js 14
- TypeScript
- Tailwind CSS
- D3.js（知識グラフの可視化）

### バックエンド
- Node.js + Express
- TypeScript
- Google AI Studio (Gemini Pro)
- Langchain
- Neo4j（知識グラフDB）
- Redis（キャッシュ）

## セットアップ

### 必要条件
- Node.js 18以上
- Docker Desktop
- Google AI Studio APIキー

### インストール

1. リポジトリのクローン:
```bash
git clone https://github.com/yourusername/web-deep-research.git
cd web-deep-research
```

2. 環境変数の設定:
```bash
cp .env.example .env
# .envファイルを編集してAPIキーなどを設定
```

3. 依存関係のインストール:
```bash
# バックエンド
cd backend
npm install

# フロントエンド
cd ../frontend
npm install
```

### 開発環境の起動

1. Dockerコンテナの起動:
```bash
docker-compose up -d
```

2. バックエンドの起動:
```bash
cd backend
npm run dev
```

3. フロントエンドの起動:
```bash
cd frontend
npm run dev
```

アプリケーションは以下のURLでアクセスできます：
- フロントエンド: http://localhost:3000
- バックエンドAPI: http://localhost:3001

## 機能

- Web情報の深層検索と解析
- Chain of Thoughtによる仮説検証
- 知識グラフの自動生成
- インタラクティブな可視化
- キャッシングによる高速なレスポンス

## API

### 検索API
- POST /api/search - 基本的な検索
- POST /api/deepresearch - 深層リサーチの実行
- POST /api/llm_summary - 検索結果の要約生成

## ライセンス

MIT

## 貢献

1. Forkを作成
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチをPush (`git push origin feature/amazing-feature`)
5. Pull Requestを作成
