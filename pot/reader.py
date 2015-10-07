# -*- coding: utf-8 -*-
import urllib.request
import urllib.parse
import urllib.error
import json
import sys
import os
import urwid
import webbrowser

from subprocess import Popen
from subprocess import PIPE
from subprocess import SubprocessError

from bs4 import BeautifulSoup
from bs4 import Tag

from .pocketapi import PocketUtils



class Reader(object):

    PALETTE = [
        ("default", "dark gray", "white", "standout"),
        ("dark", "black", "white", "standout"),
        ("pg normal", "white", "dark gray", "standout"),
        ("pg complete", "black", "dark magenta"),
        ("popup", "black", "dark green"),
        ("header", "white", "white", "bold")
    ]
    
    term_w, term_h = os.get_terminal_size()
    
    def __init__(self, article, config=None):
        self.article = article
        self.config = config if config else {
            "theme": "default"
        }

        self.title = article.resolved_title if (
            len(article.resolved_title) <= self.term_w
        ) else article.resolved_title[:self.term_w - 1]

        self.buffer, self.ref = self.parse()

        self.set_up()


    def set_up(self):
        self.offset = 0
        self.size = (self.term_w, self.term_h)
        self.content = Content(self.buffer, self.ref, self.size)
        self.status = urwid.ProgressBar(
            "pg normal",
            "pg complete",
            done=len(self.buffer)-self.term_h
        )

        self.scr = urwid.Frame(
            self.content,
            urwid.Text(("header", self.title)),
            self.status)

        self.loop = urwid.MainLoop(
            self.scr,
            self.PALETTE,
            pop_ups=True,
            handle_mouse=False
        )

        urwid.connect_signal(self.content, "update_pg", self.update_pg)
        self.loop.screen.set_terminal_properties(colors=16)
        self.loop.run()

    def parse(self):
        content = self.article.text
        elinks_params = [
            "elinks",
            "-dump", "1",
            #"-dump-color-mode", "1",
            "-dump-width", str(self.term_w)
        ]

        elinks_proc = Popen(
            elinks_params,
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            universal_newlines=True
        )

        out, err = elinks_proc.communicate(content)

        if err:
            raise SubprocessError()

        article, links = self.split_at_last(
            lambda x: x.startswith("   Visible links"),
            out.splitlines(True)
        )

        return (article, links)

    def update_pg(self):
        self.status.set_completion(self.content.offset)

    def split_at_last(self, cond, seq):
        def split_list(index, seq):
            return (seq[:index - 1], seq[index:])

        for i, l in enumerate(reversed(seq)):
            if cond(l):
                return split_list(len(seq) - i, seq)


class Content(urwid.PopUpLauncher, urwid.WidgetWrap):

    __metaclass__ = urwid.MetaSignals
    signals = [
        "keypress",
        "update_pg"
    ]

    def __init__(self, buffer, links, size):
        self.buffer = buffer
        self.text = urwid.Text("")
        self.popup = Dialog(links)
        self.fill = urwid.Filler(self.text)
        self.offset = 0
        self.term_w, self.term_h = size
        super(Content, self).__init__(self.fill)

        urwid.connect_signal(self, "keypress", self.keypress)
        urwid.connect_signal(self.popup, "close", self.close_pop_up)

        self.redraw()

    def redraw(self):
        cur_e = self.offset + self.term_h - 2
        lines = self.buffer[self.offset:cur_e]

        self.text.set_text(lines)
        urwid.emit_signal(self, "update_pg")

    def keypress(self, size, key):
        def up():
            if self.offset > 0:
                self.offset -= 1

        def down():
            if (self.offset + self.term_h < len(self.buffer)):
                self.offset += 1

        def home():
            self.offset = 0

        def end():
            self.offset = len(self.buffer) - self.term_h - 1

        def page_down():
            if self.offset + 2 * self.term_h < len(self.buffer):
                self.offset += self.term_h

        def page_up():
            if self.offset - term_h > 0:
                self.offset -= self.term_h

        def r():
            self.open_pop_up()

        def q():
            raise urwid.ExitMainLoop()

        key = key.replace(" ", "_")

        if key not in locals():
            return False

        locals().get(key)()
        self.redraw()

    def create_pop_up(self):
        return self.popup

    def get_pop_up_parameters(self):
        return {
            'left': 0,
            'top': 2,
            'overlay_width': self.term_w,
            'overlay_height': self.term_h//3
        }

    def selectable(self):
        return True


class Dialog(urwid.WidgetWrap):

    signals = ["close"]

    def __init__(self, links):
        self.body = [urwid.Text(l) for l in links]
        self.listbox = urwid.ListBox(
            urwid.SimpleFocusListWalker(self.body))
        self.win = urwid.LineBox(
            self.listbox,
            title="Links"
        )

        self.attr_win = urwid.AttrMap(self.win, "popup")
        super(Dialog, self).__init__(self.attr_win)

    def keypress(self, size, key):
        if key == "q":
            urwid.emit_signal(self, "close")

        self.listbox.keypress(size, key)


class Readability(object):
    """Deprecated since i haxed Pocket API"""
    token = "4bce87cb2c7fa40f102378923718dbbc1c864317"
    api_url = "https://readability.com/api/content/v1/parser"

    def __init__(self, url):
        self.url = url
        self.article = self.retrieve()

    def retrieve(self):
        params = urllib.parse.urlencode(
            {
                "url": self.url,
                "token": self.token
            }
        )

        request = urllib.request.Request(
            '?'.join((self.api_url, params))
        )

        request_opener = urllib.request.build_opener()
        try:
            response = request_opener.open(request)
        except urllib.error.HTTPError as err:
            sys.stderr.write("{0}\n".format(err))
            return False

        article = json.loads(
            response.readall().decode("utf-8")
        )

        return article

    def get(self, *args):
        if not args:
            return self.article.keys()
        return self.article[args[0]]


class Article(object):

    def __init__(self, id, item):
        self.id = id
        self.__dict__.update(item)
        self.has_image = True if self.has_image == "1" else False
        self.has_video = True if self.has_video == "1" else False
        self.favorite = True if self.favorite == "1" else False
            
    @property
    def text(self):

        def replace_RIL(divs, pholder, links):
            for div in divs:
                itm_id = div["id"].rsplit("_", 1)[-1]
                a_tag = bs.new_tag("a", href=links[itm_id]["src"])
                a_tag.insert(0, "[{}]".format(pholder))
                div.replace_with(a_tag)
        
        response = PocketUtils.parser(self.resolved_url)
        
        if response["responseCode"] != "200":
            return
        
        bs = BeautifulSoup(response["article"], "html.parser")

        if self.has_image:
            replace_RIL(
                bs.findAll("div", class_="RIL_IMG"),
                "IMG", self.images)
             
        if self.has_video:
            replace_RIL(bs.findAll(
                "div", class_="RIL_VIDEO"),
                "VIDEO", self.videos)
        
        return bs.prettify()

