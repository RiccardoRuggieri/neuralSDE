import torch
import torch.optim as optim
from Dataset.classification.utils import speech_commands
import model.classification.randomODE as randomODE
import model.classification.sde as sde
from common.classification.trainer import _train_loop

def main_classical_training(type='ode', hidden_dim=16, num_layers=1):

    input_dim = 20
    num_classes = 10

    use_cuda = torch.cuda.is_available()
    device = torch.device("cuda" if use_cuda else "cpu")

    if type == 'ode':
        model = randomODE.Generator(input_dim=input_dim,
                                   hidden_dim=hidden_dim,
                                   num_classes=num_classes,
                                   num_layers=num_layers,
                                   vector_field=randomODE.GeneratorFunc,
                                   final_nl=False).to(device)
    else:
        model = sde.Generator(input_dim=input_dim,
                              hidden_dim=hidden_dim,
                              num_classes=num_classes,
                              num_layers=num_layers,
                              vector_field=sde.GeneratorFunc).to(device)


    # 200 epochs
    num_epochs = 100
    lr = 1e-3

    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = torch.nn.CrossEntropyLoss()

    # Here we get the data
    data_manager = speech_commands.SpeechCommandsData(train_ratio=0.8, batch_size=128, seed=42)
    train_loader, test_loader = data_manager.get_data()

    # Here we train the model
    results = _train_loop(model, optimizer, num_epochs, train_loader, test_loader, device, criterion)

    # Show some stats at the end of the training
    # show_distribution_comparison(all_preds, all_trues)

    return results

if __name__ == '__main__':
    main_classical_training(type='ode', hidden_dim=32, num_layers=1)