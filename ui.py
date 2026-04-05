import curses
import textwrap


def wrap_text_line(text, width):
    """Wraps one line of text to the available width while preserving blank lines."""
    if width <= 1:
        return [text[:1]]
    if text == "":
        return [""]
    return textwrap.wrap(text, width=width) or [""]


def center_text(text, width):
    """Centers one line of text inside a fixed-width field."""
    if width <= 0:
        return ""
    if len(text) >= width:
        return text[:width]
    padding = width - len(text)
    left_padding = padding // 2
    right_padding = padding - left_padding
    return (" " * left_padding) + text + (" " * right_padding)


def build_centered_rule(label, width, fill_char="═"):
    """Builds one centered decorative rule with a single inline label."""
    if width <= 0:
        return ""
    decorated_label = f" {label} "
    if len(decorated_label) >= width:
        return decorated_label[:width]
    remaining = width - len(decorated_label)
    left_fill = remaining // 2
    right_fill = remaining - left_fill
    return (fill_char * left_fill) + decorated_label + (fill_char * right_fill)


def get_content_bounds(width, *, max_width=100, min_margin=2):
    """Returns a centered content column sized for readable TUI composition."""
    usable_width = max(1, width - 1)
    content_width = min(max_width, usable_width - (min_margin * 2))
    if content_width < 24:
        content_width = usable_width
    left = max(0, (usable_width - content_width) // 2)
    return left, content_width


def split_centered_columns(content_left, content_width, left_ratio=0.52, gap=3):
    """Splits one centered region into two readable columns."""
    gap = min(gap, max(1, content_width // 8))
    left_width = max(28, int(content_width * left_ratio))
    right_width = content_width - left_width - gap
    if right_width < 26:
        right_width = 26
        left_width = max(24, content_width - right_width - gap)
    if left_width + right_width + gap > content_width:
        right_width = max(20, content_width - left_width - gap)
    right_left = content_left + left_width + gap
    return left_width, right_left, right_width


def draw_text_block(stdscr, start_y, start_x, width, height, lines, *, highlight_index=None):
    """Draws a wrapped block of text inside the provided bounds."""
    y = start_y
    for index, raw_line in enumerate(lines):
        wrapped_lines = wrap_text_line(raw_line, width)
        attr = curses.A_REVERSE if highlight_index == index else curses.A_NORMAL
        for wrapped_line in wrapped_lines:
            if y >= start_y + height:
                return y
            stdscr.addnstr(y, start_x, wrapped_line, width, attr)
            y += 1
    return y


def draw_centered_text_block(stdscr, start_y, total_width, block_width, height, lines, *, highlight_index=None):
    """Draws one wrapped block inside a centered column."""
    block_width = min(block_width, max(1, total_width - 1))
    start_x = max(0, (max(1, total_width - 1) - block_width) // 2)
    return draw_text_block(
        stdscr,
        start_y,
        start_x,
        block_width,
        height,
        lines,
        highlight_index=highlight_index,
    )


def draw_truncated_block(stdscr, start_y, start_x, width, height, lines, *, highlight_index=None):
    """Draws one fixed-line block without wrapping, truncating long rows in place."""
    y = start_y
    for index, raw_line in enumerate(lines):
        if y >= start_y + height:
            return y
        attr = curses.A_REVERSE if highlight_index == index else curses.A_NORMAL
        stdscr.addnstr(y, start_x, truncate_for_width(raw_line, width).ljust(width), width, attr)
        y += 1
    return y


def get_scroll_window(lines, height, offset):
    """Returns the visible slice for a simple vertical scroll window."""
    if height <= 0:
        return [], 0, 0, 0
    total_lines = len(lines)
    max_offset = max(0, total_lines - height)
    offset = max(0, min(offset, max_offset))
    return lines[offset : offset + height], offset, max_offset, total_lines


def draw_vertical_divider(stdscr, top, left, height, char="│"):
    """Draws one light vertical divider for layout separation without boxing the whole screen."""
    if height <= 0:
        return
    for row in range(top, top + height):
        stdscr.addnstr(row, left, char, 1)


def draw_box(stdscr, top, left, height, width, *, title=None):
    """Draws one light box frame using ASCII-safe characters."""
    if height < 2 or width < 2:
        return

    inner_width = max(0, width - 2)
    horizontal = "-" * inner_width
    stdscr.addnstr(top, left, "+" + horizontal + "+", width)
    for row in range(top + 1, top + height - 1):
        stdscr.addnstr(row, left, "|", 1)
        if inner_width > 0:
            stdscr.addnstr(row, left + 1, " " * inner_width, inner_width)
        stdscr.addnstr(row, left + width - 1, "|", 1)
    stdscr.addnstr(top + height - 1, left, "+" + horizontal + "+", width)

    if title and width > 4:
        title_text = f"[ {title} ]"
        stdscr.addnstr(top, left + 2, title_text[: max(0, width - 4)], max(0, width - 4), curses.A_BOLD)


def truncate_for_width(text, width):
    """Truncates one line to fit the available width with a small ellipsis."""
    if width <= 0:
        return ""
    if len(text) <= width:
        return text
    if width == 1:
        return "…"
    return text[: width - 1] + "…"


def draw_panel_text(stdscr, top, left, height, width, lines, *, highlight_index=None, wrap=True):
    """Draws text inside a boxed panel, with optional wrapping or one-line truncation."""
    if height < 3 or width < 3:
        return

    y = top + 1
    inner_height = height - 2
    inner_width = width - 2
    for index, raw_line in enumerate(lines):
        rendered_lines = wrap_text_line(raw_line, inner_width) if wrap else [truncate_for_width(raw_line, inner_width)]
        attr = curses.A_REVERSE if highlight_index == index else curses.A_NORMAL
        for rendered_line in rendered_lines:
            if y >= top + 1 + inner_height:
                return
            stdscr.addnstr(y, left + 1, rendered_line.ljust(inner_width), inner_width, attr)
            y += 1
