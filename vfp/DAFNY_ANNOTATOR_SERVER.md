# dafny-annotator Server

The [dafny-annotator](https://github.com/metareflection/dafny-annotator) server can be run on a cluster and tunneled over HTTP with ngrok or cloudflare.

A local alternative is to convert the fine-tuned model to MLX and run locally on mac.

The `llm.py` can can be configured for MLX.

Then the `annotator_server` server can be run using `uvicorn` like the dafny-annotator one.
This simplified server assumes the localized variant and no rationales.

## Quick cheat sheet to convert from a huggingface a peft model to MLX

Run this Python script to create a standalone model from a peft model:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

base_model = AutoModelForCausalLM.from_pretrained("meta-llama/Meta-Llama-3.1-8B")
model = PeftModel.from_pretrained(base_model, "vfp-finetuned_Meta-Llama-3.1-8B-peft")
merged_model = model.merge_and_unload()
merged_model.save_pretrained("vfp-finetuned_Meta-Llama-3.1-8B")
```

Also copy the tokenizer to the model directory. Download it as follows:
```python
>>> from huggingface_hub import hf_hub_download
>>> hf_hub_download("meta-llama/Meta-Llama-3.1-8B", "tokenizer.json")
>>> hf_hub_download("meta-llama/Meta-Llama-3.1-8B", "tokenizer_config.json")
```

Finally, convert:
```
mlx_lm.convert --hf-path vfp-finetuned_Meta-Llama-3.1-8B --mlx-path vfp-finetuned_Meta-Llama-3.1-8B-mlx
```

## Alternative quick cheatsheet

Push the full model to huggingface:
```
huggingface-cli upload $MODEL_USER_NAME $MODEL_LOCAL_PATH .
```

On mac, convert the model to MLX:
```
python -m mlx_lm.convert --hf-path $MODEL_USER_NAME
```

You might need to add a `README.md`. You can clone the repo to add with:
```
GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 https://huggingface.co/$MODEL_USER_NAME
```
