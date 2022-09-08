import torch
from torch.utils.data import Dataset
from config import BaseConfig
import json
import numpy as np


class TitleDataset(Dataset):
    def __init__(self, config: BaseConfig, tokenizer):
        self.config = config
        self.tokenizer = tokenizer
        self.mode = config.mode
        self.data_path = config.data_path
        self.title_max_len = config.title_max_len
        self.content_max_len = config.content_max_len
        # <cls> content <sep> title <sep> <pad> <pad>...
        self.text_max_len = self.title_max_len+self.content_max_len+3
        self.cls_token_id = self.tokenizer.cls_token_id
        self.sep_token_id = self.tokenizer.sep_token_id
        self.pad_token_id = self.tokenizer.pad_token_id
        self.content_id = self.tokenizer.convert_tokens_to_ids("[Content]")
        self.title_id = self.tokenizer.convert_tokens_to_ids("[Title]")

        self.data = []
        if isinstance(self.data_path, str):
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        else:
            for file in self.data_path:
                with open(file, 'r', encoding='utf-8') as f:
                    self.data.extend(json.load(f))
        if config.mode == 'train':
            np.random.shuffle(self.data)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        t = self.data[index]

        title = t['title']
        content = t['content']

        content_token_ids = self.tokenizer.convert_tokens_to_ids(self.tokenizer.tokenize(content))
        title_token_ids = self.tokenizer.convert_tokens_to_ids(self.tokenizer.tokenize(title))

        if len(title_token_ids) > self.title_max_len:
            title_token_ids = title_token_ids[:self.title_max_len]
        if len(content_token_ids) > self.content_max_len:
            content_token_ids = content_token_ids[:self.content_max_len // 2] + \
                content_token_ids[-self.content_max_len//2:]  # 开头结尾各取最大长度的一半

        pad_len = self.text_max_len - len(content_token_ids)-len(title_token_ids)-3
        input_ids = [self.cls_token_id]+content_token_ids+[self.sep_token_id]+title_token_ids+[self.sep_token_id]+[0]*pad_len
        token_type_ids = [self.content_id]*(len(content_token_ids)+2)+[self.title_id]*(len(title_token_ids)+1)+[0]*pad_len
        label_mask = [0]*(len(content_token_ids)+2)+[1] * (len(title_token_ids)+1)+[0]*pad_len
        
        return {
            'input_ids': torch.tensor(input_ids).to(self.config.device),
            'token_type_ids': torch.tensor(token_type_ids).to(self.config.device),
            'label_mask': torch.tensor(label_mask).to(self.config.device)
        }
