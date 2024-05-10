# Membership bot
#### Video demo: https://youtu.be/yI6ehJnBqKM
## Description
A Telegram bot designed to help small businesses (mainly fitness-oriented ones) to keep track of their members and memberships.
## Features
* Supports English and Russian languages, set on user-by-user basis.
### Member side
* Register
* Request admin (business representative) to add membership
* Request admin to freeze their active membership
* Unfreeze their frozen membership
* Check in after attending
* Delete member and their data
* View:
    * active membership data (dates of purchase, activation and expiry, the amount of times the membership can be used)
    * dates of check-in for current active membership
    * all purchased memberships
### Admin side
#### Done by interacting with the bot itself
* Add memberships to members who requested them (or deny the requests). Set membership value
* Confirm check-ins sent in by members
#### Done by changing config values
* Set business name
* Set Telegram user ids for administrators
* Set possible values for memberships
* Set expiry period for memberships
* Set maximum freeze period for memberships
## File structure
### Project root
* `config_reader.py` - file responsible for reading the values from configuration file and abstracting them into a singleton instance of a class along with locale settings. 
* `project.py` - file with main function that launches te bot as well as a couple of menu-forming functions.
* `README.md` - this file, documentation.
* `requirements.txt` - a list of libraries needed for this project to run.
* `test_project.py` - tests for function in `project.py`.
* `.env_template` - a template file showing which values the user needs to configure for the bot to work.
### src
Keeps all source code for the bot.
#### db_calls
Keeps all database-related code that uses the sqlalchemy library.
* `__init__.py` - references other files in this directory for use through fixtures.
* `admin.py` - functions that make actual database calls as called by admin-side bot handlers.
* `database.py` - class that defines a database class using a singleton pattern.
* `member.py` - functions that make actual database calls as called by member-side bot handlers.
* `user.py` - functions that make actual database calls as called by user setting related (registration, info update) bot handlers.
#### locales
Keeps all localization/internationalization-related files.
* `*.po` files are localization sources containing code line numbers and strings that should be there as well as lines of translation that the former should be replaced with.
* `*.mo` files are compiled `*.po` files that the application actually reads.
* `*.pot` file is a base for future `*.po` files.
#### model
Keeps classes that correspond to the tables of the application's database and house actual business logic where applicable.
* `attendance.py` - simple class, only has a table config and a representation method.
* `declarative_models.py` - a base class for all other models in this module, it ensures that they work with sqlalchemy.
* `membership.py` - the beefiest of the classes, since the application's main objective is to manage memberships. 
Handles logic for activation, check-ins, freeze and unfreeze, manages related dates, keeps track of uses the membership has left.
* `request.py` - simple class that corresponds to all the requests a member can create for the admin to process.
Takes a enum to determine which type of request it's actually dealing with.
* `user.py` - another basic class with a table config + representation string. 
The app doesn't do any complicated user management, so there is not much here.
#### routers
Keeps all routers and handlers - all code that actually defines how the bot will interact with users' messages.
* `__init__.py` - references other files in this directory for use through fixtures.
* `att_for_admin.py` - admin-side handlers related to attendance/check-ins.
* `att_for_member.py` - member-side handlers related to attendance/check-ins.
* `for_admin.py` - admin-side handlers that cannot be placed in one other file.
* `for_member.py` - member-side handlers that cannot be placed in one other file.
* `helpers.py` - pieces of other functions that I had to reuse several times and thus factored them out into their own functions.
* `mb_for_admin.py` - admin-side handlers related to memberships.
* `mb_for_member.py` - member-side handlers related to memberships.
* `misc.py` - catch-all handlers and a couple of others I wasn't sure where to place.
* `user.py` - handlers related to the user managing their info (registration or updates).
#### utils
Keeps additional files and helpers that I couldn't place in any other folder. 
* `bot_helpers.py` - functions or classes that are directly related to the bot's operation 
but cannot be bundled in with any of the handlers. 
* `callback_factories.py` - there are several flows where I need to pass data between handlers. 
This is where I define the factories that play a key role in this process.
* `constants.py` - a couple of enums to ensure I don't make a typo in callback factory names.
* `decorators.py` - a bit of a misnomer, since there is only one, for a singleton pattern I use for database and config management.
* `menu.py` - houses functions that assemble keyboards for the user to interact with. 
Some of them are used so many times (like the main menu) that it was silly not to make it its own function, 
and others are just too bulky (like the callback factory assembling ones) to have in the actual handler code.
### tests
Keeps all the tests for the bot (except tests in test_project.py).
* `conftest.py` - fixtures to use in tests.
* `helper.py` - small helper functions that are only helpful in tests.
* `test_membership_class.py` - tests for the logic inside the Membership class. 
There is a lot of it, and it doesn't need to be tested together with the handles in test_handlers.py.
* `test_handlers.py` - tests for handlers of the bot.
