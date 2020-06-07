# Author-sublime_plugin
A plugin for sublime text that improves the plain text typing experiance with better Autocomplete and Autocorrect logic.

## Installation
- `cd <Packages directory>`
- `git clone https://github.com/soumil505/Author-sublime_plugin "Author"`
<!-- end of the list -->
The Packages directory can be found in sublime text by going **Preferences->Browse Packages**

## Usage
In the language selection tab on the bottom right, choose "author".

## Features
### Dynamic autocomplete
A popup will display autocomplete suggestions while you type. Press `alt+shift+right arrow` to toggle between suggestions from your current document and suggestions from a fixed corpus of words. pressing `right arrow` when the autocomplete popup is displayed also performs the same function.

### Static autocomplete
Pressing `alt+shift+left arrow` or going **author->Get word suggestions** displays a popup menu with a list of possible autocomplete suggestions based on edit distance. 

### Misspellings
Any detected misspellings will be underlined, but making the exact same misspelling 3 or more times will cause it to be ignored.

### Get synonyms
This command (**author->get synonyms**) will display words that have the same meaning as the word the caret is currently on.

### Get definitions
This command (**author->get definitions**) will display the definitions of the word the caret is currently on.

### Fold chapter
This command (**author->fold chapter**) will fold all text between two `Chapter` keywords. A chapter keyword is the word `Chapter` (case sensitive) written at the start of a line.

