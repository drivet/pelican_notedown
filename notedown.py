from pelican import signals
from pelican.readers import BaseReader
import re
import markdown


mention_re = re.compile("(^|\s)([＠@]{1}([^\s#<>[\]|{}]+))", re.UNICODE)
hashtag_re = re.compile("(^|\s)([＃#]{1}(\w+))", re.UNICODE)
link_re = re.compile("(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)", re.UNICODE)

# lookbehind matching.  Only match whitespace that has whitespace behind it
multispace_re = re.compile(r"(?<=\s)\s")


def extract_hashtags(text):
    return [m[2] for m in hashtag_re.findall(text)]


def extract_webmentions(text):
    return [m[2] for m in mention_re.findall(text)]


def extract_links(text):
    return [m[0] for m in link_re.findall(text)]


def convert2html(text, url_linking, hashtag_template, mention_template):
    if url_linking:
        text = link_re.sub(r'<a href="\1">\1</a>', text)

    if hashtag_template:
        text = hashtag_re.sub(r'\1<a href="' + hashtag_template.format(hashtag=r'\3') + r'">\2</a>', text)

    if mention_template:
        text = mention_re.sub(r'\1<a href="' + mention_template.format(mention=r'\3') + r'">\2</a>', text)

    # we'll say, somewhat arbitrarily, that tabs are replaced by four spaces
    text = text.replace('\t', '    ')
    text = multispace_re.sub('&nbsp;', text)
    text = text.replace('\n', '<br/>')

    return text


def read_whole_file(filename):
    with open(filename, 'r') as content_file:
        content = content_file.read()
    return content


def extract_metadata(metadata_text):
    md = markdown.Markdown(extensions=['meta'])
    md.convert(metadata_text)

    metadata = {}
    for key, value in md.Meta.items():
        metadata[key] = "\n".join(value)
    return metadata


class NotedownReader(BaseReader):
    enabled = True
    file_extensions = ['nd']

    def read(self, filename):
        contents = read_whole_file(filename)

        meta_text = contents.split("\n\n", 2)
        metadata = extract_metadata(meta_text[0] + "\n\n")

        parsed = {}
        for key, value in metadata.items():
            parsed[key] = self.process_metadata(key, value)
        self._meta(parsed, meta_text[1])

        url_linking_disabled = self.settings.get('NOTEDOWN_DISABLE_URL_AUTOLINKING')
        hashtag_template = self.settings.get('NOTEDOWN_HASHTAG_TEMPLATE')
        mention_template = self.settings.get('NOTEDOWN_MENTION_TEMPLATE')

        return convert2html(meta_text[1], not url_linking_disabled, hashtag_template, mention_template), parsed

    def _meta(self, parsed, text):
        # title is just the whole text
        parsed['title'] = self.process_metadata('title', text)

        hashtags = extract_hashtags(text)
        if hashtags:
            parsed['hashtags'] = self.process_metadata('hashtags', hashtags)

        webmentions = extract_webmentions(text)
        if webmentions:
            parsed['webmentions'] = self.process_metadata('webmentions', webmentions)

        links = extract_links(text)
        if links:
            parsed['links'] = self.process_metadata('links', links)


def add_reader(readers):
    for ext in NotedownReader.file_extensions:
        readers.reader_classes[ext] = NotedownReader


def register():
    signals.readers_init.connect(add_reader)
