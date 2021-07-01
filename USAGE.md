# AutoTranscode :: Automatic FFMPEG Transcoding Handler Script
Copyright © 2021 by WebMaka

# Usage:

**[sudo] python auto_transcode.py TRANSCODE [OPTIONS ...] -s /full/source/path -d /full/dest/path [-f /full/finished/path] [-ffmpeg /full/path/to/ffmpeg] [-config /full/path/to/configfile]**

NOTE: This script requires elevated privileges. On Windows machines, an
administrator-level account or UAC elevation is required. On Linux machines,
run the script via sudo.

NOTE: The script's argument/parameter parser doesn't require these be in any 
particular order aside from requiring that a parameter immediately follow its 
argument, e.g., specifying a source path with "-s" requires that the path be
immediately after the "-s".


## Path Arguments

NOTE: Paths that contain whitespace will have to be enclosed in double-quotes, 
as a space is a separator in commandline arguments.

**-s /full/source/path**  
Source directory to monitor for files to auto-transcode. This must be a full
path to a DIRECTORY which this script will monitor for files to auto-transcode.
The best option to use here is a drop directory that a video source can use
as a save directory. This directory must allow file rename/delete permissions
to this script.

**-d /full/dest/path**  
Destination path for transcoded files. This must be a full path to a DIRECTORY
into which ffmpeg will place the new video files it creates. This directory 
must allow file create/write permissions to this script.

**-f /full/finished/path** (OPTIONAL)  
Destination path for source files once they've been transcoded. This must be a
full path to a DIRECTORY into which each source file will be moved ocne ffmpeg
has transcoded it. This directory must allow file create/write permissions to
this script. IF THIS IS NOT PROVIDED, this script will append ".processed" to
the end of each file's name once ffmpeg completes transcoding.

**-ffmpeg /full/path/to/ffmpeg** (OPTIONAL)  
Full path to ffmpeg, for situations where ffmpeg is not in a directory in the
system's PATH, there are multiple ffmpeg installations, etc. If this is not
specified, the script will just try to call "ffmpeg" without specifying a path,
and if ffmpeg can't be found that way an error to that effect will be thrown.

**-config /full/path/to/configfile** (OPTIONAL)  
Full path to AND NAME OF a configuration file for this script. The config file
must be in INI format and have specific sections and fields - consult the config
file documentation for specifics. NOTE: config file values will override the 
corresponding commandline arguments/parameters if the same entry appears in both
places. Also, unless a custom ffpmeg commandline is specified, the transcode
mode (e.g., "-davinci") is still required.



## TRANSCODE Arguments:

These select the preset transcoding commandline for ffmpeg. A few presets are 
provided, and a custom ffmpeg commandline can be used via config file.

NOTE: Unless a config file is being used and said config file has a custom
ffmpeg commandline and container defined, one of these choices MUST be provided.
Otherwise, an error will occur and the script will exit.

The included presets are as follows:

**-davinci**  
Transcodes into a working format for Davinci Resolve 16+ on Linux. Converts to 
MPEG4 video and linear PCM 16-bit (SE) audio with maxed-out quality. This can 
produce big video files (half a gigabyte plus per minute of runtime at 1080p60) 
so make sure you have a lot of storage space. The results are packed into a 
Quicktime MOV container.

**-youtube**  
Transcodes into a highly compressed format that conforms to Youtube's preferred 
upload formatting guidelines as of 15 Dec 2020. Converts to H.264 video and AAC 
320kbps audio with the "fast start" option enabled and with settings optimized 
for Youtube uploading and conversion. The results are packed into a MPEG4 MP4 
container. This preset is preconfigured to output at 1920x1080 resolution and 
60mbps bitrate as per Youtube's reccomendations.

**-dnxhr**  
Transcodes into Avid DNxHR-HQ 4:2:2 format, which is a workhorse "intermediate" 
format for many NLEs. This format produces extremely high-detail working files 
that recompress well, albeit at the cost of enormous file sizes (multiple 
gigabytes per minute of runtime at 1080p60) so make sure you have a lot of 
storage space. The results are packed into a Quicktime MOV container.

**-prores**  
Transcodes into Apple ProRes (4444 profile) format, which is a workhorse 
"intermediate" format for many NLEs. This format produces extremely high-detail 
working files that recompress well, albeit at the cost of enormous file sizes 
(multiple gigabytes per minute of runtime ato 1080p60) so make sure you have a 
lot of storage space. The results are packed into a Quicktime MOV container.

**-plexhd**  
Transcodes to a format that streams well over Plex, without requiring additional 
server-side transcoding. Files are scaled to 1080p, framerate is scaled to 30FPS,
and videos with aspect ratios other than 16x9 are either leterboxed or pillarboxed 
to fit a 16x9 display.

**-plexsd**  
Transcodes to a format that streams well over Plex, without requiring additional 
server-side transcoding. Files are scaled to 720p, framerate is scaled to 30FPS,
and videos with aspect ratios other than 16x9 are either leterboxed or pillarboxed 
to fit a 16x9 display.


## OPTIONS Arguments:

**-c CONTAINER**  
Transcode container - sets the container via file extension, e.g., "mov" for 
Quicktime MOV, "mkv" for Matroska MKV, "avi" for Windows AVI, "mp4" or "m4v" 
for MPEG4, etc. etc. etc. This is automatically set when using a transcode 
preset (above), but MUST be set manually if providing a custom ffmpeg command-
line via config file

**-e EXTENSIONS**  
Filename extensions to watch for and act upon. This can be a list of extensions
but must be comma-separated and not include whitespace or punctuation, e.g., 
"mp4,m4v,mov". Default extensions are "mp4,m4v,mkv,webm,mov".

**-debug**  
Enables debug logging, which writes all output except that from ffmpeg itself
to a text file in the same directory as the script.

**-flog**  
Enables debug logging for ffmpeg, which writes all of ffmpeg's output to a text
file in the same directory as the script. WARNING: THIS FILE CAN BECOME HUGE!

**--version**  
Reports version and Copyright information and then exits.

**--help**  
Prints usage text and then exits.


END!
