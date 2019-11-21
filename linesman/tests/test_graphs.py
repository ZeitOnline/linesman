import unittest
import sys
from cProfile import Profile

from mock import Mock, patch

import linesman


class TestGraphUtils(unittest.TestCase):

    @patch("networkx.to_agraph")
    def test_draw_graph(self, mock_to_agraph):
        """ Test that the graph gets converted to an agraph """
        mock_draw = Mock()
        mock_to_agraph.return_value = mock_draw

        graph = "some graph object"
        output = "/tmp/somefile.png"
        linesman.draw_graph(graph, output)

        mock_to_agraph.assert_called_with(graph)
        mock_draw.draw.assert_called_with(output, prog="dot")

    def test_generate_key_builtin(self):
        """ Test that a key is generated for built-in functions """
        stat = Mock()
        stat.code = "__builtin__"
        key = linesman._generate_key(stat)
        self.assertEqual(key, stat.code)

    def test_generate_key_module(self):
        """ Test that a key is generated for module functions """
        def test_func():
            pass

        stat = Mock()
        stat.code = test_func.__code__

        expected_key = "%s.%s" % (self.__module__, stat.code.co_name)
        key = linesman._generate_key(stat)
        self.assertEqual(key, expected_key)

    @patch("linesman.getmodule", Mock(return_value=None))
    def test_generate_key_unknown(self):
        """ Test that unknown module functions return as strings """
        def test_func():
            pass

        stat = Mock()
        stat.code = test_func.__code__

        expected_key = "%s.%s" % (stat.code.co_filename, stat.code.co_name)
        key = linesman._generate_key(stat)
        self.assertEqual(key, expected_key)

    def test_create_graph(self):
        """ Test that a graph gets generated for a test function """
        def test_func():
            pass
        prof = Profile()
        prof.runctx("test_func()", locals(), globals())
        graph = linesman.create_graph(prof.getstats())

        nodes = [node for node in graph.nodes()]
        nodes.sort()

        # Python2 and three differ in the default callstack
        if sys.version_info[0] < 3:
            self.assertEqual(len(graph), 3)
            self.assertEqual(nodes, ["<method 'disable' of '_lsprof.Profiler' objects>", '<string>.<module>', 'linesman.tests.test_graphs.test_func'])
            # Assert that the three items we have are as expected
            self.assertEqual(nodes, ["<method 'disable' of '_lsprof.Profiler' objects>", '<string>.<module>', 'linesman.tests.test_graphs.test_func'])
            edges = [x for x in graph.edges()]
            self.assertEqual(
                [('<string>.<module>', 'linesman.tests.test_graphs.test_func')],
                edges)
        else:
            self.assertEqual(len(graph), 4)
            self.assertEqual(nodes, ["<built-in method builtins.exec>", "<method 'disable' of '_lsprof.Profiler' objects>", '<string>.<module>', 'linesman.tests.test_graphs.test_func'])
            self.assertEqual(nodes, ["<built-in method builtins.exec>", "<method 'disable' of '_lsprof.Profiler' objects>", '<string>.<module>', 'linesman.tests.test_graphs.test_func'])
            # Assert that the correct edges are set-up

            edges = [x for x in graph.edges()]
            self.assertEqual(
                [('<built-in method builtins.exec>', '<string>.<module>'), ('<string>.<module>', 'linesman.tests.test_graphs.test_func')],
                edges)
