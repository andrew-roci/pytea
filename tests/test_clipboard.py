"""Tests for OSC 52 clipboard support."""

import base64
import os
from unittest.mock import patch

from snaptui.terminal import osc52_copy, osc52_read
from snaptui.keys import ClipboardMsg, _read_osc_response
from snaptui.model import set_clipboard, set_primary_clipboard, read_clipboard, read_primary_clipboard


class TestOsc52Copy:
    def test_basic_text(self):
        result = osc52_copy('hello', 'c')
        encoded = base64.b64encode(b'hello').decode()
        assert result == f'\x1b]52;c;{encoded}\x07'

    def test_primary_selection(self):
        result = osc52_copy('world', 'p')
        encoded = base64.b64encode(b'world').decode()
        assert result == f'\x1b]52;p;{encoded}\x07'

    def test_empty_string(self):
        result = osc52_copy('', 'c')
        encoded = base64.b64encode(b'').decode()
        assert result == f'\x1b]52;c;{encoded}\x07'

    def test_unicode(self):
        result = osc52_copy('café', 'c')
        encoded = base64.b64encode('café'.encode()).decode()
        assert result == f'\x1b]52;c;{encoded}\x07'

    def test_default_selection(self):
        result = osc52_copy('test')
        assert ';c;' in result


class TestOsc52Read:
    def test_clipboard_query(self):
        assert osc52_read('c') == '\x1b]52;c;?\x07'

    def test_primary_query(self):
        assert osc52_read('p') == '\x1b]52;p;?\x07'

    def test_default_selection(self):
        assert osc52_read() == '\x1b]52;c;?\x07'


class TestClipboardMsg:
    def test_creation(self):
        msg = ClipboardMsg(content='hello', selection='c')
        assert msg.content == 'hello'
        assert msg.selection == 'c'

    def test_frozen(self):
        msg = ClipboardMsg(content='hello', selection='c')
        try:
            msg.content = 'world'  # type: ignore
            assert False, 'Should be frozen'
        except AttributeError:
            pass

    def test_primary_selection(self):
        msg = ClipboardMsg(content='text', selection='p')
        assert msg.selection == 'p'


class TestReadOscResponse:
    def _make_pipe_with_data(self, data: bytes):
        """Create a pipe and write data to it, return the read fd."""
        r, w = os.pipe()
        os.write(w, data)
        os.close(w)
        return r

    def test_parse_clipboard_response_bel(self):
        """OSC 52 response terminated with BEL."""
        encoded = base64.b64encode(b'hello world').decode()
        data = f'52;c;{encoded}\x07'.encode()
        fd = self._make_pipe_with_data(data)
        try:
            result = _read_osc_response(fd)
            assert isinstance(result, ClipboardMsg)
            assert result.content == 'hello world'
            assert result.selection == 'c'
        finally:
            os.close(fd)

    def test_parse_clipboard_response_st(self):
        """OSC 52 response terminated with ST (ESC \\)."""
        encoded = base64.b64encode(b'hello').decode()
        data = f'52;c;{encoded}\x1b\\'.encode()
        fd = self._make_pipe_with_data(data)
        try:
            result = _read_osc_response(fd)
            assert isinstance(result, ClipboardMsg)
            assert result.content == 'hello'
            assert result.selection == 'c'
        finally:
            os.close(fd)

    def test_parse_primary_response(self):
        encoded = base64.b64encode(b'primary text').decode()
        data = f'52;p;{encoded}\x07'.encode()
        fd = self._make_pipe_with_data(data)
        try:
            result = _read_osc_response(fd)
            assert isinstance(result, ClipboardMsg)
            assert result.content == 'primary text'
            assert result.selection == 'p'
        finally:
            os.close(fd)

    def test_unicode_content(self):
        encoded = base64.b64encode('café ☕'.encode()).decode()
        data = f'52;c;{encoded}\x07'.encode()
        fd = self._make_pipe_with_data(data)
        try:
            result = _read_osc_response(fd)
            assert isinstance(result, ClipboardMsg)
            assert result.content == 'café ☕'
        finally:
            os.close(fd)


class TestClipboardCommands:
    def test_set_clipboard_returns_callable(self):
        cmd = set_clipboard('test')
        assert callable(cmd)

    def test_set_primary_clipboard_returns_callable(self):
        cmd = set_primary_clipboard('test')
        assert callable(cmd)

    def test_read_clipboard_returns_callable(self):
        cmd = read_clipboard()
        assert callable(cmd)

    def test_read_primary_clipboard_returns_callable(self):
        cmd = read_primary_clipboard()
        assert callable(cmd)

    @patch('snaptui.model.terminal')
    def test_set_clipboard_writes_osc52(self, mock_terminal):
        mock_terminal.osc52_copy.return_value = '\x1b]52;c;dGVzdA==\x07'
        cmd = set_clipboard('test')
        result = cmd()
        assert result is None
        mock_terminal.write.assert_called_once_with('\x1b]52;c;dGVzdA==\x07')
        mock_terminal.osc52_copy.assert_called_once_with('test', 'c')

    @patch('snaptui.model.terminal')
    def test_set_primary_clipboard_writes_osc52(self, mock_terminal):
        mock_terminal.osc52_copy.return_value = '\x1b]52;p;dGVzdA==\x07'
        cmd = set_primary_clipboard('test')
        result = cmd()
        assert result is None
        mock_terminal.write.assert_called_once_with('\x1b]52;p;dGVzdA==\x07')
        mock_terminal.osc52_copy.assert_called_once_with('test', 'p')

    @patch('snaptui.model.terminal')
    def test_read_clipboard_writes_query(self, mock_terminal):
        mock_terminal.osc52_read.return_value = '\x1b]52;c;?\x07'
        cmd = read_clipboard()
        result = cmd()
        assert result is None
        mock_terminal.write.assert_called_once_with('\x1b]52;c;?\x07')
        mock_terminal.osc52_read.assert_called_once_with('c')

    @patch('snaptui.model.terminal')
    def test_read_primary_clipboard_writes_query(self, mock_terminal):
        mock_terminal.osc52_read.return_value = '\x1b]52;p;?\x07'
        cmd = read_primary_clipboard()
        result = cmd()
        assert result is None
        mock_terminal.write.assert_called_once_with('\x1b]52;p;?\x07')
        mock_terminal.osc52_read.assert_called_once_with('p')
