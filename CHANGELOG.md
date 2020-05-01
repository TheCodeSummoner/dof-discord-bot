# Version 1.3.0
- Added commands ordering in the help message
- Cleared log folder to only contain log files (and the `.keep` file)
- Fixed verbose log formatting
- Adjusted aliases string in the command help message
- Added alternative token configuration
- Added help alias (as per Shinrog's request)
- Added Bannerlord character code fetching

## Version 1.2.0
- Added content for Info Cog
- Moved Session and Paginator related code to utils
- Expanded `LinePaginator` (and added a new `Page` class to support that expansion)
- Adjusted `HelpSession` to be inheritable - now called a `Session`

## Version 1.1.0
 - Moved string resources to an external `YAML` file
 - Moved token loading to use a local file on the machine
 - Added a new help extension with an interactive help session
 - Added a base of the info extension with an additional (new members) welcome message - will be prepared for next version
 - Optimised a bunch of things and added more error checking
 - Adjusted some of the application form strings
 - Added `pyyaml` dependency

## Version 1.0.0
 - First version of the bot - very basic functionality
 - Added relevant accounts (Discord developer portal, *GitHub*, *ZenHub*)
 - Added apply, cancel and submit commands
 - Added per-user, direct-message application process, with progress checking and any-time cancellation