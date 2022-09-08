import copy
import os
from config import BaseConfig
from dataset import TitleDataset
import torch
from torch.utils.data import DataLoader,SequentialSampler,RandomSampler,random_split
from transformers import get_cosine_schedule_with_warmup,AdamW,BertTokenizer


def build_optimizer(config: BaseConfig, model, max_steps):
    param_optimizer = list(model.named_parameters())
    no_decay = ['bias', 'LayerNorm.bias', 'LayerNorm.weight']
    optimizer_grouped_parameters = [
        {'params': [p for n, p in param_optimizer if not any(
            nd in n for nd in no_decay)], 'weight_decay': 0.01},
        {'params': [p for n, p in param_optimizer if any(
            nd in n for nd in no_decay)], 'weight_decay': 0.0}
    ]
    optimizer = AdamW(optimizer_grouped_parameters,
                      lr=config.learning_rate,
                      eps=config.adam_epsilon)
    scheduler = get_cosine_schedule_with_warmup(optimizer,
                                                num_warmup_steps=config.warmup_ratio*max_steps,
                                                num_training_steps=max_steps)

    return optimizer, scheduler


def build_dataloaders(config: BaseConfig, use_valid=True):

    tokenizer = BertTokenizer.from_pretrained(config.vocab_path, use_fast=True)
    dataset = TitleDataset(config, tokenizer)

    if use_valid:
        size = len(dataset)
        val_size = int(size * config.val_ratio)

        train_dataset, val_dataset = random_split(
            dataset, [size - val_size, val_size], generator=torch.Generator().manual_seed(config.seed))
        train_sampler = RandomSampler(train_dataset)
        val_sampler = SequentialSampler(val_dataset)

        train_dataloader = DataLoader(train_dataset,
                                      batch_size=config.train_batch_size,
                                      sampler=train_sampler,
                                      drop_last=False,
                                      )
        val_dataloader = DataLoader(val_dataset,
                                    batch_size=config.val_batch_size,
                                    sampler=val_sampler,
                                    drop_last=False,
                                    )
    else:
        train_sampler = RandomSampler(dataset)
        train_dataloader = DataLoader(
            dataset,
            batch_size=config.train_batch_size,
            sampler=train_sampler,
            drop_last=False,
        )
        val_dataloader = None

    return train_dataloader, val_dataloader


class EMA():
    def __init__(self, model, decay):
        self.model = model
        self.decay = decay
        self.shadow = {}
        self.backup = {}
        self.register()

    def register(self):
        for name, param in self.model.named_parameters():
            if param.requires_grad:
                self.shadow[name] = param.data.clone()

    def update(self):
        for name, param in self.model.named_parameters():
            if param.requires_grad:
                assert name in self.shadow
                new_average = (1.0 - self.decay) * param.data + self.decay * self.shadow[name]
                self.shadow[name] = new_average.clone()

    def apply_shadow(self):
        for name, param in self.model.named_parameters():
            if param.requires_grad:
                assert name in self.shadow
                self.backup[name] = param.data
                param.data = self.shadow[name]

    def restore(self):
        for name, param in self.model.named_parameters():
            if param.requires_grad:
                assert name in self.backup
                param.data = self.backup[name]
        self.backup = {}


class FGM():
    def __init__(self, model):
        self.model = model
        self.backup = {}

    def attack(self, epsilon=1., emb_name='word_embeddings'):
        for name, param in self.model.named_parameters():
            if param.requires_grad and emb_name in name:
                self.backup[name] = param.data.clone()
                norm = torch.norm(param.grad)
                if norm != 0:
                    r_at = epsilon * param.grad / norm
                    param.data.add_(r_at)

    def restore(self, emb_name='word_embeddings'):
        for name, param in self.model.named_parameters():
            if param.requires_grad and emb_name in name:
                assert name in self.backup
                param.data = self.backup[name]
        self.backup = {}


class PGD():
    def __init__(self, model):
        self.model = model
        self.emb_backup = {}
        self.grad_backup = {}

    def attack(self, epsilon=1., alpha=0.3, emb_name='word_embeddings.weight', is_first_attack=False):
        for name, param in self.model.named_parameters():
            if param.requires_grad and emb_name in name:
                if is_first_attack:
                    self.emb_backup[name] = param.data.clone()
                norm = torch.norm(param.grad)
                if norm != 0:
                    r_at = alpha * param.grad / norm
                    param.data.add_(r_at)
                    param.data = self.project(name, param.data, epsilon)

    def restore(self, emb_name='word_embeddings.weight'):
        for name, param in self.model.named_parameters():
            if param.requires_grad and emb_name in name:
                assert name in self.emb_backup
                param.data = self.emb_backup[name]
        self.emb_backup = {}

    def project(self, param_name, param_data, epsilon):
        r = param_data - self.emb_backup[param_name]
        if torch.norm(r) > epsilon:
            r = epsilon * r / torch.norm(r)
        return self.emb_backup[param_name] + r

    def backup_grad(self):
        for name, param in self.model.named_parameters():
            if param.requires_grad and param.grad is not None:
                self.grad_backup[name] = param.grad.clone()

    def restore_grad(self):
        for name, param in self.model.named_parameters():
            if param.requires_grad and param.grad is not None:
                param.grad = self.grad_backup[name]

def get_model_path_list(base_dir):

    model_lists = []

    for fname in os.listdir(base_dir):
        if '.pth' in fname: 
            model_lists.append(base_dir+'/'+fname)

    model_lists = sorted(model_lists)

    return model_lists[:]

def SWA(model,base_dir='./check',k_folder=None):

    model_path_list = get_model_path_list(base_dir)
    print(f'mode_list:{model_path_list}')

    swa_model = copy.deepcopy(model)
    swa_n = 0.

    with torch.no_grad():
        for _ckpt in model_path_list:
            model.load_state_dict(torch.load(_ckpt))
            tmp_para_dict = dict(model.named_parameters())

            alpha = 1. / (swa_n + 1.)

            for name, para in swa_model.named_parameters():
                para.copy_(tmp_para_dict[name].data.clone() * alpha + para.data.clone() * (1. - alpha))

            swa_n += 1

    model_name=os.path.join(base_dir,"swa_model.pth")

    torch.save(swa_model.state_dict(), model_name)
    
    return swa_model
