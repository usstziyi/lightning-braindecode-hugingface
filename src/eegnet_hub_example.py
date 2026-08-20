from __future__ import annotations

import argparse
from ast import Return
import os

import torch
from huggingface_hub import login

from braindecode import EEGClassifier
from braindecode.datasets import MOABBDataset
from braindecode.models import EEGNet
from braindecode.preprocessing import (
    Filter,
    PickTypes,
    Preprocessor,
    Resample,
    Rescale,
    create_windows_from_events,
    exponential_moving_standardize,
    preprocess,
)

def get_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    elif torch.backends.mps.is_available():
        return torch.device("mps")  # Apple Silicon GPU 加速
    else:
        return torch.device("cpu")

def hub_logged_in():
    token = os.environ.get("HF_TOKEN")
    if token:
        login(token=token)


def train_model():
    dataset = MOABBDataset(dataset_name="BNCI2014_001")
    preprocess(
        dataset,
        [
            PickTypes(eeg=True, stim=False, verbose=False),
            Rescale(scalings={"eeg": 1e6}),  # V→µV（mne.io.Raw.rescale 包装，可序列化）
            Filter(l_freq=4.0, h_freq=38.0, verbose=False),
            Resample(sfreq=128, verbose=False),
            Preprocessor(
                exponential_moving_standardize,
                factor_new=1e-3,
                init_block_size=1000,
            ),
        ],
    )

    n_runs = len(dataset.datasets)         # 总run数
    n_valid = max(1, round(n_runs * 0.2))  # 20% 用于验证
    n_train = n_runs - n_valid             # 剩余用于训练
    splits = dataset.split(
        by={
            "train": list(range(n_train)),
            "valid": list(range(n_train, n_runs)),
        }
    )
    train_dataset, valid_dataset = splits["train"], splits["valid"]

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

    device = get_device()
    clf = EEGClassifier(
        module="EEGNet",
        criterion=torch.nn.CrossEntropyLoss,
        optimizer=torch.optim.AdamW,
        batch_size=16,
        max_epochs=5,
        train_split=None,  # 已手动划分好 train/valid
        device=device,
    )

    clf.fit(train_windows, y=None)

    model = clf.module_  # fit 后即为按名称解析并初始化好的 EEGNet

    def acc(windows):
        y_true = windows.get_metadata()["target"].to_numpy()
        y_pred = clf.predict(windows)
        return float((y_pred == y_true).mean())

    print(f"train acc = {acc(train_windows):.4f}")
    print(f"valid acc = {acc(valid_windows):.4f}")
    return model


def push_model(model: EEGNet):
    hub_logged_in()

    # 权重会保存为 model.safetensors / pytorch_model.bin，
    # 所有 EEGNet 的 __init__ 签名参数，会随 config.json 一起上传。
    model.push_to_hub(
        repo_id=f"usst-ziyi/eegnet-bnci2014-001",
        commit_message=f"EEGNet trained on BNCI2014_001",
        private=True, # 私有仓库
    )

def load_model(repo_id: str):
    hub_logged_in()
    device = get_device()
    model = EEGNet.from_pretrained(
        repo_id, 
        map_location="cpu"
    ).to(device)

    model.eval() # 这句可以省略，因为模型默认就是 eval 模式了
    with torch.no_grad():
        x = torch.randn(1, model.n_chans, model.n_times, device=device)
        out = model(x)
        print(out)
    return model


def main():
    model = train_model()
    print(model.get_config())
    push_model(model)
    model = load_model(f"usst-ziyi/eegnet-bnci2014-001")
    print(model.get_config())


if __name__ == "__main__":
    main()