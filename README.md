# marklink

`marklink` is a tool for grabbing the title of an URL found in `stdin` replacing the raw url with a markdown link.

Its goal is to increase the ergonomics of writing markdown, thus leading you to write more. Effortlessly.

It is inspired by [Titler by Brett Terpstra](http://brettterpstra.com/2015/02/18/titler-system-service/) for Mac OS.

![Using marklink](marklink.gif)

# Editor integration

## Vim

```
nnoremap <leader>l :%!marklink<CR>
vnoremap <leader>l :!marklink<CR>
```

Some useful links:

[Using external filter commands to reformat HTML](http://vimcasts.org/episodes/using-external-filter-commands-to-reformat-html/)

[Formatting text with par](http://vimcasts.org/episodes/formatting-text-with-par/)

[GitHub - ferrine/md-img-paste.vim: paste image to markdown](https://github.com/ferrine/md-img-paste.vim)

# Usage

```
usage: marklink [-h] [-q] [-r] [-l] [files]

Args that start with '--' (eg. -q) can also be set in a config file
(~/.marklink). If an arg is specified in more than one place, then 
commandline values override config file values which override defaults.

positional arguments:
  files

optional arguments:
  -h, --help          show this help message and exit
  -q, --remove-query  remove query parameters
  -r, --replace-url   remove query parameters
  -l, --create-list   remove query parameters
```
