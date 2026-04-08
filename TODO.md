# 🚀 Project: My Personal Knowledge RAG (Azure OpenAI Edition)

自分自身の学習メモや技術スタックを保存し、Azure上の強力なLLMに「自分の知識ベース」で回答・整理させるためのサーバーレスRAGシステム。

---

## 1. 開発進捗ログ (2026-04-07)

### ✅ バックエンド実装完了
- **FastAPI / Mangum**: AWS Lambdaデプロイを見据えたベース実装が完了。
- **CORS設定**: フロントエンド接続のための `CORSMiddleware` を導入。
- **検索・保存ロジック**: Pineconeメタデータフィルタリング（カテゴリ/タグ/ユーザー）を実装。
- **一括要約機能**: `/summarize-category` による、断片的なナレッジのMarkdown化（蒸留）機能を搭載。

### ✅ 開発環境の整備
- **Docker**: ローカル環境に **Dockerをインストール完了**。コンテナ化によるLambdaデプロイの準備が整った。
- **Azure移行**: Google AI Studioの制限を回避し、Azure OpenAI Serviceへの完全移行に成功。

---

## 2. 現状のステータス (Done)

### 🛠️ インフラストラクチャ
- **LLM**: Azure OpenAI Service (**GPT-5.4-mini**) 接続済み
- **Embedding**: Azure OpenAI (**text-embedding-3-small**) / **1536 dim**
- **Vector DB**: Pinecone (Serverless) 構築済み
  - **Metric**: Cosine Similarity

---

## 3. 明日の開発ロードマップ (Phase: Cloud & Frontend)

### 📤 Phase 1: デプロイ & GitHub
- [ ] GitHub リポジトリ作成
- [ ] `main.py`, `requirements.txt`, `Dockerfile` を初Push
- [ ] AWS ECR へのイメージPush & Lambdaデプロイ

### 🎨 Phase 2: フロントエンド構築 (Next.js)
- [ ] **認証**: 合言葉によるシンプルアクセス制限
- [ ] **UI**: カテゴリ別タブ切り替え & Markdown表示エリアの実装
- [ ] **AI連携**: `/ask` による回答と、`/summarize-category` によるマニュアル自動生成

---

## 4. 運用・検証用メモ (PowerShell)

```powershell
# Azure & Pinecone 環境変数
$env:AZURE_OPENAI_API_KEY = "your-key"
$env:AZURE_OPENAI_ENDPOINT = "[https://your-endpoint.openai.azure.com/](https://your-endpoint.openai.azure.com/)"
$env:CHAT_DEPLOYMENT_NAME = "gpt-5.4-mini"
$env:EMBEDDING_DEPLOYMENT_NAME = "text-embedding-3-small"
$env:PINECONE_API_KEY = "your-key"
$env:PINECONE_INDEX_NAME = "gemini-rag-no1"

# Docker ビルド & 起動確認
docker build -t knowledge-hub .
# uvicorn main:app --reload