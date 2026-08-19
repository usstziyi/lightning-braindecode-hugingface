"""EEGNet × Hugging Face Hub 示例：在真实 BNCI2014_001 数据上训练并推送。

演示 braindecode 1.x 的完整流程：
  1. 用 MOABBDataset 加载 BNCI2014_001（即 BCI Competition IV 2a，4 类运动想象）
  2. 预处理：丢弃 EOG/刺激通道、4–38 Hz 带通滤波
  3. create_windows_from_events 切出 4 秒（1000 采样点）的 trial 窗口
  4. 用 EEGClassifier（skorch）训练 EEGNet
  5. push_to_hub() 把模型（权重 + config.json）推到 Hugging Face Hub
  6. from_pretrained() 从 Hub 加载模型，并验证输出一致

用法：
    # 本地完整流程（下载数据 + 预处理 + 训练 + 评估，不需要 token / 网络推送）
    uv run python eegnet_hub_example.py

    # 训练后推送到自己的仓库（需要先登录）
    HF_TOKEN=hf_xxx uv run python eegnet_hub_example.py --push \
        --repo-id your-username/eegnet-bnci2014-001

    # 从 Hub 加载任意 EEGNet 权重（跳过训练）
    uv run python eegnet_hub_example.py --load your-username/eegnet-bnci2014-001
"""

from __future__ import annotations

import argparse
import os

import torch
from numpy import multiply
from huggingface_hub import login

from braindecode import EEGClassifier
from braindecode.datasets import MOABBDataset
from braindecode.models import EEGNet
from braindecode.preprocessing import (
    Filter,
    PickTypes,
    Resample,
    Preprocessor,
    create_windows_from_events,
    exponential_moving_standardize,
    preprocess,
)

# BNCI2014_001（BCI Competition IV 2a）：4 类运动想象，22 导 EEG + 3 导 EOG。


def train_evaluate(subject_id: int, max_epochs: int):
    """加载 → 预处理 → 按 run 划分 → 切窗 → 训练 → 评估，返回模型与分类器。"""
    # 1) 加载 BNCI2014_001 单被试数据
    print(f"[数据] 加载 BNCI2014_001，被试 {subject_id} ...")
    dataset = MOABBDataset(dataset_name="BNCI2014_001", subject_ids=[subject_id])

    # 2) 预处理：保留 EEG 通道、V→µV、4–38 Hz 带通、重采样到 128 Hz、指数移动标准化
    def scale_to_microvolt(data):
        return multiply(data, 1e6)

    preprocess(
        dataset,
        [
            PickTypes(eeg=True, stim=False, verbose=False),
            Preprocessor(scale_to_microvolt),
            Filter(l_freq=4.0, h_freq=38.0, verbose=False),
            Resample(sfreq=128, verbose=False),
            Preprocessor(
                exponential_moving_standardize,
                factor_new=1e-3,
                init_block_size=1000,
            ),
        ],
    )

    # 3) 按 run 划分 train/valid（每个 run 都含全部 4 类，天然类平衡）
    n_runs = len(dataset.datasets)
    n_valid = max(1, round(n_runs * 0.2))
    n_train = n_runs - n_valid
    splits = dataset.split(
        by={"train": list(range(n_train)), "valid": list(range(n_train, n_runs))}
    )
    train_dataset, valid_dataset = splits["train"], splits["valid"]

    # 4) 按 event 切 4 秒（512 采样点）窗口
    def make_windows(ds):
        return create_windows_from_events(
            ds,
            trial_start_offset_samples=0,
            trial_stop_offset_samples=0,
            window_size_samples=512,
            window_stride_samples=512,
            preload=True,
        )

    train_windows = make_windows(train_dataset)
    valid_windows = make_windows(valid_dataset)
    print(f"       窗口数 train={len(train_windows)} valid={len(valid_windows)}")

    # 5) 最新接口：直接以字符串 "EEGNet" 作为 module，信号参数 fit 时自动推断
    if torch.cuda.is_available():
        device = "cuda"
    elif torch.backends.mps.is_available():
        device = "mps"  # Apple Silicon GPU 加速
    else:
        device = "cpu"
    clf = EEGClassifier(
        module="EEGNet",
        criterion=torch.nn.CrossEntropyLoss,
        optimizer=torch.optim.AdamW,
        batch_size=16,
        max_epochs=max_epochs,
        train_split=None,  # 已手动划分好 train/valid
        device=device,
    )
    print(
        f"[训练] EEGClassifier(module='EEGNet', max_epochs={max_epochs}, "
        f"device={clf.device}) ..."
    )
    clf.fit(train_windows, y=None)

    model = clf.module_  # fit 后即为按名称解析并初始化好的 EEGNet
    print(
        f"[模型] n_outputs={model.n_outputs}, "
        f"参数量={sum(p.numel() for p in model.parameters()):,}"
    )

    # 6) 评估准确率
    def acc(windows):
        y_true = windows.get_metadata()["target"].to_numpy()
        y_pred = clf.predict(windows)
        return float((y_pred == y_true).mean())

    print(f"       train acc = {acc(train_windows):.4f}")
    print(f"       valid acc = {acc(valid_windows):.4f}")
    return model, clf


