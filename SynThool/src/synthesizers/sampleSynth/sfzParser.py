HEADER, OPCODE, VALUE = 'HEADER', 'OPCODE', 'VALUE'
REGION, GROUP, CONTROL, GLOBAL, CURVE, EFFECT, MASTER, MIDI, SAMPLE = \
'<region>', '<group>', '<control>', '<global>', '<curve>', '<effect>', '<master>', '<midi>', '<sample>'
pos = 0

def parser(tokens):
    result = {
        'control': {},
        'regions': []
    }
    global_header = {}
    group = {}
    region = {}
    header = None
    key = None

    for token in tokens:
        token_type = token[0]
        token_value = token[1]

        if token_type == HEADER:
            header = token_value

            if len(region):
                result['regions'].append(region)

            if header == GROUP:
                group = {}

            elif header == REGION:
                region = {}
                region.update(global_header)
                region.update(group)

        elif token_type == OPCODE:
            key = token_value

        elif token_type == VALUE:
            if header == CONTROL: result['control'][key] = token_value
            elif header == GLOBAL: global_header[key] = token_value
            elif header == GROUP: group[key] = token_value
            elif header == REGION:
                if key == 'sample':
                    # prefix = result['control']['default_path'] or ''
                    prefix = ''
                    region[key] = prefix + token_value
                else:
                    region[key] = token_value
            else:
                header_name = header[1:-1]
                result[header_name] = result[header_name] if header_name in result else {}
                result[header_name][key] = token_value

            key = None

    if len(region):
        result['regions'].append(region)

    return result

def is_value(text, pos):
    char = text[pos]

    return char >= '0' and char <= '9' \
        or char >= 'A' and char <= 'Z' \
        or char >= 'a' and char <= 'z' \
        or char == '.' \
        or char == ':' \
        or char == '\\' \
        or char == '/' \
        or char == '-' \
        or char == '_' \
        or char == '#' \
        or char == '$' \
        or char == ' ' \
        and not is_end_of_value(text, pos + 1)

def is_end_of_value(text, pos):
    while is_opcode(text[pos]):
        pos += 1
        if is_equal(text[pos]): return True

    if is_comment(text, pos): return True

    return False

def is_header(char):
    return char == '<' \
        or char == '>' \
        or char >= 'a' and char <= 'z'

def is_end_of_header(char):
    return char == '>'

def is_opcode(char):
    return char >= '0' and char <= '9' \
        or char >= 'a' and char <= 'z' \
        or char == '_'

def is_space(char):
    return char == ' ' \
        or char == '\t'

def is_equal(char):
    return char == '='

def is_comment(text, pos):
    return text[pos] == '/' and text[pos + 1] == '/'

def is_newline(char):
    return char == '\n' \
        or char == '\r'

def next_token(text):
    global pos

    if is_space(text[pos]):
        while is_space(text[pos]):
            pos += 1

    if is_newline(text[pos]):
        while is_newline(text[pos]):
            pos += 1

    if is_comment(text, pos):
        while not is_newline(text[pos]):
            pos += 1

    if is_equal(text[pos]):
        token_type = VALUE
        token_value = ''
        pos += 1

        while is_value(text, pos):
            token_value += text[pos]
            pos += 1

        return [token_type, token_value]

    elif is_opcode(text[pos]):
        token_type = OPCODE
        token_value = ''

        while is_opcode(text[pos]):
            token_value += text[pos]
            pos += 1

        return [token_type, token_value]

    elif is_header(text[pos]):
        token_type = HEADER
        token_value = ''

        while is_header(text[pos]) and not is_end_of_header(text[pos - 1]):
            token_value += text[pos]
            pos += 1

        return [token_type, token_value]

def lexer(text):
    global pos
    tokens = []

    while pos < len(text) - 1:
        token = next_token(text)
        if token: tokens.append(token)

    pos = 0

    return tokens

def read_file(filename):
    file = open(filename, 'r', encoding='utf-8')
    text = ''.join(file.readlines())
    return text

def load(filename):
    text = read_file(filename)
    tokens = lexer(text)
    result = parser(tokens)
    return result

if __name__ == '__main__':
    result = load('example.sfz')
    print(result['regions'])
