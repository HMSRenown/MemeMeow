import yaml
from pathlib import Path
from pydantic import BaseModel

class APIConfig(BaseModel):
    protected_mode: bool
    allowed_endpoints: list[str]
    rate_limit: dict
    logging: dict

def load_config(config_path: str = "config/api_config.yaml") -> APIConfig:
    try:
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"配置文件 {config_path} 不存在")
            
        with open(config_file) as f:
            raw_config = yaml.safe_load(f)
            
        return APIConfig(**raw_config["api"])
        
    except Exception as e:
        raise RuntimeError(f"配置加载失败: {str(e)}")