def ensure_logged_in() -> None:
    """如果设置了 HF_TOKEN，就用它登录（也可以先用 huggingface-cli login）。"""
    token = os.environ.get("HF_TOKEN")
    if token:
        login(token=token)


def push_demo(repo_id: str, subject_id: int, max_epochs: int) -> None:
    """训练 → 推送到 Hub → 重新加载回来验证。"""
    ensure_logged_in()

    model, clf = train_evaluate(subject_id, max_epochs)

    print(f"[推送] push_to_hub(repo_id={repo_id!r}) ...")
    # 权重会保存为 model.safetensors / pytorch_model.bin，
    # 所有 __init__ 参数会随 config.json 一起上传。
    clf.module_.push_to_hub(
        repo_id=repo_id,
        commit_message=f"EEGNet trained on BNCI2014_001 (subject {subject_id})",
        private=True,  # 先推私有仓库，确认无误后再改成 False 公开
    )
    print("      推送完成:", f"https://huggingface.co/{repo_id}")

    print("[回读] from_pretrained() 重新加载并验证 ...")
    device = next(clf.module_.parameters()).device  # 与训练设备一致（cuda/mps/cpu）
    # safetensors 的 map_location 不支持 mps，故先加载到 cpu 再移到目标设备
    loaded = EEGNet.from_pretrained(repo_id, map_location="cpu").to(device)
    clf.module_.eval()
    loaded.eval()

    with torch.no_grad():
        x = torch.randn(2, model.n_chans, model.n_times, device=device)
        out_orig = clf.module_(x)
        out_loaded = loaded(x)

    assert torch.allclose(out_orig, out_loaded, atol=1e-6), "权重不一致！"
    print(f"      输出形状一致，最大误差 = {(out_orig - out_loaded).abs().max().item():.2e}")

    # 分类头自动重建：指定别的类别数加载
    reloaded_4 = EEGNet.from_pretrained(repo_id, n_outputs=4)
    print(f"      换 n_outputs 重新加载后类别数: {reloaded_4.n_outputs}")


def load_demo(repo_id: str) -> None:
    """从 Hub 加载模型并跑一次推理。"""
    ensure_logged_in()
    print(f"加载 {repo_id} ...")
    model = EEGNet.from_pretrained(repo_id, map_location="cpu")
    model.eval()

    with torch.no_grad():
        x = torch.randn(1, model.n_chans, model.n_times)
        out = model(x)

    print(f"n_outputs = {model.n_outputs}")
    print(f"输入形状 {tuple(x.shape)} -> 输出形状 {tuple(out.shape)}")
    print("预测 logits:", out[0].tolist())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--subject", type=int, default=1, help="要加载的被试编号（默认 1）"
    )
    parser.add_argument(
        "--max-epochs", type=int, default=4, help="训练轮数（默认 4，便于快速演示）"
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help="训练后把模型推送到 Hugging Face Hub（需要 token）",
    )
    parser.add_argument(
        "--repo-id",
        default="your-username/eegnet-bnci2014-001",
        help="Hub 仓库 ID，例如 username/eegnet-bnci2014-001",
    )
    parser.add_argument(
        "--load",
        metavar="REPO_ID",
        help="直接从 Hub 加载这个仓库的 EEGNet，跳过训练",
    )
    args = parser.parse_args()

    if args.load:
        load_demo(args.load)
    elif args.push:
        push_demo(args.repo_id, args.subject, args.max_epochs)
    else:
        # 纯本地演示：下载 + 预处理 + 切窗 + 训练 + 评估，不联网推送
        model, _ = train_evaluate(args.subject, args.max_epochs)
        print("模型配置（也会随 push_to_hub 自动保存到 config.json）:")
        print(model.get_config())
        print("\n现在可以运行：")
        print(
            f"  uv run python eegnet_hub_example.py --push "
            f"--repo-id {args.repo_id} --subject {args.subject}"
        )


if __name__ == "__main__":
    main()