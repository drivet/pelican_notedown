# Notedown Reader for Pelican

A Pelican plugin to read the notedown format.  The notedown format
is used to display notes - short, titleless, unstructured articles on your 
pelican blog, similar to what people might call tweets.

## Whitespace

In a note, whitespace is significant and preserved via conversion to
appropriate HTML artifacts.  Specifically, this means:

* tabs are converted to 4 spaces
* newlines are converted to <br/> tags
* more than two spaces (after tab conversion) in a row are converted to &nbsp;
  characters separately


## Auto-linking

The following entities in a note are recognized and auto-linked:

* hashtags (i.e. #blah) 
* webmentions (i.e. @blah)
* URLs

URLs are auto-linked to themselves.  Hashtags and webmentions are auto-linked to
whatever is configured in the pelican config file.  For example, this config will 
auto-link to meaningful twitter links:

```
NOTEDOWN_HASHTAG_TEMPLATE = r'https://twitter.com/hashtag/{hashtag}'
NOTEDOWN_MENTION_TEMPLATE = r'https://twitter.com/{mention}'
```

Leave these empty if you don't want auto-linking for these entities.  To turn off
URL auto-linking, use:

```
NOTEDOWN_DISABLE_URL_AUTOLINKING = True
```
