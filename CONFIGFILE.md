# AutoTranscode :: Automatic FFMPEG Transcoding Handler Script
Copyright © 2021 by WebMaka

# Configuration Files

AutoTranscode can use a configuration file in INI format. This contains almost
all options available via commandline but either requires or adds one: one
must EITHER provide an argument for a transcoding mode preset (e.g., "-youtube")
in the commandline OR provide a complete ffmpeg commandline sequence and
container setting in the config file. One or the other must be present, and if
both are, the config file setting will override the commandline.

The config file is a standard INI file, with the following contents:

	[paths]
	# Full path to source files
	source=

	# Full path to destination for completed transcodes
	destination=

	# Full path to storage directory for finished transcode sources
	finished=

	# Full path to ffmpeg if it's not in a PATHed directory
	ffmpeg=

	[monitor]
	# Filename extensions to monitor
	extensions=

	[transcode]
	# Custom ffmpeg commandline string
	#
	# Please note the following tokens are allowed:
	#   %FFMPEG% : Full path to ffmpeg (defaults to "ffmpeg" but requires ffmpeg to
	#              be in a directory on the system's PATH)
	#   %SPATH% : Source directory provided by caller (not generally needed here)
	#   %DPATH% : Destination directory provided by caller (not generally needed here)
	#   %SOURCEFILE% : target file (filename, with full path)
	#   %DESTFILE% : destination file (filename, with full path, but with NEW extension)
	#   %NEWEXT% : New file extension, taken from the "container" option below
	#
	# NOTE: If a custom ffmpeg commandline is provided, a container must also be
	# provided.
	custom=

	# Container for completed transcode - if a custom ffmpeg commandline string is
	# provided, a container also must be provided.
	container=

	[options]
	# Save output to debug log file (anything but an empty string enables logging.)
	debug=

	# Save ffmpeg output to log file (anything but an empty string enables logging.)
	flog=

Required items can be provided in the commandline instead of config file, but
if the same item appears in both places the config file will override the
commandline. Optional/unused selctions can be left blank.
