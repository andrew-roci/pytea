# snaptui

Build terminal apps in Python. Your UI is a function that returns a string.

[![PyPI](https://img.shields.io/pypi/v/snaptui)](https://pypi.org/project/snaptui/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

- **Elm Architecture** — your app is `init()`, `update(msg)`, `view()`, nothing else
- **Zero dependencies** — uses only the Python standard library
- **11 ready-to-use components** — text input, select, form, table, viewport, and more
- **Faithful port of the [Charm](https://charm.sh) stack** — Bubble Tea + Lip Gloss + Bubbles + Huh, in one Python package

## Quick Start

```
pip install snaptui
```

```python
from snaptui import Style, ROUNDED_BORDER

style = Style().bold().fg("#7D56F4").padding(1, 3).border(ROUNDED_BORDER)
print(style.render("Hello from snaptui"))
```

## The Elm Architecture

Every snaptui app is three methods: `init` sets up state, `update` handles messages, and `view` returns a string to display.

```python
from snaptui import Program, KeyMsg, quit_cmd

class Counter:
    def __init__(self):
        self.count = 0

    def init(self):
        return None

    def update(self, msg):
        if isinstance(msg, KeyMsg):
            if msg.key == 'q':
                return self, quit_cmd
            elif msg.key == 'up':
                self.count += 1
            elif msg.key == 'down':
                self.count -= 1
        return self, None

    def view(self):
        return f"Count: {self.count}\n\nup/down to change, q to quit"

Program(Counter()).run()
```

After every `update()`, the renderer diffs the `view()` output line-by-line and redraws only what changed. No widget tree, no layout engine — just a string.

## Styling

Lip Gloss-style chainable builder for text formatting, borders, and spacing:

```python
from snaptui import Style

title = Style().bold().fg("#FAFAFA").bg("#7D56F4").padding(0, 1)
print(title.render("snaptui"))
```

```python
from snaptui import Style, ROUNDED_BORDER

card = Style().border(ROUNDED_BORDER).border_fg("#555").padding(1, 3).width(40)
print(card.render("Styled content with borders"))
```

Available attributes: `bold`, `dim`, `italic`, `underline`, `strikethrough`, `reverse`, `fg`, `bg`, `padding`, `margin`, `width`, `height`, `max_width`, `max_height`, `border`, `border_fg`, `align`.

## Layout

Compose styled blocks with `join_horizontal`, `join_vertical`, and `place`:

```python
from snaptui import Style, join_horizontal, join_vertical, place, CENTER

a = Style().bg("#7D56F4").padding(1, 3).render("Left")
b = Style().bg("#FF5F87").padding(1, 3).render("Right")
print(join_horizontal(CENTER, a, b))
```

## Components

**Input**: TextInput (single-line), TextArea (multi-line), Confirm (yes/no)

**Display**: Table (column-aligned data), Viewport (scrollable), Spinner (animated), Progress (bar), Help (keybinds)

**Selection**: Select (option picker), List (paginated, delegate pattern), Form (multi-field, Tab navigation)

Build multi-component interfaces with Form:

```python
from snaptui.components import Form, TextInput, Select, Confirm

form = Form()
form.add_field(TextInput(placeholder="Elara").label("Name"), key="name")
form.add_field(Select(options=["Earth", "Mars", "Europa"]).label("Destination"), key="dest")
form.add_field(Confirm(prompt="Confirm booking?"), key="ok")
```

## Program Options

```python
Program(model, alt_screen=True, mouse=True, bracketed_paste=True)
```

Advanced features: mouse events (`MouseMsg`), bracketed paste (`PasteMsg`), OSC 52 clipboard (`set_clipboard`), focus/blur tracking (`FocusMsg`), suspend/resume (Ctrl+Z), subscriptions (`Sub`).

## What's Ported

snaptui combines features from four Charm libraries into one package.

### From [Bubble Tea](https://github.com/charmbracelet/bubbletea) (v1.3.10)

| Feature | snaptui | Status |
|---------|---------|--------|
| Elm Architecture (init/update/view) | `Model` protocol, `Program` | Done |
| Message types (Key, WindowSize, Quit) | `KeyMsg`, `WindowSizeMsg`, `QuitMsg` | Done |
| Command system (async Cmd) | `Cmd`, `batch()`, `quit_cmd` | Done |
| Raw terminal mode (termios) | `terminal.make_raw()` | Done |
| Alternate screen buffer | `Program(alt_screen=True)` | Done |
| Line-diff renderer | `renderer.Renderer` | Done |
| Keyboard input parsing (70+ sequences) | `keys.read_key()` | Done |
| SIGWINCH resize handling | `terminal.listen_for_resize()` | Done |
| Mouse input events (SGR) | `MouseMsg`, `Program(mouse=True)` | Done |
| Bracketed paste events | `PasteMsg`, `Program(bracketed_paste=True)` | Done |
| Declarative View struct | `View` dataclass | Done |
| Key modifier bitfield | `Mod` IntFlag on `KeyMsg` | Done |
| Focus/blur events | `FocusMsg` | Done |
| Clipboard (OSC 52) | `ClipboardMsg`, `set_clipboard()` | Done |
| Subscriptions (long-running listeners) | `Sub`, `Model.subscriptions()` | Done |
| Suspend/resume (Ctrl+Z) | SIGTSTP/SIGCONT handling | Done |
| Kitty keyboard protocol | -- | Not yet |

### From [Lip Gloss](https://github.com/charmbracelet/lipgloss) (v1.1.0)

| Feature | snaptui | Status |
|---------|---------|--------|
| Chainable style builder | `Style` class | Done |
| Text attributes (bold, dim, italic, underline, reverse, strikethrough) | `Style.bold()`, `.dim()`, etc. | Done |
| Underline styles (curly, dotted, dashed, double) and color | `Style.underline_style()`, `.underline_color()` | Done |
| True color (24-bit RGB) | `Style.fg()`, `.bg()` | Done |
| Padding (CSS shorthand) | `Style.padding()` | Done |
| Margin (CSS shorthand) | `Style.margin()` | Done |
| Width/height constraints | `Style.width()`, `.height()` | Done |
| Max width/height | `Style.max_width()`, `.max_height()` | Done |
| Auto word-wrap on `.width()` | `Style._apply_wrap()` | Done |
| Borders (5 types, per-side, colored) | `Style.border()`, `.border_fg()` | Done |
| Horizontal alignment | `Style.align()` | Done |
| Immutable builder pattern | `Style._copy()` | Done |
| Join blocks horizontally | `join_horizontal()` | Done |
| Join blocks vertically | `join_vertical()` | Done |
| Place content in canvas (2D) | `place()` | Done |
| ANSI 16/256 color fallback | -- | Not yet |
| Adaptive colors (light/dark) | -- | Not yet |
| Vertical alignment | -- | Not yet |
| Tab width | -- | Not yet |
| PlaceHorizontal / PlaceVertical | -- | Not yet |
| Table rendering | -- | Not yet |
| List rendering (enumerators) | -- | Not yet |
| Tree rendering | -- | Not yet |

### From [Bubbles](https://github.com/charmbracelet/bubbles) (v1.0.0) + [Huh](https://github.com/charmbracelet/huh) (v0.8.0)

| Component | snaptui | Status |
|-----------|---------|--------|
| Single-line text input | `TextInput` | Done |
| Multi-line text area | `TextArea` | Done |
| Scrollable viewport | `Viewport` | Done |
| Paginated list (delegate pattern) | `List` | Done |
| Option picker (select) | `Select` | Done |
| Yes/No confirmation | `Confirm` | Done |
| Multi-field form | `Form` | Done |
| Form theme (focused/blurred styles) | `Theme`, `ThemeCharm` | Done |
| App theme (titles, borders, list items) | `AppTheme`, `AppThemeCharm` | Done |
| Table | `Table`, `Column` | Done |
| Spinner | `Spinner`, `SpinnerTickMsg` | Done |
| Progress bar | `Progress` | Done |
| Help (auto-generated keybinds) | `Help`, `KeyBinding` | Done |
| File picker | -- | Not yet |
| Timer / Stopwatch | -- | Not yet |

### From [x/ansi](https://github.com/charmbracelet/x/tree/main/ansi) (v0.11.6)

| Feature | snaptui | Status |
|---------|---------|--------|
| ANSI-aware visible width | `strutil.visible_width()` | Done |
| ANSI stripping | `strutil.strip_ansi()` | Done |
| ANSI-aware truncation | `strutil.truncate()` | Done |
| Truncate with tail | `strutil.truncate(s, w, tail="...")` | Done |
| ANSI-aware word wrap | `strutil.word_wrap()` | Done |
| ANSI-aware padding | `strutil.pad_right()` | Done |
| CJK wide character support | `strutil._char_width()` | Done |
| Grapheme cluster segmentation | -- | Not yet |
| Hard wrap (non-word-boundary) | -- | Not yet |

**Done** = implemented and tested. **Not yet** = not implemented; listed so you know what to expect.

## Status

Alpha. API may change. Python 3.11+ required. MIT license.

[GitHub](https://github.com/andrew-roci/snaptui)
