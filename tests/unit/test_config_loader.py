"""Unit tests for configuration loader."""

import pytest
import os
import json
import yaml
from src.config.config_loader import ConfigLoader, load_config


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary configuration directory."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    return config_dir


@pytest.fixture
def sample_yaml_config(temp_config_dir):
    """Create a sample YAML configuration file."""
    config_file = temp_config_dir / "test.yaml"
    config_data = {
        "database": {"host": "localhost", "port": 5432},
        "logging": {"level": "INFO"},
    }
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)
    return config_file


@pytest.fixture
def sample_json_config(temp_config_dir):
    """Create a sample JSON configuration file."""
    config_file = temp_config_dir / "test.json"
    config_data = {
        "api": {"key": "secret123", "timeout": 30},
        "features": {"enabled": True},
    }
    with open(config_file, "w") as f:
        json.dump(config_data, f)
    return config_file


def test_config_loader_initialization(temp_config_dir):
    """Test ConfigLoader initialization."""
    loader = ConfigLoader(str(temp_config_dir))
    assert loader.config_dir == temp_config_dir
    assert loader.config == {}


def test_load_from_yaml_file(temp_config_dir, sample_yaml_config):
    """Test loading configuration from YAML file."""
    loader = ConfigLoader(str(temp_config_dir))
    config = loader.load_from_file("test.yaml")

    assert config["database"]["host"] == "localhost"
    assert config["database"]["port"] == 5432
    assert config["logging"]["level"] == "INFO"


def test_load_from_json_file(temp_config_dir, sample_json_config):
    """Test loading configuration from JSON file."""
    loader = ConfigLoader(str(temp_config_dir))
    config = loader.load_from_file("test.json")

    assert config["api"]["key"] == "secret123"
    assert config["api"]["timeout"] == 30
    assert config["features"]["enabled"] is True


def test_load_from_yml_extension(temp_config_dir):
    """Test loading configuration from .yml file."""
    config_file = temp_config_dir / "test.yml"
    config_data = {"setting": "value"}
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)

    loader = ConfigLoader(str(temp_config_dir))
    config = loader.load_from_file("test.yml")
    assert config["setting"] == "value"


def test_load_from_nonexistent_file(temp_config_dir):
    """Test loading from nonexistent file raises error."""
    loader = ConfigLoader(str(temp_config_dir))

    with pytest.raises(FileNotFoundError, match="Configuration file not found"):
        loader.load_from_file("nonexistent.yaml")


def test_load_from_unsupported_format(temp_config_dir):
    """Test loading unsupported format raises error."""
    config_file = temp_config_dir / "test.txt"
    with open(config_file, "w") as f:
        f.write("some text")

    loader = ConfigLoader(str(temp_config_dir))

    with pytest.raises(ValueError, match="Unsupported configuration format"):
        loader.load_from_file("test.txt")


def test_load_from_env():
    """Test loading configuration from environment variables."""
    # Set test environment variables
    os.environ["PIPE_DATABASE_HOST"] = "testhost"
    os.environ["PIPE_DATABASE_PORT"] = "3306"
    os.environ["PIPE_LOG_LEVEL"] = "DEBUG"
    os.environ["OTHER_VAR"] = "ignored"

    try:
        loader = ConfigLoader()
        config = loader.load_from_env("PIPE_")

        assert config["database_host"] == "testhost"
        assert config["database_port"] == "3306"
        assert config["log_level"] == "DEBUG"
        assert "other_var" not in config
    finally:
        # Cleanup
        del os.environ["PIPE_DATABASE_HOST"]
        del os.environ["PIPE_DATABASE_PORT"]
        del os.environ["PIPE_LOG_LEVEL"]
        del os.environ["OTHER_VAR"]


def test_load_from_env_custom_prefix():
    """Test loading with custom environment prefix."""
    os.environ["CUSTOM_SETTING"] = "value"
    os.environ["CUSTOM_NUMBER"] = "42"

    try:
        loader = ConfigLoader()
        config = loader.load_from_env("CUSTOM_")

        assert config["setting"] == "value"
        assert config["number"] == "42"
    finally:
        del os.environ["CUSTOM_SETTING"]
        del os.environ["CUSTOM_NUMBER"]


