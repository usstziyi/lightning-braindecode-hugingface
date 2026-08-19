# Braindecode × Hugging Face 学习项目

本项目用 [uv](https://docs.astral.sh/uv/) 管理环境，演示 braindecode 如何与
Hugging Face Hub 对接：下载/上传模型权重、加载官方预训练模型并微调。

## 快速开始

```bash
# 1. 创建虚拟环境并安装依赖（会自动下载合适的 Python 版本）
uv sync

# 2. 验证安装
uv run python -c "import braindecode, huggingface_hub; print(braindecode.__version__)"

# 3. 登录 Hugging Face（推送模型时才需要 token）
uv run huggingface-cli login
```

> 推送模型前也可以在命令行设置 `HF_TOKEN` 环境变量。

## 核心用法

### 从 Hub 加载官方预训练模型

```python
from braindecode.models import BENDR

model = BENDR.from_pretrained(
    "braindecode/braindecode-bendr",
    n_outputs=2,
)
```

其他官方权重见
[加载预训练模型示例](https://braindecode.org/dev/auto_examples/model_building/plot_load_pretrained_models.html)，
例如 `braindecode/STEEGFormer-small`、`braindecode/eegpt-pretrained`。
部分外部仓库（如 `brain-bzh/reve-base`）是 gated 模型，需要登录 token。

### 把训练好的模型推到 Hub

```python
from braindecode.models import ShallowFBCSPNet

model = ShallowFBCSPNet(
    n_chans=22, n_outputs=4, n_times=1000,
    input_window_samples=1000, sfreq=250,
)
# 训练...
model.push_to_hub("your-username/my-eeg-model")

# 别人（或另一个环境）这样加载：
loaded = ShallowFBCSPNet.from_pretrained("your-username/my-eeg-model")
```

### 在 Jupyter 中实验

```bash
uv run jupyter lab
```

## 参考链接

- [Braindecode 预训练模型加载示例](https://braindecode.org/dev/auto_examples/model_building/plot_load_pretrained_models.html)
- [Braindecode Hub 数据集集成](https://braindecode.org/dev/generated/braindecode.datasets.bids.HubDatasetMixin.html)
- [Braindecode GitHub](https://github.com/braindecode/braindecode)
- [uv 官方文档](https://docs.astral.sh/uv/)
