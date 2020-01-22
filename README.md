# Boxbot 2.0
  A discord bot for a variety of things.

  Boxbot was intended as a replacement to [SauceBot](https://github.com/JeremyRuhland/saucebot-discord), in addition to finding regular 4chan threads under specific tags. This serves the needs of a specific community and is optional for any other party using Boxbot.

## Source Embedding ("Sauce")
  Boxbot replaces much of the functionality of SauceBot, and extends its features to include more websites. Components are maintained through extensions called "ladles".
### Pixiv
  - Posts and albums are embedded with a preview, up to 3 images max.
  - Ugoira does not work at this time (January 2020).
### Furaffinity
  - Explicit links are embedded with submission info and an image.
### e621/e926
  - Images directly linked from e621/e926 are sourced back to their original posts.
  - Links to pools are sourced with a description, and 3 preview images are embedded in Discord.
### Imgur
  - Multi-image albums are embedded with a description and previews.
  - Sound from Imgur videos does not work due to their unique implementation of webm.
### Inkbunny
  - Albums are embedded with a description and previews.
  - Mature or Explicit links are handled for users who are not logged in.
### E-Hentai Galleries
  - Gallery links and individual pages are sourced back to the original gallery page.
  - ExHentai links are sourced back to e-hentai when possible.
### Planned Ladles
  - Weasyl

## Threadwatcher
  - Boxbot automatically searches for 4chan threads according to tags you set.
  - Threadwatcher will post in a specific channel and update a specific role when posts are made.
  - For example, Boxbot can periodically search for threads containing the text "Mao Mao" from /co/ and post them to an announcement channel, notifying a "Cartoon Fans" role upon update. 
  - This feature is optional.
