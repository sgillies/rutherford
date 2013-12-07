"""
Rutherford

Atom feed extension for Tinkerer.

:copyright: Copyright 2013 Sean Gillies
:license: BSD, see LICENSE file
"""

from datetime import datetime
import logging
import os.path
from urlparse import urlparse

from jinja2 import Environment, PackageLoader
import pytz
from sphinx.util.compat import Directive
from tinkerer import __version__ as tinkerer_version
from tzlocal import get_localzone

log = logging.getLogger('rutherford')

class SummaryDirective(Directive):
    """Optional summary metadata for posts and pages.

    From http://tools.ietf.org/html/rfc4287#section-4.2.13:

      The "atom:summary" element is a Text construct that conveys a
      short summary, abstract, or excerpt of an entry.

      It is not advisable for the atom:summary element to duplicate
      atom:title or atom:content because Atom Processors might assume
      there is a useful summary when there is none.

    The directive is not rendered, just stored in the 
    metadata and passed to the templating engine.
    """

    required_arguments = 0
    optional_arguments = 100
    has_content = False

    def run(self):
        """Called when parsing the document."""
        env = self.state.document.settings.env
        summary = " ".join(self.arguments)
        env.blog_metadata[env.docname].summary = summary
        return []


def generate_feed(app, err):
    """Generates Atom feed."""
    if err is not None:
        log.warning("error found at build-finished, feed not written")
        return None

    env = app.builder.env
    # don't do anything if no posts are available
    if not env.blog_posts:
        return
    context = dict()

    # Some parts of the tag: URI to be used for ids.
    parts = urlparse(app.config.website)
    netloc = parts.netloc
    idpath = parts.path.strip('/').replace("/", ":")
    
    tz = get_localzone()
    
    # feed items
    context["entries"] = []

    for post in env.blog_posts[:app.config.posts_per_page]:
        
        link = "%s%s.html" % (app.config.website, post)

        timestamp = env.blog_metadata[post].date.isoformat()
        entry_date = timestamp.split('T')[0]
        
        # updated time
        post_path = os.path.join(app.srcdir, post + ".rst")
        mtime = os.path.getmtime(post_path)
        mdt = datetime.fromtimestamp(mtime)
        updated = tz.localize(mdt).isoformat()

        categories = [
            category[1] for category in 
            ( env.blog_metadata[post].filing["categories"]
              + env.blog_metadata[post].filing["tags"])]

        context["entries"].append({
            "title": env.titles[post].astext(),
            "id": "tag:%s,%s:%s:%s" % (
                netloc, entry_date, idpath, post[11:]),
            "link": link,
            "summary": getattr(env.blog_metadata[post], 'summary', None),
            "categories": categories, # terms
            "published": timestamp,
            "updated": updated,
            "author": env.blog_metadata[post].author,
            "content": env.blog_metadata[post].body,
        })

    # feed metadata 
    context["title"] = app.config.project
    context["id"] = "tag:%s,%s:%s" % (
        netloc, app.config.blog_date, idpath)
    context["link"] = app.config.website
    context["subtitle"] = app.config.tagline
    context["language"] = "en-us"
    context["rights"] = app.config.rights
    context["tinkerer_version"] = tinkerer_version
  
    # feed pubDate is equal to latest post pubDate
    context["updated"] = context["entries"][0]["updated"]

    jenv = Environment(loader=PackageLoader('rutherford', 'templates'))
    template = jenv.get_template('feed.xml')
    with open(os.path.join(app.outdir, 'feed.atom'), 'w') as f:
        f.write(template.render(context).encode('utf-8'))


def add_atom_context(app, pagename, templatename, context, doctree):
    """Add items to HTML page context"""
    context["rights"] = app.config.rights

def setup(app):
    # new config values
    app.add_config_value('blog_date', "2013", True)
    app.add_config_value("rights", "", True)

    # new directives
    app.add_directive("summary", SummaryDirective)
 
    # event handlers
    app.connect("html-page-context", add_atom_context)
    app.connect("build-finished", generate_feed)

