Twitinerary
===========

A tweet scheduler.
------------------

Twitinerary is a tweet scheduler built on Google App Engine and Django, which I
created in collaboration with my designer friend [Alex
Swanson](http://alexswanson.net/). Based on his desire for a simple but
graceful tweet scheduler, I wrote a rough prototype as a means of learning App
Engine, then gradually fleshed it out based on brainstorming sessions with
Alex. Though we planned to integrate a user interface created by Alex and
deploy the app to the masses, we abandoned Twitinerary for other projects
before reaching completion.

My focus throughout the project was on building a rich user interface using
jQuery UI, eliminating transitions between pages. Noteworthy is Twitinerary's
time handling, which deals solely in the user's local time zone URL shortening
and image uploading support are built-in.

A prime challenge in building Twitinerary was to interface with Twitter's OAuth
API. Beginning from a base of Mike Knapp's
[AppEngine-OAuth-Library](http://github.com/mikeknapp/AppEngine-OAuth-Library/),
I rewrote most of the code as I became intimately familiar with OAuth, fixing a
number of bugs and adding new functionality as I went.
