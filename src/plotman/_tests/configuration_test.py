"""Tests for plotman/configuration.py"""
import importlib.resources

import pytest
import yaml

from plotman import configuration
from plotman import resources as plotman_resources


@pytest.fixture(name='config_text')
def config_text_fixture():
    return importlib.resources.read_text(plotman_resources, "plotman.yaml")


def test_get_validated_configs__default(config_text):
    """Check that get_validated_configs() works with default/example plotman.yaml file."""
    res = configuration.get_validated_configs(config_text, '')
    assert isinstance(res, configuration.PlotmanConfig)

def test_tool_interactive_should_be_none(config_text):
    """When tools/interacting doesn't exist, its configuration property should be None"""
    loaded_yaml = yaml.load(config_text, Loader=yaml.SafeLoader)
    
    del loaded_yaml["tools"]["interactive"]
    reloaded_yaml = configuration.get_validated_configs(yaml.dump(loaded_yaml, Dumper=yaml.SafeDumper), '')
    assert reloaded_yaml.tools.interactive is None

def test_tool_section_does_not_exist(config_text):
    """When tools doesn't exist, its configuration property should be None"""
    loaded_yaml = yaml.load(config_text, Loader=yaml.SafeLoader)
    
    del loaded_yaml["tools"]
    reloaded_yaml = configuration.get_validated_configs(yaml.dump(loaded_yaml, Dumper=yaml.SafeDumper), '')
    assert reloaded_yaml.tools is None

def test_get_validated_configs__malformed(config_text):
    """Check that get_validated_configs() raises exception with invalid plotman.yaml contents."""
    loaded_yaml = yaml.load(config_text, Loader=yaml.SafeLoader)

    # Purposefully malform the contents of loaded_yaml by changing tmp from List[str] --> str
    loaded_yaml["directories"]["tmp"] = "/mnt/tmp/00"
    malformed_config_text = yaml.dump(loaded_yaml, Dumper=yaml.SafeDumper)

    with pytest.raises(configuration.ConfigurationException) as exc_info:
        configuration.get_validated_configs(malformed_config_text, '/the_path')

    assert exc_info.value.args[0] == f"Config file at: '/the_path' is malformed"


def test_get_validated_configs__missing():
    """Check that get_validated_configs() raises exception when plotman.yaml does not exist."""
    with pytest.raises(configuration.ConfigurationException) as exc_info:
        configuration.read_configuration_text('/invalid_path')

    assert exc_info.value.args[0] == (
        f"No 'plotman.yaml' file exists at expected location: '/invalid_path'. To generate "
        f"default config file, run: 'plotman config generate'"
    )


def test_loads_without_user_interface(config_text):
    loaded_yaml = yaml.load(config_text, Loader=yaml.SafeLoader)

    del loaded_yaml["user_interface"]

    stripped_config_text = yaml.dump(loaded_yaml, Dumper=yaml.SafeDumper)

    reloaded_yaml = configuration.get_validated_configs(stripped_config_text, '')

    assert reloaded_yaml.user_interface == configuration.UserInterface()


def test_get_dst_directories_gets_dst():
    tmp = ['/tmp']
    dst = ['/dst0', '/dst1']
    directories = configuration.Directories(log='', tmp=tmp, dst=dst)

    assert directories.get_dst_directories() == dst


def test_get_dst_directories_gets_tmp():
    tmp = ['/tmp']
    directories = configuration.Directories(log='', tmp=tmp)

    assert directories.get_dst_directories() == tmp


def test_dst_is_dst():
    tmp = ['/tmp']
    dst = ['/dst0', '/dst1']
    directories = configuration.Directories(log='', tmp=tmp, dst=dst)

    assert not directories.dst_is_tmp()


def test_dst_is_tmp():
    tmp = ['/tmp']
    directories = configuration.Directories(log='', tmp=tmp)

    assert directories.dst_is_tmp()
