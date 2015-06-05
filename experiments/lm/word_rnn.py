#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
from argparse import ArgumentParser

from utils import load_data
from lm import NeuralLM
from deepy.trainers import SGDTrainer, LearningRateAnnealer
from deepy.layers import LSTM, Dense, RNN, Softmax3D


logging.basicConfig(level=logging.INFO)

default_model = os.path.join(os.path.dirname(__file__), "models", "word_rnn1.gz")

if __name__ == '__main__':
    ap = ArgumentParser()
    ap.add_argument("--model", default="")
    ap.add_argument("--small", action="store_true")
    args = ap.parse_args()

    vocab, lmdata = load_data(small=args.small, history_len=5)
    model = NeuralLM(vocab.size, test_data=lmdata.valid_set())
    model.stack(RNN(hidden_size=50, output_type="sequence", hidden_activation='sigmoid',
                    persistent_state=True, batch_size=lmdata.size,
                    reset_state_for_input=1),
                Dense(vocab.size, activation="linear"),
                Softmax3D())

    if os.path.exists(args.model):
        model.load_params(args.model)

    trainer = SGDTrainer(model, {"learning_rate": LearningRateAnnealer.learning_rate(0.1),
                                 "weight_l2": 1e-4})
    annealer = LearningRateAnnealer(trainer)

    trainer.run(lmdata, controllers=[annealer])

    model.save_params(default_model)
