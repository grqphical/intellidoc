import unittest
from embeddings import DocumentChunker

class TestDocumentChunker(unittest.TestCase):
    def test_process_text(self):
        EXAMPLE_MARKDOWN = """# Hello world
foo bar baz bing bong

- one
- two
- three
- four
-five

## Number two

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure 
dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non 
proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
"""
        EXPECTED_RESULT = ['# Hello world\nfoo bar baz bing bong', '- one\n- two\n- three\n- four\n-five\n\n## Number two', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do', 'sit amet, consectetur adipiscing elit, sed do eiusmod tempor', 'adipiscing elit, sed do eiusmod tempor incididunt ut labore et', 'sed do eiusmod tempor incididunt ut labore et dolore magna', 'tempor incididunt ut labore et dolore magna aliqua.', 'Ut enim ad minim veniam, quis nostrud exercitation ullamco', 'minim veniam, quis nostrud exercitation ullamco laboris nisi ut', 'quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea', 'ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis', 'nisi ut aliquip ex ea commodo consequat. Duis aute irure', 'dolor in reprehenderit in voluptate velit esse cillum dolore eu', 'in voluptate velit esse cillum dolore eu fugiat nulla pariatur.', 'esse cillum dolore eu fugiat nulla pariatur. Excepteur sint', 'dolore eu fugiat nulla pariatur. Excepteur sint occaecat', 'eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non', 'pariatur. Excepteur sint occaecat cupidatat non', 'proident, sunt in culpa qui officia deserunt mollit anim id est', 'in culpa qui officia deserunt mollit anim id est laborum.']

        chunker = DocumentChunker(chunk_size=64)
        result = chunker._process_text(EXAMPLE_MARKDOWN)
        self.assertEqual(EXPECTED_RESULT, result)
