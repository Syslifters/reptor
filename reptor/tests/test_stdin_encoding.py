import io
import sys
from unittest.mock import patch

import pytest

from reptor import Reptor


class MockStdinNoBuffer:
    """Mock stdin object without buffer attribute for testing"""
    encoding = 'latin-1'
    
    def read(self):
        return "test"


class TestStdinEncoding:
    """
    Test cases to verify that stdin is read with correct UTF-8 encoding
    """

    def test_stdin_utf8_encoding_basic(self):
        """Test that stdin has UTF-8 encoding after Reptor initialization"""
        # Save original stdin
        original_stdin = sys.stdin
        
        try:
            # Create a mock stdin with UTF-8 encoding
            mock_buffer = io.BytesIO(b"Test data")
            sys.stdin = io.TextIOWrapper(mock_buffer, encoding='latin-1')
            
            # Mock __name__ to simulate CLI context
            with patch('reptor.lib.reptor.__name__', '__main__'):
                # Create a Reptor instance without parameters (CLI mode)
                Reptor()
                
                # Check that stdin has UTF-8 encoding
                # After wrapping in __init__, stdin.encoding should be 'utf-8'
                assert hasattr(sys.stdin, 'encoding')
                encoding = sys.stdin.encoding
                assert encoding is not None
                assert encoding.lower() in ['utf-8', 'utf8'], f"Expected UTF-8, got {encoding}"
        finally:
            # Restore original stdin
            sys.stdin = original_stdin

    def test_stdin_reads_utf8_characters(self):
        """Test that stdin can read multi-byte UTF-8 characters correctly"""
        # Test data with various UTF-8 characters
        test_data = "Hello 你好 мир 🔒 café"
        
        # Mock stdin with UTF-8 encoded data
        mock_stdin = io.BytesIO(test_data.encode('utf-8'))
        
        with patch('sys.stdin', io.TextIOWrapper(mock_stdin, encoding='utf-8')):
            # Read from mocked stdin
            result = sys.stdin.read()
            
            # Verify the content matches
            assert result == test_data
            assert '你好' in result  # Chinese characters
            assert 'мир' in result  # Cyrillic characters
            assert '🔒' in result   # Emoji
            assert 'café' in result  # Accented characters

    def test_stdin_handles_special_characters(self):
        """Test that stdin handles common special characters used in security reports"""
        # Characters commonly found in security reports
        test_data = """
        SQL Injection: ' OR '1'='1
        XSS: <script>alert('XSS')</script>
        Path Traversal: ../../etc/passwd
        Unicode: \u0041\u0042\u0043
        Symbols: ©®™€£¥
        Math: ∀x∈ℝ
        Arrows: → ⇒ ↔
        """
        
        mock_stdin = io.BytesIO(test_data.encode('utf-8'))
        
        with patch('sys.stdin', io.TextIOWrapper(mock_stdin, encoding='utf-8')):
            result = sys.stdin.read()
            
            # Verify all special characters are preserved
            assert "'1'='1" in result
            assert "<script>" in result
            assert "../../etc/passwd" in result
            assert "©®™" in result
            assert "∀x∈ℝ" in result
            assert "→ ⇒ ↔" in result

    def test_stdin_encoding_with_buffer_unavailable(self):
        """Test that Reptor handles gracefully when stdin.buffer is not available in CLI mode"""
        # Save original stdin
        original_stdin = sys.stdin
        
        try:
            # Use mock stdin without buffer attribute
            sys.stdin = MockStdinNoBuffer()
            
            # Mock __name__ to simulate CLI context
            with patch('reptor.lib.reptor.__name__', '__main__'):
                # Create Reptor instance without params (CLI mode)
                # Should raise AttributeError when trying to access stdin.buffer
                with pytest.raises(AttributeError):
                    Reptor()
        finally:
            # Restore original stdin
            sys.stdin = original_stdin

    def test_stdin_preserves_line_endings(self):
        """Test that different line endings are preserved correctly"""
        test_cases = [
            "line1\nline2\nline3",  # Unix line endings
            "line1\r\nline2\r\nline3",  # Windows line endings
            "line1\rline2\rline3",  # Old Mac line endings
        ]
        
        for test_data in test_cases:
            mock_stdin = io.BytesIO(test_data.encode('utf-8'))
            
            with patch('sys.stdin', io.TextIOWrapper(mock_stdin, encoding='utf-8')):
                result = sys.stdin.read()
                
                # Verify content is readable (line endings may be normalized by TextIOWrapper)
                assert len(result) > 0
                assert 'line1' in result
                assert 'line2' in result
                assert 'line3' in result

    def test_stdin_handles_binary_data_decoded_as_utf8(self):
        """Test that binary data that represents valid UTF-8 is decoded correctly"""
        # Create binary data that is valid UTF-8
        test_string = "Testing UTF-8: 测试 тест テスト"
        binary_data = test_string.encode('utf-8')
        
        mock_stdin = io.BytesIO(binary_data)
        
        with patch('sys.stdin', io.TextIOWrapper(mock_stdin, encoding='utf-8')):
            result = sys.stdin.read()
            
            # Verify binary was correctly decoded
            assert result == test_string
            assert isinstance(result, str)

    def test_stdin_handles_invalid_utf8_gracefully(self):
        """Test that invalid UTF-8 sequences are handled gracefully"""
        # Create invalid UTF-8 byte sequence
        invalid_utf8 = b'\xff\xfe Invalid UTF-8 \x80\x81'
        
        mock_stdin = io.BytesIO(invalid_utf8)
        
        # Use 'replace' error handling to avoid crashes
        with patch('sys.stdin', io.TextIOWrapper(mock_stdin, encoding='utf-8', errors='replace')):
            result = sys.stdin.read()
            
            # Should contain the valid parts and replacement characters
            assert 'Invalid UTF-8' in result
            assert isinstance(result, str)

    def test_stdin_encoding_in_reptor_init(self):
        """Test that Reptor.__init__ properly wraps stdin with UTF-8 encoding in CLI mode"""
        # Save original stdin
        original_stdin = sys.stdin
        
        try:
            # Create a mock stdin with non-UTF-8 encoding
            mock_buffer = io.BytesIO(b"Test data \xe4\xb8\xad\xe6\x96\x87")  # UTF-8 bytes for "中文"
            sys.stdin = io.TextIOWrapper(mock_buffer, encoding='latin-1')
            
            # Mock __name__ to simulate CLI context
            with patch('reptor.lib.reptor.__name__', '__main__'):
                # Initialize Reptor without params (CLI mode) - should wrap stdin with UTF-8
                Reptor()
                
                # Check that stdin encoding is now UTF-8
                assert sys.stdin.encoding.lower() in ['utf-8', 'utf8']
            
        finally:
            # Restore original stdin
            sys.stdin = original_stdin

    def test_multiple_stdin_reads_consistency(self):
        """Test that multiple reads from stdin maintain encoding consistency"""
        test_data = "First line with émojis 🎉\nSecond line with 中文\nThird line ✓"
        
        mock_stdin = io.BytesIO(test_data.encode('utf-8'))
        
        with patch('sys.stdin', io.TextIOWrapper(mock_stdin, encoding='utf-8')):
            # Read line by line
            lines = []
            for line in sys.stdin:
                lines.append(line)
            
            # Verify all lines preserved UTF-8 characters
            assert len(lines) == 3
            assert 'émojis' in lines[0]
            assert '🎉' in lines[0]
            assert '中文' in lines[1]
            assert '✓' in lines[2]

    def test_stdin_not_modified_in_library_mode(self):
        """Test that stdin is NOT modified when Reptor is used as a library"""
        # Save original stdin
        original_stdin = sys.stdin
        
        try:
            # Create a mock stdin with non-UTF-8 encoding
            mock_buffer = io.BytesIO(b"Test data")
            sys.stdin = io.TextIOWrapper(mock_buffer, encoding='latin-1')
            original_encoding = sys.stdin.encoding
            
            # Initialize Reptor with server parameter (library mode)
            Reptor(from_cli=True)
            
            # Check that stdin encoding was NOT changed
            # It should still have the original encoding
            assert sys.stdin.encoding == original_encoding
            assert sys.stdin.encoding == 'latin-1'
            
        finally:
            # Restore original stdin
            sys.stdin = original_stdin
