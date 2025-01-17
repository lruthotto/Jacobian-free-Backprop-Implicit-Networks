'''
Functions for training and testing different models
'''
import torch
from matplotlib import pyplot as plt

def train_dncnn(model, loader, operator, loss_function, optimizer, device):
    model.train()
    nbatch = 200 // model.bsz # only train on 200 images
    L = []
    grad_norm_list = []
    for batch_idx, X in enumerate(loader):
        if batch_idx > nbatch:
            break
        optimizer.zero_grad()
        X = X.to(device)
        d = operator.forward(X)
        pred = model(d)
        batch_loss = torch.div(loss_function(pred, X), model.bsz)
        batch_loss.backward()
        grad_norm_list.append(model.current_grad_norm())
        optimizer.step()
        L.append(batch_loss.item())
    return L, grad_norm_list

def train_jfb(model, loader, operator, loss_function, optimizer, device, ssim_calculator):
    model.train()
    model.dncnn.train()
    L = []
    n_iters_list = []
    grad_norm_list = []
    ssim_list = []
    for batch_idx, X in enumerate(loader):
        optimizer.zero_grad()
        X = X.to(device)
        d = operator.forward(X)
        pred, n_iters = model(d)
        batch_loss = torch.div(loss_function(pred, X), model.bsz)
        batch_loss.backward()
        grad_norm_list.append(model.current_grad_norm())
        optimizer.step()
        L.append(batch_loss.item())
        n_iters_list.append(n_iters)
        with torch.no_grad():
            batch_ssim = ssim_calculator(pred, X)
        ssim_list.append(batch_ssim.item())
    return L, n_iters_list, grad_norm_list, ssim_list

def valid_jfb(model, loader, operator, loss_function, device, ssim_calculator):
    model.eval()
    model.dncnn.eval()
    acc = 0
    ssim = 0
    for batch_idx, X in enumerate(loader):
        X = X.to(device)
        d = operator.forward(X)
        pred, _ = model(d)
        batch_loss = loss_function(pred, X)
        batch_ssim = ssim_calculator(pred, X)
        acc += batch_loss.item()
        ssim += batch_ssim.item()
    return acc/(batch_idx + 1), ssim/(batch_idx + 1)


def plotting(loss_list, n_iters_list, grad_norm_list, epoch_number, path):
    fig = plt.figure()
    fig.add_subplot(1, 3, 1)
    plt.plot(loss_list)
    plt.xlabel("# epochs")
    plt.ylabel("avg loss of epoch")
    fig.add_subplot(1, 3, 2)
    plt.plot(n_iters_list)
    plt.xlabel("# epochs")
    plt.ylabel("# iterations applied")
    fig.add_subplot(1, 3, 3)
    plt.plot(grad_norm_list)
    plt.xlabel("#epochs")
    plt.ylabel("avg gradient norm")
    plt.savefig(path+"results"+str(epoch_number)+".png")
