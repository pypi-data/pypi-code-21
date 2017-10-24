
# coding: utf-8

# In[ ]:
import argparse
from math import log10

import torch
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable
from torch.utils.data import DataLoader
from . import get_dataset
from utils.log import warning, error

class learn():
    def __init__(self):
        self.members = ['get_dataset', 'load_dataset']
        
    def get_var_name():
        return [k for k,v in locals().items() if v is True][0]

    def get_default(param_name):
        return {
            'criterion': nn.CrossEntropyLoss()
    #        , 'model': Net()
    #        , 'optimizer': optim.Adam(Net().parameters())
        }.get(param_name, error("No default specified"))

    class learn_model(data_dir = None, model = None, criterion = None, optimizer = None):
        if data_dir is None:
            error("No data_dir provided")
        if model is None:
            error("No model provided")
        if criterion is None:
            error("No criterion provided")
        if optimizer is None:
            error("No optimizer provided")

        if torch.cuda.is_available():
            cuda = True

        print("Building model...")
        model = model
        criterion = criterion

        if cuda:
            model = model.cuda()
            criterion = criterion.cuda()

        optimizer = optim.Adam(model.parameters())

        print("Loading datasets...")
        train_data_loader, val_data_loader, test_data_loader = get_split_data_loaders(data_dir)

        def learn(epoch, data_loader, train = True):
            epoch_loss = 0
            for iteration, batch in enumerate(data_loader, 1):
                input, target = Variable(batch[0]), Variable(batch[1])
                if cuda:
                    input = input.cuda()
                    target = target.cuda()

                optimizer.zero_grad()
                loss = criterion(model(input), target)
                epoch_loss += loss.data[0]
                if train is True:
                    loss.backward()
                    optimizer.step()
                global min_loss_to_date
                global do_checkpoint
                if loss.data[0] < min_loss_to_date:
                    min_loss_to_date = loss.data[0]
                    do_checkpoint = True

                print(f"===> Epoch [{epoch}]({iteration}/{len(data_loader)}): Loss: {loss.data[0]:.4f}")

            print(f"===> Epoch {epoch} Complete: Avg. Loss: {epoch_loss/len(data_loader):.4f}")


        def train(epoch):
            learn(epoch, train_data_loader)

        def val(epoch):
            learn(epoch, val_data_loader, train = False)

        def test(epoch):
            learn(epoch, test_data_loader, train = False)

        def checkpoint(epoch):
            model_out_path = f"model_epoch_{epoch}.pth"
            torch.save(model, model_out_path)
            print(f"Checkpoint saved to {model_out_path}")

        min_loss_to_data = Inf
        do_checkpoint = False

        for epoch in range(num_epochs = None):
            if num_epochs is None:
                warning("Number of epochs not specified. Using default of 10.")
                num_epochs = 10
            train(epoch)
            val(epoch)
            if do_checkpoint:
                checkpoint(epoch)

