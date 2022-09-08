import numpy as np
import torch


class BaseConfig():
    def __init__(self) -> None:
        self.mode = 'base'
        self.data_path = None
        self.vocab_path = './vocab/vocab.txt'
        self.bert_config_path = './config/config.json'
        self.seed = 2022
        self.title_max_len = 25
        self.content_max_len = 400
        self.adam_epsilon = 1e-8
        self.learning_rate = 1e-4
        self.warmup_ratio = 0.01
        self.val_ratio = 0.1
        self.train_batch_size = 12  # 12
        self.val_batch_size = 32
        self.save_batch = 5000
        self.epochs = 2
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    @staticmethod
    def seed_all(seed=2022):
        np.random.seed(seed)
        torch.manual_seed(seed)
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)

    @staticmethod
    def get_device():
        return torch.device('cuda' if torch.cuda.is_available() else 'cpu')


class TrainConfig(BaseConfig):
    def __init__(self) -> None:
        super().__init__()
        self.mode = 'train'
        self.data_path = [
            './data/train.json',
            # 扩充数据集 https://zhuanlan.zhihu.com/p/341398288
        ]
        self.epochs = 10


class FinetuneConfig(BaseConfig):
    def __init__(self) -> None:
        super().__init__()
        self.mode = 'train'
        self.data_path = [
            './data/train.json',
            # './data/dev.json'
        ]
        self.epochs = 5
        self.learning_rate = 5e-5
        self.warmup_ratio = 0.1


class ValidConfig(BaseConfig):
    def __init__(self) -> None:
        super().__init__()
        self.mode = 'valid'
        self.data_path = './data/dev.json'
        self.max_generate_len = 20
