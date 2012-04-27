# Copyright (C) 2011, J. Ignacio Alvarez <neonigma@gmail.com>

# This file is part of Anobii API access.

# Anobii API access is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Anobii API access is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Anobii API access. If not, see <http://www.gnu.org/licenses/>.

import sys
import hashlib
import urllib
from xml.etree.ElementTree import XML, tostring, fromstring

class AnobiiShelf:
    
    def __init__(self, api_key, secret, user_id, lang, progress, limit, start):
        self.api_key = api_key
        self.api_sig = hashlib.md5(api_key + secret).hexdigest()
        self.user_id = user_id
        self.lang = lang
        self.progress = progress
        self.limit = limit
        self.start = start

    def getApiSig(self):
        return self.api_sig

    def getBookShelf(self):
        url = "http://api.anobii.com/shelf/getSimpleShelf?api_key="+self.api_key
        url += "&api_sig="+self.api_sig+"&user_id="+self.user_id
        if self.lang: url +="&lang="+self.lang
        if self.progress: url += "&progress="+self.progress
        if self.limit: url += "&limit="+self.limit
        if self.start: url += "&start="+self.start

        #print url

        return urllib.urlopen(url).read()

    def getConfData(self):
        return {'api_key': self.api_key, 'api_sig': self.api_sig, 'user_id': self.user_id, 
                'lang': self.lang, 'progress': self.progress, 'limit': self.limit,
                'start': self.start}

class AnobiiBook:

    def __init__(self, book_id, confdata):
        self.book_id = book_id
        self.confdata = confdata

    def getBookData(self):
        url = "http://api.anobii.com/item/getInfo?api_key="+self.confdata['api_key']
        url += "&api_sig="+self.confdata['api_sig']+"&item_id="+self.book_id

        #print url
       
        return urllib.urlopen(url).read()

class AnobiiContributor:

    def __init__(self, book_id, contrib_id, confdata):
        self.book_id = book_id
        self.contrib_id = contrib_id
        self.confdata = confdata

    def getContributorData(self):
        url = "http://api.anobii.com/contributor/getInfo?api_key="+self.confdata['api_key']
        url += "&api_sig="+self.confdata['api_sig']+"&contributor_id="+self.contrib_id
        url += "&item_id="+self.book_id

        #print url
       
        return urllib.urlopen(url).read()

class BookHandler:

    def __init__(self, confdata, content):
        self.confdata = confdata
        self.content = content
        self.books = []
 
    def parse_contrib(self, contrib_content, new_book):
        tree = fromstring(contrib_content)
        items = tree.findall("roles/role")

        for item in items:
            for contrib_data in item.items():
                if contrib_data[0] == 'name':
                    new_book.update({contrib_data[0] : contrib_data[1]})
               
    def parse_book(self, book_content, book_id, new_book, item_to_parse):
        tree_book = fromstring(book_content)
        iterator = tree_book.getiterator()

        for element in iterator:
            if element.tag == item_to_parse:
                item_list = element.items()
                for item in item_list:
                    if item[0] == "id" and item_to_parse == "contributor":
                        acontrib = AnobiiContributor(book_id, item[1], self.confdata)
                        self.parse_contrib(acontrib.getContributorData(), new_book)
                    if item[1] != "" and item[0] != "id":
                        new_book.update({item[0] : item[1]})

    def parse_books(self):
        tree = fromstring(self.content)
        books = tree.findall("items/item")
  
        for book in books:
            new_book = {}
            for book_data in book.items():
                if book_data[0] == "id":
                    new_book.update({'id': book_data[1]})
                    abook = AnobiiBook(book_data[1], self.confdata)
                    self.parse_book(abook.getBookData(), book_data[1], new_book, "item")
                    self.parse_book(abook.getBookData(), book_data[1], new_book, "contributor")
                elif book_data[1] != "":
                    new_book.update({book_data[0] : book_data[1]})
            self.books.append(new_book)

    def getBooks(self):
        return self.books

api_key = sys.argv[1]
secret = sys.argv[2]
user_id = sys.argv[3]
lang = sys.argv[4]

anobii = AnobiiShelf(api_key, secret, user_id, lang, None, None, None)
content = anobii.getBookShelf()

handler = BookHandler(anobii.getConfData(), content)
handler.parse_books()
print handler.getBooks()

