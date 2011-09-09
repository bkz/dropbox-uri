*Work in progress*

## Overview

This is a proof of concept prototype which implements a URI sharing mechanism
for Dropbox shared folders. In a team environment you often want to share links
to items in shared folders but Dropbox makes this task pretty annoying. You
have to manually type or copy and paste paths in emails or via IM and then
manually navigate to the items of interest. The experimental "Get Shareable
Link" is pretty broken as well since it gives you a (public!) shortened URL
which will re-download the item instead of pointing directly to copy you
already have in your local Dropbox folder.

## Design goals:

  - Sender should be able to navigate to a shared folder, select a sub-set of
    items (files and folders) and be able share a set of links via Gmail.

  - Reciever should be able to click on a link and securely be navigated to the
    matching item independent of how he/she has mounted the shared folder.

  - Reciever should only be able to access the linked item if he/she has access
    to shared folder.

  - Reciever should not have to download the item multiple times, if the item
    is available locally he/she will be able to access it via a suitable link.

This prototype implements a very simple mechanism which allows you to
right-click on files and directories in shared folders and generate Dropbox
URIs, "HTML links" which are saved to the clipboard ready to be pasted into
Gmail or your IM client. Team-members who have installed the program will be
able to click on such links and a new Finder/Explorer window will open with the
item selected. Note: we won't execute or open the selected item with its
associated program to keep things simple and not introduce possible security
issues.

## Example:

  - Right clicking on ~/Dropbox/Shared/Folder/Item.ext woud generate a Dropbox
    URI similar to this which you can paste into an email:

    [/Folder/Item.ext](#) -> dropbox:fhksd838ejsfg3g3489ffh38hf

  - Clicking on this link will locate the shared folder on the reciever end and
    select the mathcing file or directory.

## Disclaimer:

Binaries are available but you should really build this yourself, I'm not that
keen on maintaing this for public usage. I'd rather have the Dropbox team
implement this feature for everyone :)

## OSX installation:

  Download the binary distribution or fetch the source, install Py2App and run
  "python setup.py" to build DropboxURI.app (look in the dist folder).

  Copy DropboxURI.app into the /Applications folder. You need run this
  application at least once before it will trigger on Dropbox links so go ahead
  and double-click on it (it runs silently so nothing will happen).

  Add a menu-item to the Finder right-click menu for generating Dropbox URIs
  using Automator (screenshots [1][s1] and [2][s2]):

  - Launch Automator, create new service, from the "Library" choose "Utilities"
    and drag and drop "Run shell script" to the workflow.

  - Set "Services recieves selected" to "files and folders" and limit the
    applications to "Finder". In the "Run Shell Script" pane set "pass input"
    to "as arguments" and paste the following line into text area (change the
    path if needed):

      open -a /Applications/DropboxURI.app "$@"

  - Hit Cmd+S and select a name for the action (e.g. Copy Dropbox URI).

### OSX usage:

  - Right-click on an item in a shared folder and select the "Copy Dropbox URI"
    menu entry. Links are generated and placed in the clipboard.

  - Paste the clipboard content in Gmail or your IM client.

  - Clicking on a Dropbox link (URI) will open a new Finder window which has
    the item selected.

## Windows installation:

  Download and run the installer (setup.exe) OR follow these instructions:

  Fetch the source, build and copy the platform wapper library "platform.dll"
  to the same folder as the main.py script. You need Python 2.6+ and Py2Exe to
  build the executable using "python setup.py".

  To install the right-click menu entry and register the URI handler run the
  following from an (elevated) admin propmpt:

  DropboxUri.exe [/install] [/uninstall]

### Windows usage:

  - Right-click on an item in a shared folder, navigate to the "Send To" menu
    and select "Copy Dropbox URI". Links are generated and placed in the
    clipboard.

  - Paste the clipboard content in Gmail or your IM client.

  - Clicking on a Dropbox link (URI) will open a new Explorer window which has
    the item selected.

## Techincal:

The prototype should handle shared folders properly as it creates the URI by
combining the namespace ID from the mount_table and a relative path for the
item. During lookup the full path is simply reconstructed from the namespace
and relative path. Unicode paths should also be handled correctly.

A shareable URI basically looks something like this:

    dropbox:Njk1NDEzM3xcQXZzdMOkbmduaW5nXFRlc3TDhMOWw4Vc2KfZhNi52LHYqNmKLnR4dA

The "dropbox:" part is the protocol handler which is registered with the OS, it
allows browsers and other applications to trigger our program (handler) so that
we can look up the item and possible navigate to it. The remaning stuff is
basically base64(shared folder namespace id, item relative path) which we use
to determine to correct path.

Since we want to be able to paste the links where ever HTML is accepted we
fallback to using standard HTML links with a simply webservice since many
applications dont't allow or won't parse raw protocol URIs correctly. Browsers
will handle our URIs correctly so we'll simply let the browser trigger the
protocol handler instead of relying on the transport medium (Gmail, IM, etc):

1. Generate URI -> dropbox:34fsd23s089d...

2. Embed URI in webservice URL -> http://www.sharedropbox.com/34fsd23s089d...

3. Reconstruct URI in browser and let it trigger the local protocol handler
   (and offer the user to install the handler if he/she hasn't done so).

## The End.

[s1]: https://github.com/bkz/dropbox-uri/raw/master/doc/osx1.png
[s2]: https://github.com/bkz/dropbox-uri/raw/master/doc/osx2.png
