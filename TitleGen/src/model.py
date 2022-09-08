
import torch.nn as nn
from transformers import GPT2Config,GPT2Model

class Model(nn.Module):
    def __init__(self,config:GPT2Config) -> None:
        super().__init__()
        self.conifg=config
        self.gpt=GPT2Model(config)
        self.lm_head=nn.Linear(config.n_embd,config.vocab_size,bias=False)

    def forward(self,input_ids,token_type_ids,label_mask=None):

        gpt_outputs=self.gpt(input_ids=input_ids,token_type_ids=token_type_ids)
        last_hidden_states=gpt_outputs[0]
        lm_logits=self.lm_head(last_hidden_states)

        loss=None
        if label_mask!=None:
            labels=input_ids*label_mask  
            shift_logits=lm_logits[...,:-1,:].contiguous()
            shift_labels=labels[...,1:].contiguous()

            loss_fn=nn.CrossEntropyLoss(ignore_index=0,reduction='sum')
            loss=loss_fn(shift_logits.view(-1,shift_logits.shape[-1]),shift_labels.view(-1))

            num=shift_labels.ne(0).long().sum().item()
            loss=loss/num

        outputs={
            'loss':loss,
            'lm_logits':lm_logits
        }
        return outputs

