"""
Configuration loader for YAML-based validation rules.
Loads and parses document types, field definitions, and correction rules.
"""
import os
import yaml
from pathlib import Path


def load_yaml_config(file_path):
    """
    Load YAML configuration file
    
    Args:
        file_path: Path to YAML configuration file
        
    Returns:
        dict: Parsed YAML content
    """
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except (yaml.YAMLError, FileNotFoundError) as e:
        print(f"Error loading configuration from {file_path}: {e}")
        return {}


def get_config_dir():
    """Get path to configuration directory"""
    # Start with the directory this file is in
    base_dir = Path(__file__).parent.parent
    return base_dir / 'config'


def load_document_types():
    """Load document type definitions"""
    config_dir = get_config_dir()
    return load_yaml_config(config_dir / 'doc_types.yaml')


def load_field_definitions():
    """Load field definitions and patterns"""
    config_dir = get_config_dir()
    return load_yaml_config(config_dir / 'fields.yaml')


def load_correction_rules():
    """Load auto-correction rules"""
    config_dir = get_config_dir()
    return load_yaml_config(config_dir / 'correction_rules.yaml')


def get_document_types():
    """Get all document types"""
    doc_types = load_document_types()
    return doc_types.get('document_types', {})


def get_field_definitions():
    """Get all field definitions"""
    field_defs = load_field_definitions()
    return field_defs.get('fields', {})


def get_correction_rules():
    """Get all correction rules"""
    rules = load_correction_rules()
    return rules.get('correction_rules', {})