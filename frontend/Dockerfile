# ベースイメージの選択
FROM node:20-slim AS base

# 作業ディレクトリの設定
WORKDIR /app

# 依存関係ファイルのコピー
COPY package*.json ./

# 開発用の依存関係をインストール
RUN npm ci

# ソースコードのコピー
COPY . .

# 開発サーバーのポートを公開
EXPOSE 5173

# 開発サーバーを起動
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"] 