import torch


class MetricWatcher:
    """
    Base class which monitors a given metric on a Trainer object
    and check whether the model has been improved according to this metric
    """

    def __init__(self, metric, mode="min"):
        self.best = None
        self.metric = metric
        self.mode = mode
        self.scores = None  # will be filled by the Trainer instance

    def has_improved(self):

        # get the latest value for the desired metric
        value = self.scores[self.metric][-1]

        # init best value
        if self.best is None:
            self.best = value
            return True

        if (
                self.mode == "min" and value < self.best
                or
                self.mode == "max" and value > self.best
        ):  # the performance of the model has been improved :)
            self.best = value
            return True
        else:
            # no improvement :(
            return False


class EarlyStop(MetricWatcher):
    def __init__(self, metric, mode="min", patience=0):
        """

        Args:
            patience (int): for how many epochs to wait, for the performance
                to improve.
            mode (str, optional): Possible values {"min","max"}.
                - "min": save the model if the monitored metric is decreased.
                - "max": save the model if the monitored metric is increased.
        """
        MetricWatcher.__init__(self, metric, mode)
        self.patience = patience
        self.patience_left = patience

    def stop(self):
        """
        Check whether we should stop the training
        """

        if self.has_improved():
            self.patience_left = self.patience  # reset patience
        else:
            self.patience_left -= 1  # decrease patience

        # if no more patience left, then stop training
        return self.patience_left < 0


class Checkpoint(MetricWatcher):
    def __init__(self, file, model, metric, mode="min"):
        """

        Args:
            file (str):
            model (nn.Module):
            mode (str, optional): Possible values {"min","max"}.
                - "min": save the model if the monitored metric is decreased.
                - "max": save the model if the monitored metric is increased.
        """
        MetricWatcher.__init__(self, metric, mode)

        self.file = file
        self.model = model

    def check(self):
        if self.has_improved():
            print("Improved model! Saving checkpoint...")
            torch.save(self.model, self.file)


class Trainer:
    def __init__(self, model,
                 train_dataloader,
                 optimizer,
                 pipeline,
                 metrics=None,
                 val_dataloader=None,
                 checkpoint=None,
                 early_stopping=None):
        """
         The Trainer is responsible for training a model.
         It is a stateful object.
         It holds a set of variables that helps us to abstract
         the training process.
        many
        Args:
            model ():
            train_dataloader ():
            optimizer ():
            pipeline ():
            metrics ():
            val_dataloader ():
            early_stopping (EarlyStop):
            checkpoint (Checkpoint):
        """
        self.model = model
        self.train_dataloader = train_dataloader
        self.val_dataloader = val_dataloader
        self.optimizer = optimizer
        self.pipeline = pipeline
        self.checkpoint = checkpoint
        self.early_stopping = early_stopping

        self.metrics = {} if metrics is None else metrics
        self.scores = {k: [] for k, v in self.metrics.items()}

        self.running_loss = 0.0
        self.epoch = 0

        # we need to attach the metrics dictionary
        # on checkpoint and early_stopping objects
        if self.checkpoint is not None:
            self.checkpoint.scores = self.scores
        if self.early_stopping is not None:
            self.early_stopping.scores = self.scores

    def train_epoch(self):
        """
        Train the model for one epoch
        Returns:

        """
        # switch to train mode -> enable regularization layers, such as Dropout
        self.model.train()
        self.epoch += 1
        running_loss = 0.0

        for i_batch, sample_batched in enumerate(self.train_dataloader, 1):
            # 1 - zero the gradients
            self.optimizer.zero_grad()

            # 2 - compute loss using the provided pipeline
            outputs, labels, loss = self.pipeline(self.model, sample_batched)

            # 3 - backward pass: compute gradient wrt model parameters
            loss.backward()

            # 4 - update weights
            self.optimizer.step()

            running_loss += loss.data[0]

            # print statistics
            progress(loss=loss.data[0],
                     epoch=self.epoch,
                     batch=i_batch,
                     batch_size=self.train_dataloader.batch_size,
                     dataset_size=len(self.train_dataloader.dataset))

        if self.val_dataloader is not None:
            avg_loss, (y, y_pred) = self.eval(self.val_dataloader)
            self.update_scores(y, y_pred)

        return running_loss / i_batch

    def update_scores(self, y, y_pred):
        """
        Evaluate the predictions, with each metric
        Args:
            y (): list of the gold labels
            y_pred (): list of the predicted labels

        Returns:

        """
        for name, metric in self.metrics.items():
            self.scores[name].append(metric(y, y_pred))

    def eval(self, dataloader):
        """
        Evaluate the model, on a given dataset (dataloader)
        Args:
            dataloader (DataLoader): a torch DataLoader which will be used for
                evaluating the performance of the model

        Returns:

        """
        # switch to eval mode -> disable regularization layers, such as Dropout
        self.model.eval()

        y_pred = []
        y = []

        total_loss = 0

        for i_batch, sample_batched in enumerate(dataloader, 1):
            outputs, labels, loss = self.pipeline(self.model, sample_batched)

            total_loss += loss.data[0]

            _, predicted = torch.max(outputs.data, 1)

            y.extend(list(labels.data.cpu().numpy().squeeze()))
            y_pred.extend(list(predicted.squeeze()))

        avg_loss = total_loss / i_batch

        return avg_loss, (y, y_pred)
