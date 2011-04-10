A simple browser mostly aimed at allowing you to log into multiple
different sessions/accounts at once. E.g. different gmail accounts, twitter
accounts, etc.

- google mail (normal or for domains), apps in general
- twitter
- android market

Optional features:

- select application type from template, enter username/password,
  auto-login ("keychain")

Why not ...

- Ingocnito/private browsing? All incognito/private tabs/windows run
  in the same session, so essentially you'll get two sessions max.
- Google authentication switching? It doesn't work. at all. 
- Firefox profiles. Gives you lots of windows, and if your default session
  crashes the next profile becomes the default target for new links. 
  You'll have to terminate all profiles so your default session can be
  the first again.

TODO:
- better session definition, more sensible title in top-row tabs
  - definition of session profiles (?) / apps?
- twitter view is too big -> too slow. Scroll window is max size!
- reorder tab-order
- handle window close request (eg. popin gtalk chat)
- favicon should be timeout, async
- enable/disable forward/back depending on can_*
- if there are more tabs than can fit on the screen, some are hidden

ISSUES:

Strange crash:

CHILD wrote status https://google.com/profiles
./browser.py:216: Warning: g_object_get_qdata: assertion `G_IS_OBJECT (object)' failed
  self.send("location " + p.browser.get_main_frame().get_uri())
./browser.py:216: Warning: g_type_get_qdata: assertion `node != NULL' failed
  self.send("location " + p.browser.get_main_frame().get_uri())
CHILD wrote title Hacker News | Tell HN: .ly domains starting to have problems (letter.ly)

