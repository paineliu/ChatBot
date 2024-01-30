import os
from dataclasses import dataclass
from transformers import T5Config
from os.path import dirname, abspath

# ===================================================================================
# 以下为推断的配置
@dataclass
class InferConfig:
    max_seq_len: int = 320                          # 回答的最大长度
    mixed_precision: str = "bf16"                   # 混合精度 ''no','fp16','bf16' or 'fp8'

    # 全量DPO模型文件
    model_dir: str = './output/model_save/'

    # lora PDO 合并后的模型文件
    # model_file: str = './model_save/chat_small_t5.best.dpo.lora_merged.bin'
    
    # this confing for api demo:
    api_key: str = ""
    host: str = '127.0.0.1'
    port: int = 8812
    reload: bool = True
    workers: int = 1
    log_level: str = 'info'


#===================================================================================
# 以下为dpo训练配置
@dataclass
class DpoConfig:
    max_seq_len: int = 512 + 8                  # 8 for eos token 
    sft_model_file: str = './model_save/'

    tokenizer_dir: str = './model_save/tokenizer'

    dpo_train_file: str = './data/my_dpo_data.json'
    dpo_eval_file: str = './data/my_dpo_eval.json'

    adapter_file: str = './data/dpo/adapter_model.safetensors'
    log_dir: str = './logs/'

    per_device_train_batch_size: int = 4
    num_train_epochs: int = 4
    gradient_accumulation_steps: int = 8
    learning_rate: float = 1e-5
    logging_first_step: bool = True
    logging_steps: int = 20                      
    save_steps: int = 2000
    output_dir: str = '/model_save/dpo'
    warmup_steps: int = 1000
    fp16: bool = True
    seed: int = 23333
    beta: float = 0.1



# 以下为sft配置
@dataclass
class SFTconfig:
    max_seq_len: int = 384 + 8                # 8 for eos token 

    finetune_from_ckp_file = './model_save/'

    tokenizer_dir: str = './model_save/tokenizer'
    sft_train_file: str = './data/sft_train.json'

    batch_size: int = 12
    num_train_epochs: int = 4
    save_steps: int = 5000
    gradient_accumulation_steps: int = 4
    learning_rate: float = 1e-5
    logging_first_step: bool = True
    logging_steps: int = 100                      
    output_dir: str = './model_save/sft'
    warmup_steps: int = 100
    fp16: bool = True
    seed: int = 23333


# ===================================================================================
# 以下为训练的配置
@dataclass
class TrainConfig:
    def __post_init__(self):
        self.train_file: str = os.path.join(self.dataset_path, 'train.parquet')
        self.test_file: str = os.path.join(self.dataset_path, 'test.parquet')
        self.validation_file: str = os.path.join(self.dataset_path, 'valid.parquet')

    epochs: int = 8
    batch_size_per_gpu: int = 16
    
    learn_rate: float = 0.0001                      # 最大 div_factor * learn_rate
    div_factor: int = 50

    mixed_precision: str = "bf16"                   # 混合精度 ''no','fp16','bf16' or 'fp8'

    # 注意：计算梯度时相当于batch_size * gradient_accumulation_steps，说人话就是梯度累积步数>1时，等于增大n倍的batch_size
    gradient_accumulation_steps: int = 8           # 累积梯度更新步数

    warmup_steps: int = 1024                        # 模型参数预热步数，预热样本数=warmup_steps * batch_size * gradient_accumulation_steps
    
    # dataset
    dataset_path: str = './data/result/data_shuffle'
    train_file: str = './data/result/data_shuffle/train.parquet'
    validation_file: str = './data/result/data_shuffle/valid.parquet'
    test_file: str = './data/result/data_shuffle/test.parquet'
    
    # token
    tokenizer_dir: str = './output/tokenizer'

    # 
    model_file: str =        './data/model/pertrain/chat_bot_t5.{}.bin'
    model_config_file: str = './data/model/pertrain/config.json'
    # 训练状态保存，中断后可以从此处继续训练
    train_state_dir: str =  './data/model/pertrain/train_latest_state'

    output_model_file: str = './output/model/chat_bot_t5_best.bin'
    output_state_dir: str  = './output/model/pretrain_best_state'

    logging_steps: int = 50
    save_steps: int = 10000
    
    # dataset_cache_dir: str = './data/.cache'
    # trainer_log_file: str = './logs/trainer.log'

    keep_latest_n_ckp: int = 8                  # 训练过程中，最多保留多少个分数最好的模型文件

    seed: int = 23333
    dataloader_buffer_size: int = 50000
    max_seq_len: int = 256                      # 最大句子长度，默认：256


#======================================================================================
# 以下为模型的配置
@dataclass
class T5ModelConfig:
    d_ff: int = 3072                        # 全连接层维度，默认：2048, 大：3072

    d_model: int = 768                      # 词向量维度，默认：512, 大：768
    num_heads: int = 12                     # 注意力头数 d_model // num_heads == d_kv， 默认：8, 大：12
    d_kv: int = 64                          # d_model // num_heads， 默认：64, 大：64

    num_decoder_layers: int = 10            # Transformer decoder 隐藏层层数， 默认：6, 大：10
    num_layers: int = 10                    # Transformer encoder 隐藏层层数，默认：6, 大：10


def get_T5_config(config: T5ModelConfig, vocab_size: int, decoder_start_token_id: int=0, eos_token_id: int=1) -> T5Config:
    '''
    用户配置转换为T5Config
    '''
    t5_config = T5Config()
    # t5_config.model_type = 'TextToTextModel'
    # 初始化
    t5_config.d_ff = config.d_ff
    t5_config.d_kv = config.d_kv
    t5_config.d_model = config.d_model
    t5_config.num_decoder_layers = config.num_decoder_layers
    t5_config.num_heads = config.num_heads
    t5_config.num_layers = config.num_layers
    t5_config.vocab_size = vocab_size
    t5_config.decoder_start_token_id = decoder_start_token_id
    t5_config.eos_token_id = eos_token_id

    return t5_config

if __name__ == '__main__':
    train_config = TrainConfig(epochs=9, dataset_path="./")
    print(train_config)