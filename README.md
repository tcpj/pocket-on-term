# pocket-on-term
Pocket client in terminal

## Usage:
Firstly, register new application at http://getpocket.com/developer. You will obtain consumer key, which is important to run this application. Then config your pot.py:

```
$ pot.py set pocket consumer_key YOUR_KEY_GOES_HERE
$ pot.py init
```

Well, after granting access, you can do whatever you want. Actualy... no.

### List articles
Simple list articles by given criterie. Using command get:

```
$ pot.py get _state_ _count_ [-t _tag_] [-f] [-s _sort_by_]
[0] Article
.
.
.
[_count_] Another article
```

### Read article
Read one of listed articles by given index from last output:

```
$ pot.py read _id_
```

Reader gui will appear. Controls are easy. Up, Down, Page Up, Page Down, Home and End. You can see links indexed like [5] by pressing "r". Popup will show up with link list. Press "q" to close. 

### Archive article
Archiving one or many articles by given index from last output:

```
$ pot.py archive _ids_
example:
$ pot.py archive 0 1 2 3
Success!
```

You can easily archive more articles

### Add article
Add an article to your list:

```
$ pot.py add _url_
OK - _resolved_title_
```

### Delete article
Delete an article from your list. Permanently:

```
$ pot.py delete 5
Success!
```

### Readding article
Revive an article from archive:

```
$ pot.py readd 5
Success!
```

### Favorite/Unfavorit article
Make your article favorited. Or take it's favoritness away:

```
$ pot.py favorite 5 6
$ pot.py unfavorite 6
```

### Tags!
Tagging your articles. Examples:

```
$ pot.py tag add 1 5 6 --tags rekt smashing_tag puppets
$ pot.py tag remove 1 --tags rekt
$ pot.py tag replace 6 --tags kittens
$ pot.py tag clear 5
```

Your homework: figure out, what each command does :)

### LICENSE

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
