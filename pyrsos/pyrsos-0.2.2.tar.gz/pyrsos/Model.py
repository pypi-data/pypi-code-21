from pyrsos.training import epoch_progress


class Model():
    def __init__(self, model):
        self.model = model

    def fit(self,
            epochs,
            batch_size,
            train_set,
            val_set=None,
            metrics=None,
            on_batch_end=None,
            on_epoch_end=None):

        if metrics is None:
            metrics = []

        if on_batch_end is None:
            on_batch_end = []

        if on_epoch_end is None:
            on_epoch_end = []

        for epoch in range(epochs):
            running_loss = 0.0
            self.model.train()

            for i_batch, sample_batched in enumerate(train_set):

                loss = train_scenario(sample_batched)

                # print statistics
                running_loss += loss.data[0]
                epoch_progress(loss=loss.data[0],
                               epoch=epoch + 1,
                               batch=i_batch + 1,
                               batch_size=batch_size,
                               dataset_size=len(train_set.dataset))

                # Callback for batch end
                for callback in on_batch_end:
                    callback(self.model, loss)

            print(" -- Avg Epoch Loss = {:.4f}".format(
                running_loss / (i_batch + 1)))

            # Callback for epoch end
            for callback in on_epoch_end:
                callback(self.model, loss)
