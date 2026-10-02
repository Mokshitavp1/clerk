import sys
from huggingface_hub import snapshot_download

repo = sys.argv[1]
path = snapshot_download(
    repo,
    ignore_patterns=["onnx/*", "*.onnx", "*.onnx_data", "imgs/*", "*.md", "*.png"],
)
print("DONE:", path)