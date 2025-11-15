#!/usr/bin/env python3
"""
Test script for dynamic tag parsing
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.processor.tag_parser import parse_tags, format_column_name

print("Testing Dynamic Tag Parsing")
print("=" * 60)

# Test 1: Escaped JSON format with custom fields
print("\nTest 1: Escaped JSON with custom fields")
tag1 = '"primarycontact":"midhun jose","usage":"databricks prod env, hot storage"'
result1 = parse_tags(tag1)
print(f"Input: {tag1}")
print(f"Output: {result1}")
print(f"Expected: Primary Contact, Usage columns")

# Test 2: Standard fields
print("\nTest 2: Standard fields")
tag2 = '"owner":"data","environment":"production","applicationname":"arcesb"'
result2 = parse_tags(tag2)
print(f"Input: {tag2}")
print(f"Output: {result2}")
print(f"Expected: Owner, Environment, Application Name columns")

# Test 3: Mixed custom and standard fields
print("\nTest 3: Mixed custom and standard fields")
tag3 = '"owner":"john","primarycontact":"jane doe","costcenter":"CC123","department":"IT"'
result3 = parse_tags(tag3)
print(f"Input: {tag3}")
print(f"Output: {result3}")
print(f"Expected: Owner, Primary Contact, Cost Center, Department columns")

# Test 4: Key-value format
print("\nTest 4: Key-value format")
tag4 = "applicationname:myapp,environment:prod,usage:databricks,team:analytics"
result4 = parse_tags(tag4)
print(f"Input: {tag4}")
print(f"Output: {result4}")
print(f"Expected: Application Name, Environment, Usage, Team columns")

# Test 5: JSON format
print("\nTest 5: JSON format")
tag5 = '{"applicationname": "myapp", "primarycontact": "john doe", "project": "analytics"}'
result5 = parse_tags(tag5)
print(f"Input: {tag5}")
print(f"Output: {result5}")
print(f"Expected: Application Name, Primary Contact, Project columns")

# Test column name formatting
print("\n" + "=" * 60)
print("Testing Column Name Formatting")
print("=" * 60)

test_keys = [
    ('primarycontact', 'Primary Contact'),
    ('application_name', 'Application Name'),
    ('costcenter', 'Cost Center'),
    ('businessunit', 'Business Unit'),
    ('custom_field', 'Custom Field'),
    ('mykey', 'Mykey'),
]

for key, expected in test_keys:
    result = format_column_name(key)
    status = "✓" if result == expected else "✗"
    print(f"{status} {key:20} -> {result:20} (expected: {expected})")

print("\n" + "=" * 60)
print("All tests completed!")
