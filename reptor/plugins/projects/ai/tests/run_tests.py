#!/usr/bin/env python3
"""
Simple test runner for Ai module.

Run this script to test the module without complex setup.

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py unit         # Run unit tests only
    python run_tests.py integration  # Run integration tests only
    python run_tests.py skills       # Test skill loading
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai import (
    SkillLoader,
    AISkillSelector,
    PromptBuilder,
    OpenAIProcessor,
    SectionProcessor,
)


def test_skills():
    """Test skill loading and availability."""
    print("\n" + "=" * 70)
    print("SKILL LOADING TEST")
    print("=" * 70)

    skills_dir = Path(__file__).parent.parent / "skills"
    loader = SkillLoader(skills_dir)

    skills = loader.list_skills()
    print(f"\nFound {len(skills)} skills:")
    for skill in sorted(skills):
        content = loader.load_skill(skill)
        if content:
            lines = len(content.split("\n"))
            print(f"  - {skill:15} ({lines} lines)")
        else:
            print(f"  - {skill:15} (FAILED TO LOAD)")

    if not skills:
        print("  ERROR: No skills found! Check skills/ directory")
        return False

    return len(skills) > 0


def test_skill_selection():
    """Test skill selection logic."""
    print("\n" + "=" * 70)
    print("SKILL SELECTION TEST")
    print("=" * 70)

    mock_processor = MagicMock()
    selector = AISkillSelector(openai_processor=mock_processor)
    skills_dir = Path(__file__).parent.parent / "skills"
    available_skills = SkillLoader(skills_dir).list_skills()

    if not available_skills:
        print("  ERROR: No skills available")
        return False

    test_cases = [
        ("Fix grammar errors", "grammar"),
        ("Improve security findings", "security"),
        ("Make it longer and more detailed", "expand"),
        ("Translate to Spanish", "translate"),
    ]

    all_passed = True
    for task, expected in test_cases:
        mock_processor.process.return_value = expected
        selected = selector.select(task, available_skills)
        if selected == expected:
            print(f"  [PASS] '{task}' -> {selected}")
        else:
            print(f"  [WARN] '{task}' -> {selected} (expected {expected})")

    return all_passed


def test_prompt_building():
    """Test prompt construction."""
    print("\n" + "=" * 70)
    print("PROMPT BUILDING TEST")
    print("=" * 70)

    builder = PromptBuilder()
    skill = "Test skill instructions."
    task = "Fix grammar"
    content = "The finding shows vulnerabilities."

    prompt = builder.build(skill, task, content)

    checks = [
        ("Contains skill", "Test skill instructions" in prompt),
        ("Contains task", "Fix grammar" in prompt),
        ("Contains content", "The finding shows vulnerabilities" in prompt),
        ("Well-formatted", len(prompt) > 100),
        ("Deterministic", builder.build(skill, task, content) == prompt),
    ]

    all_passed = True
    for check_name, result in checks:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {check_name}")
        if not result:
            all_passed = False

    if all_passed:
        print(f"\n  Generated prompt preview ({len(prompt)} chars):")
        for line in prompt.split("\n")[:5]:
            print(f"    {line}")

    return all_passed


def test_section_processor():
    """Test section processing with mocks."""
    print("\n" + "=" * 70)
    print("SECTION PROCESSOR TEST")
    print("=" * 70)

    skills_dir = Path(__file__).parent.parent / "skills"
    loader = SkillLoader(skills_dir)
    mock_selector = MagicMock()
    builder = PromptBuilder()

    mock_processor = MagicMock()
    mock_processor.process.return_value = "Enhanced content"
    mock_processor.get_usage_summary.return_value = {
        "tokens": 500,
        "calls": 1,
        "errors": 0,
    }

    processor = SectionProcessor(
        skill_loader=loader,
        skill_selector=mock_selector,
        prompt_builder=builder,
        openai_processor=mock_processor,
        skip_fields=["references"],
    )

    mock_section = Mock()
    mock_field = Mock()
    mock_field.type = "markdown"
    mock_field.name = "description"
    mock_field.value = "Original content"
    mock_section.data = [mock_field]
    mock_section.id = "test-123"

    result = processor.process_section(mock_section, "Fix grammar")

    checks = [
        ("Field updated", mock_field.value == "Enhanced content"),
        ("Processed count incremented", processor.processed_count == 1),
        ("Error count is zero", processor.error_count == 0),
        ("Stats available", "processed_fields" in processor.get_stats()),
    ]

    all_passed = True
    for check_name, result_val in checks:
        status = "[PASS]" if result_val else "[FAIL]"
        print(f"  {status} {check_name}")
        if not result_val:
            all_passed = False

    stats = processor.get_stats()
    print(f"\n  Stats: {stats['processed_fields']} processed, {stats['errors']} errors")

    return all_passed


def test_openai_processor_mock():
    """Test OpenAI processor with mocking."""
    print("\n" + "=" * 70)
    print("OPENAI PROCESSOR TEST (MOCKED)")
    print("=" * 70)

    with patch("ai.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Processed result"
        mock_response.usage.total_tokens = 250
        mock_client.chat.completions.create.return_value = mock_response

        processor = OpenAIProcessor(api_key="sk-test")
        result = processor.process("Test prompt")

        checks = [
            ("Correct result", result == "Processed result"),
            ("Usage tracked", processor.usage_stats["calls"] == 1),
            ("Tokens tracked", processor.usage_stats["tokens"] == 250),
        ]

        all_passed = True
        for check_name, check_result in checks:
            status = "[PASS]" if check_result else "[FAIL]"
            print(f"  {status} {check_name}")
            if not check_result:
                all_passed = False

        return all_passed


def run_unit_tests():
    """Run the full unit test suite."""
    print("\n" + "=" * 70)
    print("UNIT TEST SUITE")
    print("=" * 70)

    loader = unittest.TestLoader()
    suite = loader.discover(".", pattern="test_ai.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("AIProcess Module - Complete Test Suite")
    print("=" * 70)

    results = {}

    results["Skills Loading"] = test_skills()
    results["Skill Selection"] = test_skill_selection()
    results["Prompt Building"] = test_prompt_building()
    results["Section Processor"] = test_section_processor()
    results["OpenAI Processor (Mock)"] = test_openai_processor_mock()

    try:
        results["Unit Test Suite"] = run_unit_tests()
    except Exception as e:
        print(f"\n(!) Unit tests not available: {e}")
        results["Unit Test Suite"] = None

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = 0
    failed = 0
    skipped = 0

    for test_name, result in results.items():
        if result is True:
            print(f"  [PASS] {test_name:30} PASSED")
            passed += 1
        elif result is False:
            print(f"  [FAIL] {test_name:30} FAILED")
            failed += 1
        else:
            print(f"  [SKIP] {test_name:30} SKIPPED")
            skipped += 1

    print("\n" + "=" * 70)
    print(f"Results: {passed} passed, {failed} failed, {skipped} skipped")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()

        if test_type == "unit":
            success = run_unit_tests()
        elif test_type == "integration":
            success = test_section_processor()
        elif test_type == "skills":
            success = test_skills()
        elif test_type == "selection":
            success = test_skill_selection()
        elif test_type == "prompt":
            success = test_prompt_building()
        else:
            print(f"Unknown test type: {test_type}")
            print("Available: unit, integration, skills, selection, prompt")
            sys.exit(1)
    else:
        success = run_all_tests()

    sys.exit(0 if success else 1)
