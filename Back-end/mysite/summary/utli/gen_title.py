import torch


def gen_title(model, tokenizer, config, content):
    model.eval()
    content_token_ids = tokenizer.convert_tokens_to_ids(tokenizer.tokenize(content))
    content_token = tokenizer.convert_tokens_to_ids('[Content]')
    title_token = tokenizer.convert_tokens_to_ids("[Title]")

    if len(content_token_ids) > config.content_max_len:
        content_token_ids = content_token_ids[:config.content_max_len // 2] + content_token_ids[
                                                                              -config.content_max_len // 2:]
    input_ids = [tokenizer.cls_token_id] + content_token_ids + [tokenizer.sep_token_id]
    token_type_ids = [content_token] * len(input_ids)
    input_ids = torch.tensor(input_ids).view(1, -1).to(config.device)
    token_type_ids = torch.tensor(token_type_ids).view(1, -1).long().to(config.device)
    title_ids = []
    with torch.no_grad():
        for _ in range(config.max_generate_len):
            logits = model(input_ids, token_type_ids)['lm_logits']
            token_id = logits[0, -1, :].argmax(0)
            if token_id == tokenizer.sep_token_id:
                break
            title_ids.append(token_id.item())
            input_ids = torch.concat([input_ids, token_id.view(1, 1)], -1)
            token_type_ids = torch.concat(
                [token_type_ids, torch.tensor(title_token).view(1, 1).long().to(config.device)], -1)
    result = ""
    for i in tokenizer.convert_ids_to_tokens(title_ids):
        result += i
    return result
