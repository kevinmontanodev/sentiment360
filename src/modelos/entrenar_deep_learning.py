"""
Entrenamiento y evaluación de un modelo de Deep Learning (BiGRU) con PyTorch.
Historia de Usuario: US-07
"""

import argparse
import json
import os
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from torch.utils.data import DataLoader, Dataset

from src.modelos.texto import normalize_text


# ==========================================
# 1. Vocabulario y Dataset
# ==========================================
class Vocabulary:
    def __init__(self, max_size: int = 15000):
        self.max_size = max_size
        self.pad_token = "<PAD>"
        self.unk_token = "<UNK>"
        self.w2i = {self.pad_token: 0, self.unk_token: 1}
        self.i2w = {0: self.pad_token, 1: self.unk_token}

    def build_vocab(self, texts: list[str]) -> None:
        counter = Counter()
        for text in texts:
            counter.update(text.split())

        for word, _ in counter.most_common(self.max_size - 2):
            idx = len(self.w2i)
            self.w2i[word] = idx
            self.i2w[idx] = word

    def encode(self, text: str, max_len: int = 100) -> list[int]:
        tokens = text.split()[:max_len]
        indices = [self.w2i.get(token, self.w2i[self.unk_token]) for token in tokens]
        if len(indices) < max_len:
            indices += [self.w2i[self.pad_token]] * (max_len - len(indices))
        return indices

    def __len__(self) -> int:
        return len(self.w2i)


class ReviewsDataset(Dataset):
    def __init__(self, texts: list[str], labels: list[int], vocab: Vocabulary, max_len: int = 100):
        self.vocab = vocab
        self.max_len = max_len
        self.data = [
            (self.vocab.encode(normalize_text(t), max_len=self.max_len), l)
            for t, l in zip(texts, labels)
        ]

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        x, y = self.data[idx]
        return torch.tensor(x, dtype=torch.long), torch.tensor(y, dtype=torch.long)


# ==========================================
# 2. Arquitectura de la Red Neuronal (BiGRU)
# ==========================================
class SentimentBiGRU(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        embed_dim: int = 128,
        hidden_dim: int = 64,
        num_classes: int = 5,
        dropout: float = 0.4,
    ):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.gru = nn.GRU(
            embed_dim,
            hidden_dim,
            batch_first=True,
            bidirectional=True,
        )
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_dim * 2, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        embedded = self.dropout(self.embedding(x))
        out, h_n = self.gru(embedded)
        # Concatenar el último estado oculto hacia adelante y hacia atrás
        hidden_cat = torch.cat((h_n[-2, :, :], h_n[-1, :, :]), dim=1)
        logits = self.fc(self.dropout(hidden_cat))
        return logits


# ==========================================
# 3. Early Stopping
# ==========================================
class EarlyStopping:
    def __init__(self, patience: int = 3, delta: float = 1e-4):
        self.patience = patience
        self.delta = delta
        self.counter = 0
        self.best_loss = float("inf")
        self.early_stop = False
        self.best_state = None

    def __call__(self, val_loss: float, model: nn.Module) -> None:
        if val_loss < self.best_loss - self.delta:
            self.best_loss = val_loss
            self.counter = 0
            self.best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True


# ==========================================
# 4. Funciones de Entrenamiento y Evaluación
# ==========================================
def train_one_epoch(
    model: nn.Module,
    dataloader: DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
) -> tuple[float, float]:
    model.train()
    total_loss, correct, total = 0.0, 0, 0
    for x, y in dataloader:
        x, y = x.to(device), y.to(device)
        optimizer.zero_grad()
        logits = model(x)
        loss = criterion(logits, y)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * len(y)
        preds = logits.argmax(dim=1)
        correct += (preds == y).sum().item()
        total += len(y)

    return total_loss / total, correct / total


