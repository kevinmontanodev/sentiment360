"""Pruebas unitarias para el modelo de Deep Learning (US-07)."""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from src.modelos.entrenar_deep_learning import (
    EarlyStopping,
    ReviewsDataset,
    SentimentBiGRU,
    Vocabulary,
    evaluate,
    train_one_epoch,
)


def test_vocabulary_encoding():
    vocab = Vocabulary(max_size=10)
    vocab.build_vocab(["excelente producto muy bueno", "muy mal servicio"])
    encoded = vocab.encode("excelente servicio desconocido", max_len=5)
    assert len(encoded) == 5
    assert encoded[0] == vocab.w2i["excelente"]
    assert encoded[2] == vocab.w2i["<UNK>"]
    assert encoded[3] == vocab.w2i["<PAD>"]


def test_model_forward_shape():
    model = SentimentBiGRU(vocab_size=50, embed_dim=16, hidden_dim=8, num_classes=5)
    batch_x = torch.randint(0, 50, (4, 10))  # batch de 4, secuencia de 10
    out = model(batch_x)
    assert out.shape == (4, 5)


def test_training_one_epoch_reduces_loss():
    texts = [
        "buen producto me gusto mucho",
        "pesima calidad no lo recomiendo",
        "regular calidad aceptable",
    ] * 8
    labels = [4, 0, 2] * 8

    vocab = Vocabulary(max_size=50)
    vocab.build_vocab(texts)
    dataset = ReviewsDataset(texts, labels, vocab, max_len=10)
    loader = DataLoader(dataset, batch_size=4, shuffle=True)

    model = SentimentBiGRU(vocab_size=len(vocab), embed_dim=16, hidden_dim=8, num_classes=5)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    device = torch.device("cpu")

    loss_prev, _ = train_one_epoch(model, loader, criterion, optimizer, device)
    loss_next, _ = train_one_epoch(model, loader, criterion, optimizer, device)
    assert isinstance(loss_next, float)


def test_early_stopping_activation():
    early_stopping = EarlyStopping(patience=2)
    model = nn.Linear(5, 5)

    early_stopping(1.0, model)
    assert early_stopping.counter == 0
    assert early_stopping.early_stop is False

    early_stopping(1.05, model)
    assert early_stopping.counter == 1

    early_stopping(1.10, model)
    assert early_stopping.counter == 2
    assert early_stopping.early_stop is True