"""
Quick test script to verify tag parsing with the actual format
"""
import sys
sys.path.append('.')

from src.processor.tag_parser import parse_tags

# Test with the format you described
test_tags = [
    # Format 1: Escaped JSON-like
    '"owner":"data","environment":"production","applicationname":"arcesb"',

    # Format 2: With escaped quotes
    '\\"owner\\":\\"data\\",\\"environment\\":\\"production\\",\\"applicationname\\":\\"arcesb\\"',

    # Format 3: Full JSON
    '{"owner":"data","environment":"production","applicationname":"arcesb"}',

    # Format 4: Proper JSON with braces
    '{"applicationname": "myapp", "environment": "dev", "owner": "john"}',
]

print("Testing tag parser with different formats:\n")
print("=" * 80)

for i, tag in enumerate(test_tags, 1):
    print(f"\nTest {i}:")
    print(f"Input: {tag[:80]}...")
    result = parse_tags(tag)
    print(f"Results:")
    print(f"  Application Name: {result['Application Name']}")
    print(f"  Environment: {result['Environment']}")
    print(f"  Owner: {result['Owner']}")
    print("-" * 80)