@torch.no_grad()
def evaluate(
    model: nn.Module,
    dataloader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
) -> tuple[float, float, np.ndarray, np.ndarray]:
    model.eval()
    total_loss, correct, total = 0.0, 0, 0
    all_preds, all_labels = [], []
    for x, y in dataloader:
        x, y = x.to(device), y.to(device)
        logits = model(x)
        loss = criterion(logits, y)

        total_loss += loss.item() * len(y)
        preds = logits.argmax(dim=1)
        correct += (preds == y).sum().item()
        total += len(y)

        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(y.cpu().numpy())

    return total_loss / total, correct / total, np.array(all_preds), np.array(all_labels)


def plot_learning_curves(history: dict, output_path: Path) -> None:
    epochs = range(1, len(history["train_loss"]) + 1)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    axes[0].plot(epochs, history["train_loss"], label="Train Loss", marker="o")
    axes[0].plot(epochs, history["val_loss"], label="Val Loss", marker="o")
    axes[0].set_title("Curva de Pérdida (Loss)")
    axes[0].set_xlabel("Época")
    axes[0].set_ylabel("CrossEntropy Loss")
    axes[0].legend()
    axes[0].grid(True)

    axes[1].plot(epochs, history["train_acc"], label="Train Acc", marker="o")
    axes[1].plot(epochs, history["val_acc"], label="Val Acc", marker="o")
    axes[1].set_title("Curva de Exactitud (Accuracy)")
    axes[1].set_xlabel("Época")
    axes[1].set_ylabel("Accuracy")
    axes[1].legend()
    axes[1].grid(True)

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_confusion_matrix(cm: np.ndarray, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(cm, interpolation="nearest", cmap="Blues")
    ax.figure.colorbar(im, ax=ax)
    classes = [f"Clase {i}" for i in range(5)]
    ax.set(
        xticks=np.arange(cm.shape[1]),
        yticks=np.arange(cm.shape[0]),
        xticklabels=classes,
        yticklabels=classes,
        ylabel="Etiqueta Real",
        xlabel="Predicción",
        title="Matriz de Confusión - BiGRU",
    )
    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(
                j,
                i,
                format(cm[i, j], "d"),
                ha="center",
                va="center",
                color="white" if cm[i, j] > thresh else "black",
            )
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()


# ==========================================
# 5. Punto de Entrada Principal (CLI)
# ==========================================
def main() -> None:
    parser = argparse.ArgumentParser(description="Entrena y evalúa modelo BiGRU en PyTorch (US-07).")
    parser.add_argument("--data-dir", type=Path, default=Path("data/processed/ml_evaluacion"))
    parser.add_argument("--max-train", type=int, default=10000, help="Muestra de entrenamiento (referencia US-06).")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=Path, default=Path("reports/deep_learning"))
    parser.add_argument("--model-dir", type=Path, default=Path("models/deep_learning"))
    args = parser.parse_args()

    # Reproducibilidad
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Dispositivo de ejecución: {device}")

    # Cargar datos respetando la partición estricta
    print("Cargando particiones Parquet...")
    df_train = pd.read_parquet(args.data_dir / "train.parquet")
    if args.max_train and args.max_train < len(df_train):
        df_train = df_train.sample(n=args.max_train, random_state=args.seed).reset_index(drop=True)

    df_val = pd.read_parquet(args.data_dir / "validation.parquet")
    df_test = pd.read_parquet(args.data_dir / "test.parquet")

    print(f"Tamaño Train: {len(df_train)} | Val: {len(df_val)} | Test: {len(df_test)}")

    # Vocabulario ajustado únicamente sobre Train
    vocab = Vocabulary(max_size=15000)
    vocab.build_vocab([normalize_text(t) for t in df_train["text"]])
    print(f"Tamaño del vocabulario: {len(vocab)}")

    train_ds = ReviewsDataset(df_train["text"].tolist(), df_train["label"].tolist(), vocab)
    val_ds = ReviewsDataset(df_val["text"].tolist(), df_val["label"].tolist(), vocab)
    test_ds = ReviewsDataset(df_test["text"].tolist(), df_test["label"].tolist(), vocab)

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False)
    test_loader = DataLoader(test_ds, batch_size=args.batch_size, shuffle=False)

    # Inicializar modelo
    model = SentimentBiGRU(
        vocab_size=len(vocab),
        embed_dim=128,
        hidden_dim=64,
        num_classes=5,
        dropout=0.4,
    ).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr, weight_decay=1e-5)
    early_stopping = EarlyStopping(patience=3)

    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}

    print("\nIniciando entrenamiento...")
    for epoch in range(1, args.epochs + 1):
        train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc, _, _ = evaluate(model, val_loader, criterion, device)

        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(train_acc)
        history["val_acc"].append(val_acc)

        print(
            f"Época [{epoch:02d}/{args.epochs:02d}] "
            f"Train Loss: {train_loss:.4f} - Train Acc: {train_acc:.4f} | "
            f"Val Loss: {val_loss:.4f} - Val Acc: {val_acc:.4f}"
        )

        early_stopping(val_loss, model)
        if early_stopping.early_stop:
            print(f"Early Stopping activado en época {epoch}.")
            break

    # Restaurar mejores pesos del modelo
    if early_stopping.best_state:
        model.load_state_dict(early_stopping.best_state)

    # Evaluación final estricta en el conjunto Test
    print("\nEvaluando en conjunto de prueba (Test)...")
    test_loss, test_acc, y_pred, y_true = evaluate(model, test_loader, criterion, device)

    prec_macro = precision_score(y_true, y_pred, average="macro", zero_division=0)
    rec_macro = recall_score(y_true, y_pred, average="macro", zero_division=0)
    f1_macro = f1_score(y_true, y_pred, average="macro", zero_division=0)
    cm = confusion_matrix(y_true, y_pred)
    report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)

    print("\n=== Resultados en Test (BiGRU) ===")
    print(f"Accuracy:        {test_acc:.4f}")
    print(f"Precisión macro: {prec_macro:.4f}")
    print(f"Recall macro:    {rec_macro:.4f}")
    print(f"F1 macro:        {f1_macro:.4f}")

    # Guardar artefactos
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.model_dir.mkdir(parents=True, exist_ok=True)

    # Gráficos
    plot_learning_curves(history, args.output_dir / "curvas_aprendizaje.png")
    plot_confusion_matrix(cm, args.output_dir / "matriz_confusion.png")
    np.savetxt(args.output_dir / "matriz_confusion.csv", cm, delimiter=",", fmt="%d")

    # Guardar modelo entrenado
    torch.save(model.state_dict(), args.model_dir / "modelo_bigru.pt")

    # Guardar métricas en JSON con comparativa directa de la US-06
    resultados = {
        "modelo": "BiGRU (PyTorch)",
        "arquitectura": {
            "vocab_size": len(vocab),
            "embed_dim": 128,
            "hidden_dim": 64,
            "bidirectional": True,
            "dropout": 0.4,
            "num_classes": 5,
        },
        "parametros": {
            "max_train": args.max_train,
            "batch_size": args.batch_size,
            "learning_rate": args.lr,
            "seed": args.seed,
            "epocas_ejecutadas": len(history["train_loss"]),
        },
        "metricas_test": {
            "accuracy": round(float(test_acc), 4),
            "precision_macro": round(float(prec_macro), 4),
            "recall_macro": round(float(rec_macro), 4),
            "f1_macro": round(float(f1_macro), 4),
        },
        "referencia_us06_regresion_logistica": {
            "accuracy": 0.4914,
            "precision_macro": 0.4875,
            "recall_macro": 0.4917,
            "f1_macro": 0.4892,
        },
        "comparativa_diferencia": {
            "delta_accuracy": round(float(test_acc) - 0.4914, 4),
            "delta_f1_macro": round(float(f1_macro) - 0.4892, 4),
        },
        "reporte_por_clase": report,
    }

    with open(args.output_dir / "resultados_dl.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

    print(f"\nArtefactos guardados en:")
    print(f" - Gráficos y métricas: {args.output_dir}")
    print(f" - Checkpoint del modelo: {args.model_dir / 'modelo_bigru.pt'}")


if __name__ == "__main__":
    main()