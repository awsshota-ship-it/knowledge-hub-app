FROM public.ecr.aws/lambda/python:3.11

# 作業ディレクトリの設定
WORKDIR ${LAMBDA_TASK_ROOT}

# 依存ライブラリのコピーとインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ソースコードをコピー
COPY main.py .

# Lambdaのハンドラー（Mangum）を指定
CMD [ "main.handler" ]