import os
import yaml
from pathlib import Path

def load_config(config_name):
    """Load config from rules subdirectory, preferring _loc version."""
    loc_file = Path(f"config/rules/{config_name}_loc.yaml")
    public_file = Path(f"config/rules/{config_name}.yaml")
    
    if loc_file.exists():
        with open(loc_file, 'r') as f:
            return yaml.safe_load(f)
    elif public_file.exists():
        with open(public_file, 'r') as f:
            return yaml.safe_load(f)
    else:
        raise FileNotFoundError(f"No config found for {config_name}")

def load_doc_types():
    """Load document type definitions."""
    return load_config("doc_types")

def load_fields():
    """Load field definitions.""" 
    return load_config("fields")

def load_correction_rules():
    """Load correction rules."""
    return load_config("correction_rules")