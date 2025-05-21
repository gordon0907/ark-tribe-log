import io
import re

from bs4 import BeautifulSoup
from flask import Flask, render_template_string

app = Flask(__name__)

# Path to the binary ARK tribe log file
ARKTRIBE_PATH = r"\\192.168.0.100\docker\SteamCMD\steamapps\common\ARK Survival Evolved Dedicated Server\ShooterGame\Saved\SavedArks\1167393038.arktribe"


def read_int32(stream, signed=True) -> int:
    return int.from_bytes(stream.read(4), byteorder='little', signed=signed)


def read_int64(stream, signed=True) -> int:
    return int.from_bytes(stream.read(8), byteorder='little', signed=signed)


def parse_sgml_line(line: str) -> list[dict]:
    # Parse RichColor SGML-style tags into a list of segments with text and RGBA color
    pattern = re.compile(r'(.*?)<RichColor Color="([\d., ]+)">(.*?)</>')
    result: list[dict] = []

    end = 0
    for match in pattern.finditer(line):
        start, end = match.span()
        prefix_text, color_values, colored_text = match.groups()

        # Convert float RGB color values (0–1) to integer (0–255), keep alpha as float
        rgba = list(map(float, color_values.split(',')))
        rgba = [int(value * 255) for value in rgba[:3]] + rgba[3:]

        if prefix_text:
            result.append({'text': prefix_text, 'color': None})

        result.append({'text': colored_text, 'color': tuple(rgba)})

    # Add any remaining text after the last RichColor tag
    if end < len(line):
        result.append({'text': line[end:], 'color': None})

    return result


def read_tribe_log() -> list[list[dict]]:
    with open(ARKTRIBE_PATH, 'rb') as file:
        data = file.read()

    keyword = b'TribeLog\0'
    start = data.find(len(keyword).to_bytes(4, byteorder='little') + keyword)
    stream = io.BytesIO(data[start + 4 + len(keyword):])

    # Read and verify metadata structure
    length: int = read_int32(stream)
    assert stream.read(length) == b'ArrayProperty\0'
    array_size = read_int64(stream)

    length: int = read_int32(stream)
    assert stream.read(length) == b'StrProperty\0'
    num_logs = read_int32(stream)

    # Truncate stream to just the tribe log entries
    stream.truncate(stream.tell() - 4 + array_size)

    logs: list[list[dict]] = []

    # Read log entries until the stream ends
    while length := int.from_bytes(stream.read(4), byteorder='little', signed=True):
        if length < 0:
            # UTF-16 encoded string (negative value indicates wide characters)
            length = abs(length) * 2
            log_entry = stream.read(length).decode('utf-16-le')
        else:
            # ASCII encoded string
            log_entry = stream.read(length).decode('ascii')

        # Exclude the null terminator and parse the SGML markup
        logs.append(parse_sgml_line(log_entry[:-1]))

    return logs


@app.route('/')
def index():
    logs = read_tribe_log()

    html_template = """
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="utf-8"/>
            <title>ARK Tribe Log</title>
            <style>
                body {
                    background-color: #121212;
                    color: #ffffff;
                    font-family: monospace;
                    margin: 0;
                    padding: 20px;
                }
            </style>
        </head>
        <body></body>
    </html>
    """

    soup = BeautifulSoup(html_template, 'lxml')

    # Render each log entry in reverse chronological order
    for log in reversed(logs):
        div = soup.new_tag('div')

        for segment in log:
            if segment['color'] is None:
                div.append(segment['text'])
            else:
                span = soup.new_tag('span')
                span['style'] = f"color: rgba{segment['color']};"
                span.string = segment['text']
                div.append(span)

        soup.body.append(div)

    return render_template_string(soup.prettify())


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
