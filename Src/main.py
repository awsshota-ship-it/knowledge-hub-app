import os
import uuid
from typing import List, Optional
from fastapi import FastAPI
from pydantic import BaseModel
from openai import AzureOpenAI
from pinecone import Pinecone
from mangum import Mangum

app = FastAPI()
handler = Mangum(app)

# 環境変数の読み込み
AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_VERSION = os.environ.get("AZURE_OPENAI_VERSION")
CHAT_DEPLOYMENT = os.environ.get("CHAT_DEPLOYMENT_NAME")
EMBED_DEPLOYMENT = os.environ.get("EMBEDDING_DEPLOYMENT_NAME")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME")

# エラーチェック
required_vars = {
    "AZURE_OPENAI_API_KEY": AZURE_OPENAI_API_KEY,
    "AZURE_OPENAI_ENDPOINT": AZURE_OPENAI_ENDPOINT,
    "AZURE_OPENAI_VERSION": AZURE_OPENAI_VERSION,
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
    api_version= AZURE_OPENAI_VERSION, # 必要に応じてバージョンを調整
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

# --- モデル定義 ---
class SaveRequest(BaseModel):
    text: str
    tags: List[str] = []
    user: str = "guest" # 誰が登録したか

class QueryRequest(BaseModel):
    prompt: str
    filter_tag: Optional[str] = None # 特定のタグで絞りたい場合
    filter_user: Optional[str] = None # 特定のユーザーで絞りたい場合

# --- エンドポイント ---
@app.get("/")
def root():
    return {"status": "running", "message": "Knowledge Hub API (Azure Powered)"}

@app.post("/save")
def save_knowledge(req: SaveRequest):
    # 1. ベクトル化
    res = client.embeddings.create(input=[req.text], model=EMBED_DEPLOYMENT)
    vector = res.data[0].embedding
    
    # 2. Pineconeへ保存（メタデータを充実させる）
    doc_id = str(uuid.uuid4())
    index.upsert(vectors=[{
        "id": doc_id, 
        "values": vector, 
        "metadata": {
            "text": req.text,
            "tags": req.tags,
            "user": req.user
        }
    }])
    return {"message": "Saved!", "id": doc_id, "tags": req.tags, "user": req.user}

@app.post("/ask")
def ask_question(req: QueryRequest):
    # 1. 質問をベクトル化
    res = client.embeddings.create(input=[req.prompt], model=EMBED_DEPLOYMENT)
    query_vector = res.data[0].embedding

    # 2. フィルタの構築 (Pineconeのメタデータフィルタ)
    # 友達と共有する際、「筋トレ知識だけから探して」という指定が可能になる
    filter_condition = {}
    if req.filter_tag:
        filter_condition["tags"] = {"$in": [req.filter_tag]}
    if req.filter_user:
        filter_condition["user"] = {"$eq": req.filter_user}

    # 3. Pinecone検索 (フィルタ適用)
    search_results = index.query(
        vector=query_vector, 
        top_k=3, 
        include_metadata=True,
        filter=filter_condition if filter_condition else None
    )
    
    if not search_results['matches']:
        return {"answer": "その情報のメモはまだありません。", "sources": []}

    context_text = "\n".join([m['metadata']['text'] for m in search_results['matches']])
    
    # 4. GPT-5.4-mini による回答生成
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