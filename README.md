# pocket-on-term
[![Build Status](https://travis-ci.org/jaduse/pocket-on-term.svg?branch=master)](https://travis-ci.org/jaduse/pocket-on-term)
Pocket client in terminal

## Installation
Currently only from github:

```
$ pip install git+https://github.com/jaduse/pocket-on-term
```

## Usage:
Firstly, register new application at http://getpocket.com/developer. You will obtain consumer key, which is important to run this application. Then config your pot.py:

```
$ pot set pocket consumer_key YOUR_KEY_GOES_HERE
$ pot init
```

Well, after granting access, you can do whatever you want. Actualy... no.

### List articles
Simple list articles by given criterie. Using command get:

```
$ pot get _state_ _count_ [-t _tag_] [-f] [-s _sort_by_] [-o _offset_]
[0] Article
.
.
.
[_count_] Another article

$ pot get unread 5 -t programming -o 5 # so, you want 5 unread articles, with "programming" tag, and you want start from fifth article. So you want 5 articles that come after article 5, so you get articles 6, 7, 8, 9 and 10. 
 ```

### Read article
Read one of listed articles by given index from last output:

```
$ pot read _id_
```

Reader gui will appear. Controls are easy. Up, Down, Page Up, Page Down, Home and End. You can see links indexed like [5] by pressing "r". Popup will show up with link list. Press "q" to close. 

### Archive article
Archiving one or many articles by given index from last output:

```
$ pot archive _ids_
example:
$ pot archive 0 1 2 3
Success!
```

You can easily archive more articles

### Add article
Add an article to your list:

```
$ pot add _url_
OK - _resolved_title_
```

### Delete article
Delete an article from your list. Permanently:

```
$ pot delete 5
Success!
```

### Readding article
Revive an article from archive:

```
$ pot readd 5
Success!
```

### Favorite/Unfavorit article
Make your article favorited. Or take it's favoritness away:

```
$ pot favorite 5 6
$ pot unfavorite 6
```

### Tags!
Tagging your articles. Examples:

```
$ pot tag add 1 5 6 --tags rekt smashing_tag puppets
$ pot tag remove 1 --tags rekt
$ pot tag replace 6 --tags kittens
$ pot tag clear 5
```

Your homework: figure out, what each command does :)

## LICENSE

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
