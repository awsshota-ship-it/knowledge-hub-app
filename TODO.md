# 🚀 Project: My Personal Knowledge RAG (Azure OpenAI Edition)

自分自身の学習メモや技術スタックを保存し、Azure上の強力なLLMに「自分の知識ベース」で回答・整理させるためのサーバーレスRAGシステム。

---

## 1. 現状のステータス（Done）

### ✅ インフラストラクチャ
- **LLM**: Azure OpenAI Service (**GPT-5.4-mini**) 接続済み
- **Embedding**: Azure OpenAI (**text-embedding-3-small**) 
- **Vector DB**: Pinecone (Serverless) 構築済み
  - **Dimension**: **1536** (Azure Embeddingモデル `text-embedding-3-small` に最適化)
  - **Metric**: Cosine Similarity
- **Cloud**: Azure AI Foundry リソース活用

### ✅ コアロジック（ローカル検証済）
- `openai` (AzureOpenAI) & `pinecone` 最新SDKを用いた実装
- **429 Resource Exhausted (制限)**: Google AI Studio の無料枠制限を Azure 移行により回避
- **400 Bad Request (次元数不一致)**: Pinecone Index を 3072 → 1536 に再作成して解決
- **RAG動作確認**: 
    - 既知の情報の抽出（神戸のステーキハウス等）に成功
    - 未知の質問に対する「メモがありません」というガードレール動作を確認

---

## 2. システムアーキテクチャ

運用コストを管理しつつ、高精度な回答を実現するエンタープライズ級の構成。

- **Frontend**: AWS Amplify (将来予定)
- **Backend API**: Python + FastAPI + Mangum (Uvicorn起動)
- **Embedding**: text-embedding-3-small (**1536 dim**)
- **Reasoning**: **GPT-5.4-mini** (Azure Deployment)
- **Database**: Pinecone Index (`gemini-rag-no1`)

---

## 3. 今後の開発ロードマップ

### Phase 1: APIサーバーのブラッシュアップ
- [x] Azure OpenAI SDK への完全移植
- [x] 知らないことは「知らない」と答えるガードレールの実装
- [ ] `/delete` エンドポイントの実装（特定のメモをID指定で削除）

### Phase 2: AWS Lambda デプロイ
- [ ] `requirements.txt` の整備（`openai`, `fastapi`, `pinecone-client`, `mangum`）
- [ ] Lambda関数へのデプロイと環境変数のセキュアな管理
- [ ] API Gateway のエンドポイント公開

### Phase 3: 知識の「蒸留 (Distillation)」とメンテナンス
- [ ] **知識の正規化**: 重複するメモをGPTに投げ、1つの体系的なドキュメントにまとめ直す
- [ ] **自動サマリー**: 日々の断片的なメモを週次で要約するバッチ処理の実装

---

## 4. 運用環境変数（PowerShell）

セッション開始時に以下の変数をセットして使用。

```powershell
# 実行ポリシーの変更（必要に応じて）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force

# Azure OpenAI 設定
$env:AZURE_OPENAI_API_KEY = "YOUR_API_KEY"
$env:AZURE_OPENAI_ENDPOINT = "[https://your-resource-name.openai.azure.com/](https://your-resource-name.openai.azure.com/)"
$env:CHAT_DEPLOYMENT_NAME = "gpt-5.4-mini"
$env:EMBEDDING_DEPLOYMENT_NAME = "text-embedding-3-small"

# Pinecone 設定
$env:PINECONE_API_KEY = "YOUR_PINECONE_KEY"
$env:PINECONE_INDEX_NAME = "gemini-rag-no1"

# サーバー起動
uvicorn main:app --reload
```

## 備考
タグ検索機能: /ask の時に「muscle タグが付いている知識の中からだけ探す」といったフィルタリングを実装する。

作成者（User）の記録: metadata に "user": "ore" のように名前を入れる。

Reactフロントエンド: テキストボックスとタグ入力欄（チップス形式）を作って、スマホからサクッと登録できるようにする。