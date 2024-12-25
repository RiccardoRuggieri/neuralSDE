import torch
import matplotlib.pyplot as plt


def _train_loop(model, optimizer, num_epochs, train_loader, test_loader, device, criterion):
    global all_preds, all_trues
    for epoch in range(1, num_epochs + 1):
        model.train()
        total_loss = 0
        for batch in train_loader:
            coeffs = batch[1].to(device)
            times = torch.linspace(0, 1, batch[0].shape[1]).to(device)

            _len = int(batch[0].shape[1] * 0.5)
            _coeffs = coeffs[:_len]
            _times = times[:_len]

            optimizer.zero_grad()
            true = batch[0][:, :, 1].to(device)
            _true = true[:, :_len]
            pred = model(_coeffs, _times).squeeze(-1)
            loss = criterion(pred, _true)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        if epoch % 10 == 0:
            avg_loss = total_loss / len(train_loader)
            print(f'Epoch {epoch}, Loss: {avg_loss}')

            ##
            model.eval()
            total_loss = 0
            all_preds = []
            all_trues = []
            with torch.no_grad():
                for batch in test_loader:
                    coeffs = batch[1].to(device)
                    times = torch.linspace(0, 1, batch[0].shape[1]).to(device)
                    coeffs = torch.cat((coeffs[:_len], torch.zeros_like(coeffs[_len:])), dim=0)

                    true = batch[0][:, :, 1].to(device)
                    pred = model(coeffs, times).squeeze(-1)
                    # only compute the forecasting loss
                    loss = criterion(pred[:, _len:], true[:, _len:])
                    total_loss += loss.item()

                    all_preds.append(pred[:, _len:].cpu())
                    all_trues.append(true[:, _len:].cpu())

            avg_loss = total_loss / len(test_loader)
            print(f'Test Loss: {avg_loss}')

            all_preds = torch.cat(all_preds, dim=0)
            all_trues = torch.cat(all_trues, dim=0)

            ## plotting
            num_samples = 1

            plt.figure(figsize=(8, 4))
            for i in range(num_samples):
                plt.plot(all_trues[i].numpy(), color='r')
                plt.plot(all_preds[i].numpy(), color='b')
            plt.xlabel('Time')
            plt.ylabel('Value')
            plt.ylim(-2,2)
            plt.title('Model Predictions vs True Values')
            plt.show()

    return all_preds, all_trues