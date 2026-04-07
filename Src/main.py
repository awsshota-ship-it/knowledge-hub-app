import os
import uuid
from fastapi import FastAPI
from pydantic import BaseModel
from openai import AzureOpenAI  # Google から Azure OpenAI に変更
from pinecone import Pinecone
from mangum import Mangum

# 1. 初期化
app = FastAPI()
handler = Mangum(app)

# 環境変数から取得（Azure 用の変数を追加してください）
AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
CHAT_DEPLOYMENT = os.environ.get("CHAT_DEPLOYMENT_NAME") # 例: "gpt-4o"
EMBED_DEPLOYMENT = os.environ.get("EMBEDDING_DEPLOYMENT_NAME") # 例: "text-embedding-3-small"

PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME")

# エラーチェック
required_vars = {
    "AZURE_OPENAI_API_KEY": AZURE_OPENAI_API_KEY,
    "AZURE_OPENAI_ENDPOINT": AZURE_OPENAI_ENDPOINT,
    "CHAT_DEPLOYMENT_NAME": CHAT_DEPLOYMENT,
    "EMBEDDING_DEPLOYMENT_NAME": EMBED_DEPLOYMENT,
    "PINECONE_API_KEY": PINECONE_API_KEY,
    "PINECONE_INDEX_NAME": PINECONE_INDEX_NAME
}

missing_vars = [name for name, value in required_vars.items() if not value]

if missing_vars:
    raise ValueError(f"以下の環境変数が設定されていません: {', '.join(missing_vars)}")

# Azure OpenAI クライアントの初期化
client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version="2025-04-01-preview", # 必要に応じてバージョンを調整
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

class QueryRequest(BaseModel):
    prompt: str

class SaveRequest(BaseModel):
    text: str
    tags: list[str] = []

@app.get("/")
def root():
    return {"status": "running", "message": "Knowledge Hub API (Azure Powered)"}

@app.post("/save")
def save_knowledge(req: SaveRequest):
    # Azure OpenAI で Embedding
    res = client.embeddings.create(
        input=[req.text],
        model=EMBED_DEPLOYMENT
    )
    vector = res.data[0].embedding
    
    doc_id = str(uuid.uuid4())
    index.upsert(vectors=[{
        "id": doc_id, 
        "values": vector, 
        "metadata": {
            "text": req.text,
            "tags": req.tags  # ここでタグを保存！
        }
    }])
    
    return {"message": "Saved successfully", "id": doc_id}

@app.post("/ask")
def ask_question(req: QueryRequest):
    # 1. 質問をベクトル化 (Azure 版)
    res = client.embeddings.create(
        input=[req.prompt],
        model=EMBED_DEPLOYMENT
    )
    query_vector = res.data[0].embedding

    # 2. Pinecone から検索
    search_results = index.query(vector=query_vector, top_k=3, include_metadata=True)
    
    if not search_results['matches']:
        return {"answer": "関連するメモが見つかりませんでした。", "sources": []}

    context_text = "\n".join([m['metadata']['text'] for m in search_results['matches']])
    
    # 3. Azure OpenAI (GPT-4o 等) に回答を依頼
    rag_prompt = f"""
    あなたはユーザーの記憶を補助する優秀なアシスタントです。
    【参考資料】の内容に基づいて、質問に答えてください。
    資料に答えが含まれていない場合は、「その情報のメモはまだありません」と答えてください。

    【参考資料】:
    {context_text}

    【質問】:
    {req.prompt}
    """
    
    response = client.chat.completions.create(
        model=CHAT_DEPLOYMENT,
        messages=[
            {"role": "system", "content": "あなたは優秀なアシスタントです。"},
            {"role": "user", "content": rag_prompt}
        ]
    )
    
    return {
        "answer": response.choices[0].message.content,
        "sources": [m['metadata']['text'] for m in search_results['matches']]
    }