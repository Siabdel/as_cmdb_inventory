#!/bin/bash
# lancer-vllm-rtx3060.sh

# Activer l'environnement virtuel
source /home/django/Depots/www/projets/envCMDBIventory/bin/activate

# Option A : DeepSeek-V2-Lite (si tu veux tester)
# python -m vllm.entrypoints.openai.api_server \
#   --model deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct \
#   --model Qwen/Qwen2.5-Coder-14B-Instruct-AWQ \
#   --deepseek-ai--DeepSeek-Coder-V2-Lite-Instruct
#   --model Qwen/Qwen2.5-Coder-1.5B-Instruct \
#   -- Qwen/Qwen2.5-Coder-1.5B-Instruct \
#   --port 8001 \
#   --max-model-len 8192 \
#   --dtype auto \
#   --gpu-memory-utilization 0.80 \
#   --host 127.0.0.1 \
#   --trust-remote-code \
#   --enforce-eager
#   --quantization awq \

python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-Coder-14B-Instruct-AWQ \
  --port 8001 \
  --max-model-len 16384 \
  --gpu-memory-utilization 0.80 \
  --dtype float16 \
  --enforce-eager \
  --disable-frontend-multiprocessing \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder \
  --trust-remote-code
