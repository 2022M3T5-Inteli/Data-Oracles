# Imagem do pipeline. Em 2022 o Dockerfile subia uma API Flask; agora roda o pipeline em lote.
FROM python:3.11-slim

# libgomp1 é exigida pelo LightGBM
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar primeiro o que muda pouco: se só o código mudar, as dependências vêm do cache.
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir -e .

COPY configs ./configs

RUN useradd --create-home oraculo && chown -R oraculo /app
USER oraculo

ENV MLFLOW_DISABLE_AGENT_HINT=1

ENTRYPOINT ["python", "-m", "oraculo.pipeline"]
CMD ["--config", "configs/config.yaml"]
