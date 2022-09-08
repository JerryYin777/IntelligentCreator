import torch
import torch.nn as nn
from config import *
from model import *
from tqdm.autonotebook import tqdm
from utils import *
from torch.utils.tensorboard import SummaryWriter
from transformers import GPT2Config


def finetune(model: nn.Module, trainloader, testloader,optimizer,scheduler,epochs,writer):
    # ema=EMA(net,0.999)
    # ema.register()

    # swa_start=2
    # swa_batch=2000

    model.train()

    for e in range(epochs):
        tqdm_loader = tqdm(trainloader)
        total_train_loss = 0

        for i, input_data in enumerate(tqdm_loader):
            out=model(**input_data)
            loss = out['loss']
            loss.backward()  
            
            optimizer.step()
            scheduler.step()
            # ema.update()
            model.zero_grad()

            total_train_loss += loss.item()

            writer.add_scalar('finetune/loss', loss.item(), e*len(trainloader)+i)
            tqdm_loader.set_description(
                f"epoch:{e+1} batch:{i+1} loss:{loss.item():.6f} ")

        # ema.apply_shadow()
        message=f"average train loss: {total_train_loss/i: .6f}\n"
        print(message)
        torch.save(model.state_dict(), f"./check/model_finetune.pth")
        # ema.restore()

if __name__ == '__main__':
    config = FinetuneConfig()
    config.seed_all()
    model = Model(GPT2Config.from_json_file(config.bert_config_path)).to(config.device)
    model.load_state_dict(torch.load('./check/model_train.pth'))
    trainloader,testloader= build_dataloaders(config,False)
    max_steps=len(trainloader)*config.epochs
    optimizer,scheduler=build_optimizer(config,model,max_steps)
    writer = SummaryWriter('./logs')
    finetune(model, trainloader,testloader,optimizer,scheduler ,config.epochs,writer)
    writer.close()




