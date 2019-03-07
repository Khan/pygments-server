import logging

import flask
import pygments
import pygments.formatters
import pygments.lexers
import pygments.util


__version__ = '0.1.0 (pygments version %s)' % (pygments.__version__)

flask_app = flask.Flask(__name__)


# If running under gunicorn, set the flask log level to be the same as
# the gunicorn log level.  Based on
# https://medium.com/@trstringer/logging-flask-and-gunicorn-the-manageable-way-2e6f0b8beb2f
gunicorn_logger = logging.getLogger('gunicorn.error')
if gunicorn_logger.handlers:
    flask_app.logger.handlers = gunicorn_logger.handlers
    flask_app.logger.setLevel(gunicorn_logger.level)


_FORMATTERS = {}
_LEXERS = {}


def _get_formatter(output_format, output_style):
    if output_format not in _FORMATTERS:
        _FORMATTERS[output_format] = pygments.formatters.get_formatter_by_name(
            output_format, style=output_style,
            noclasses=False, nowrap=False, encoding='utf-8')
    return _FORMATTERS[output_format]


def _get_lexer(lang):
    if lang not in _LEXERS:
        _LEXERS[lang] = pygments.lexers.get_lexer_by_name(
            lang, encoding='utf-8')
    return _LEXERS[lang]


class ClientError(Exception):
    """Anything that would cause us to give back a 400 response."""
    pass


@flask_app.errorhandler(ClientError)
def handle_invalid_usage(error):
    response = flask.jsonify({'message': error.args[0]})
    response.status_code = 400
    return response


@flask_app.route('/_api/version', methods=['GET'])
def version():
    return "Version %s\n" % __version__, 200


@flask_app.route('/pygmentize', methods=['POST'])
def pygmentize():
    """Takes code as input and returns formatted code as output.

    Query parameters:
        lang: the programming language the input is in
        formatter: the formatter to use for output (defaults to "html")
        style: the style to use for the output (defaults to "default")
    """
    lang = flask.request.args.get('lang')
    formatter = flask.request.args.get('formatter', 'html')
    style = flask.request.args.get('style', 'default')

    if not lang:
        raise ClientError('must specify the `lang` parameter')

    try:
        formatter_class = _get_formatter(formatter, style)
    except pygments.util.ClassNotFound:
        raise ClientError('Unknown formatter "%s"' % formatter)

    try:
        lexer_class = _get_lexer(lang)
    except pygments.util.ClassNotFound:
        raise ClientError('Unknown language (for lexer) "%s"' % lang)

    result = pygments.highlight(flask.request.data,
                                lexer_class, formatter_class)

    return result, 200


def main(port, debug):
    flask_app.run(port=port, debug=debug)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Run a pygments server")
    parser.add_argument("-p", "--port", default=7878, type=int,
                        help="Port to listen for HTTP requests")
    parser.add_argument("-d", "--debug", action='store_true',
                        help="Run flask in debug mode")
    parser.add_argument("-v", "--verbose", action='store_true',
                        help="More verbose logging")
    args = parser.parse_args()

    logging.root.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    main(args.port, args.debug)
