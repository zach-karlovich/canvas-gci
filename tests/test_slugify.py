from canvas_gci.fs import slugify

test_cases = [
    ("01-Module 1 - Getting Yourself Unstuck", "m1-getting-yourself-unstuck"),
    ("Module 2: The Art of Prompting", "m2-the-art-of-prompting"),
    ("10-module-10-Advanced Techniques", "m10-advanced-techniques"),
    ("No Module Here", "no-module-here"),
    ("module 05_Another Example", "m5-another-example"),
    (
        "This is just a Topic, not a module",
        "this-is-just-a-topic-not-a-module",
    ),
    ("Module6WithoutSpace", "m6-withoutspace"),
    (
        "  Module 7 - Leading and Trailing Spaces   ",
        "m7-leading-and-trailing-spaces",
    ),
    (
        "Module 8 - Very Long Name That Will Exceed Sixty Characters Limit For Sure",  # noqa: E501
        "m8-very-long-name-that-will-exceed-sixty-characters-limit-fo",  # noqa: E501
    ),
    ("module 9", "m9"),
    ("Another test without module", "another-test-without-module"),
    ("MODULE 11 - Uppercase Module", "m11-uppercase-module"),
    ("12-Module 12 with Number Prefix", "m12-with-number-prefix"),
]

for i, (input_str, expected_output) in enumerate(test_cases):
    actual_output = slugify(input_str)
    print(f"Test Case {i + 1}:")
    print(f"  Input:    '{input_str}'")
    print(f"  Expected: '{expected_output}'")
    print(f"  Actual:   '{actual_output}'")
    assert actual_output == expected_output, (
        f"Test Case {i + 1} FAILED! "
        f"Expected '{expected_output}', got '{actual_output}'"
    )
    print("  Result:   PASSED")

print("\nAll slugify test cases passed!")
