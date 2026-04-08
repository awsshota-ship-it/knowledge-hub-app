import os
from pinecone import Pinecone

# 環境変数から取得（以前設定したものを使用）
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME")

def clear_index():
    if not PINECONE_API_KEY or not PINECONE_INDEX_NAME:
        print("エラー: 環境変数が設定されていません。")
        return

    # Pinecone初期化
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX_NAME)

    print(f"Index: {PINECONE_INDEX_NAME} の全データを削除しています...")

    try:
        # デフォルトネームスペースの全ベクトルを削除
        # namespaceを指定している場合は、namespace='your-name' を追加してください
        index.delete(delete_all=True)
        print("✅ 削除リクエストが完了しました。")
        print("※ 反映まで数秒〜数十秒かかる場合があります。")
        
        # 現在の統計を表示
        stats = index.describe_index_stats()
        print(f"現在のステータス: {stats}")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    clear_index()