def test_merge_configs():
    """Test merging multiple configurations."""
    loader = ConfigLoader()

    config1 = {"a": 1, "b": {"c": 2, "d": 3}}
    config2 = {"b": {"c": 20, "e": 4}, "f": 5}

    merged = loader.merge_configs(config1, config2)

    assert merged["a"] == 1
    assert merged["b"]["c"] == 20  # Overwritten
    assert merged["b"]["d"] == 3  # Preserved
    assert merged["b"]["e"] == 4  # Added
    assert merged["f"] == 5


def test_merge_configs_multiple():
    """Test merging more than two configurations."""
    loader = ConfigLoader()

    config1 = {"a": 1, "b": 2}
    config2 = {"b": 20, "c": 3}
    config3 = {"c": 30, "d": 4}

    merged = loader.merge_configs(config1, config2, config3)

    assert merged["a"] == 1
    assert merged["b"] == 20
    assert merged["c"] == 30
    assert merged["d"] == 4


def test_deep_merge_nested_dicts():
    """Test deep merge with deeply nested dictionaries."""
    loader = ConfigLoader()

    config1 = {"level1": {"level2": {"level3": {"value": 1, "other": 2}}}}
    config2 = {"level1": {"level2": {"level3": {"value": 10}, "new": 3}}}

    merged = loader.merge_configs(config1, config2)

    assert merged["level1"]["level2"]["level3"]["value"] == 10
    assert merged["level1"]["level2"]["level3"]["other"] == 2
    assert merged["level1"]["level2"]["new"] == 3


def test_load_with_file_and_env(temp_config_dir, sample_yaml_config):
    """Test loading from both file and environment."""
    os.environ["PIPE_OVERRIDE"] = "from_env"

    try:
        loader = ConfigLoader(str(temp_config_dir))
        config = loader.load("test.yaml", use_env=True)

        # From file
        assert config["database"]["host"] == "localhost"
        assert config["logging"]["level"] == "INFO"

        # From env
        assert config["override"] == "from_env"
    finally:
        del os.environ["PIPE_OVERRIDE"]


def test_load_without_env(temp_config_dir, sample_yaml_config):
    """Test loading without environment variables."""
    os.environ["PIPE_SHOULD_NOT_LOAD"] = "ignored"

    try:
        loader = ConfigLoader(str(temp_config_dir))
        config = loader.load("test.yaml", use_env=False)

        assert config["database"]["host"] == "localhost"
        assert "should_not_load" not in config
    finally:
        del os.environ["PIPE_SHOULD_NOT_LOAD"]


def test_load_with_missing_file(temp_config_dir):
    """Test loading with missing file doesn't fail."""
    loader = ConfigLoader(str(temp_config_dir))
    config = loader.load("nonexistent.yaml", use_env=False)

    # Should return empty config when no sources available
    assert config == {}


def test_get_simple_key(temp_config_dir, sample_yaml_config):
    """Test getting simple configuration value."""
    loader = ConfigLoader(str(temp_config_dir))
    loader.load("test.yaml", use_env=False)

    assert loader.get("logging") == {"level": "INFO"}


def test_get_nested_key(temp_config_dir, sample_yaml_config):
    """Test getting nested configuration value with dot notation."""
    loader = ConfigLoader(str(temp_config_dir))
    loader.load("test.yaml", use_env=False)

    assert loader.get("database.host") == "localhost"
    assert loader.get("database.port") == 5432


def test_get_with_default(temp_config_dir):
    """Test getting configuration value with default."""
    loader = ConfigLoader(str(temp_config_dir))
    loader.config = {"existing": "value"}

    assert loader.get("existing") == "value"
    assert loader.get("nonexistent", "default") == "default"
    assert loader.get("nested.key", "default") == "default"


def test_get_nested_nonexistent(temp_config_dir):
    """Test getting nonexistent nested key returns default."""
    loader = ConfigLoader(str(temp_config_dir))
    loader.config = {"level1": {"level2": "value"}}

    assert loader.get("level1.level2") == "value"
    assert loader.get("level1.nonexistent", "default") == "default"
    assert loader.get("nonexistent.level2", "default") == "default"


def test_get_none_value(temp_config_dir):
    """Test getting key with None value."""
    loader = ConfigLoader(str(temp_config_dir))
    loader.config = {"key": None}

    assert loader.get("key", "default") == "default"


def test_load_config_convenience_function(temp_config_dir, sample_yaml_config):
    """Test convenience function load_config."""
    config = load_config("test.yaml", str(temp_config_dir))

    assert config["database"]["host"] == "localhost"
    assert config["database"]["port"] == 5432
