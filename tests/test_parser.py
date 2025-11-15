"""
Unit tests for tag parser module
"""
import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from src.processor.tag_parser import parse_tags


class TestTagParser:
    """Test cases for tag parsing functionality"""

    def test_key_value_comma_separated(self):
        """Test parsing key-value pairs with comma separator"""
        tag = "app:myapp,env:production,owner:john.doe"
        result = parse_tags(tag)

        assert result['Application Name'] == 'myapp'
        assert result['Environment'] == 'production'
        assert result['Owner'] == 'john.doe'

    def test_key_value_semicolon_separated(self):
        """Test parsing key-value pairs with semicolon separator"""
        tag = "app:webapp;env:dev;owner:jane"
        result = parse_tags(tag)

        assert result['Application Name'] == 'webapp'
        assert result['Environment'] == 'dev'
        assert result['Owner'] == 'jane'

    def test_pipe_separated(self):
        """Test parsing pipe-separated values"""
        tag = "myapp|production|john.doe"
        result = parse_tags(tag)

        assert result['Application Name'] == 'myapp'
        assert result['Environment'] == 'production'
        assert result['Owner'] == 'john.doe'

    def test_json_format(self):
        """Test parsing JSON format"""
        tag = '{"app":"myapp","env":"prod","owner":"john"}'
        result = parse_tags(tag)

        assert result['Application Name'] == 'myapp'
        assert result['Environment'] == 'prod'
        assert result['Owner'] == 'john'

    def test_empty_string(self):
        """Test parsing empty string"""
        result = parse_tags("")

        assert result['Application Name'] is None
        assert result['Environment'] is None
        assert result['Owner'] is None

    def test_none_value(self):
        """Test parsing None value"""
        result = parse_tags(None)

        assert result['Application Name'] is None
        assert result['Environment'] is None
        assert result['Owner'] is None

    def test_partial_tags(self):
        """Test parsing with only some values present"""
        tag = "app:myapp,env:production"
        result = parse_tags(tag)

        assert result['Application Name'] == 'myapp'
        assert result['Environment'] == 'production'
        assert result['Owner'] is None

    def test_alternative_key_names(self):
        """Test parsing with alternative key names"""
        tag = "application:myapp,environment:prod,owner_name:john"
        result = parse_tags(tag)

        assert result['Application Name'] == 'myapp'
        assert result['Environment'] == 'prod'
        assert result['Owner'] == 'john'

    def test_whitespace_handling(self):
        """Test that whitespace is properly trimmed"""
        tag = " app : myapp , env : production , owner : john "
        result = parse_tags(tag)

        assert result['Application Name'] == 'myapp'
        assert result['Environment'] == 'production'
        assert result['Owner'] == 'john'

    def test_invalid_format(self):
        """Test parsing invalid format returns None values"""
        tag = "invalid-format-string"
        result = parse_tags(tag)

        # Should return structure even if no values found
        assert 'Application Name' in result
        assert 'Environment' in result
        assert 'Owner' in result

    def test_escaped_json_format(self):
        """Test parsing escaped JSON format (Azure tags)"""
        tag = '"owner":"data","environment":"production","applicationname":"arcesb"'
        result = parse_tags(tag)

        assert result['Application Name'] == 'arcesb'
        assert result['Environment'] == 'production'
        assert result['Owner'] == 'data'

    def test_double_escaped_json_format(self):
        """Test parsing double-escaped JSON format"""
        tag = '\\"owner\\":\\"data\\",\\"environment\\":\\"production\\",\\"applicationname\\":\\"webapp\\"'
        result = parse_tags(tag)

        assert result['Application Name'] == 'webapp'
        assert result['Environment'] == 'production'
        assert result['Owner'] == 'data'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
