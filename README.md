# AutoTranscode :: Automatic FFMPEG Transcoding Handler Script


Copyright © 2021 by WebMaka


This script watches a specific directory for new files with specific file 
extensions, and transcodes any file with the proper extension into specific
formats for purposes like importing into a NLE, uploading to Youtube, etc.

Originally built as an import/export handler for uploading Twitch streams
to Youtube, this script is built to move H.264 files into Linux NLEs that
may not natively support H.264, and then transcode edited videos back into
H.264 for faster uploads to Youtube.

By default, this script assumes the video being input runs at 60FPS, and
exports to the same. Lower-framerate video sources, or video sources with
variable framerates, will have frames added to bring them up to a constant
60FPS. The input/output resolutions are left undeclared but are assumed to
be 1920x1080, at least for the Youtube preset - the other presets are set
to run at whatever the input resolution happens to be.

The transcode presets include:

-davinci : Transcodes into a working format for Davinci Resolve 16+ on 
		   Linux. Converts to MPEG4 video and linear PCM 16-bit (SE) audio
		   with maxed-out quality. This can produce big video files (half a 
		   gigabyte plus per minute of runtime at 1080p60) so make sure
		   you have a lot of storage space. The results are packed into a
		   Quicktime MOV container.

-youtube : Transcodes into a highly compressed format that conforms to
		   Youtube's preferred upload formatting guidelines as of 15 Dec
		   2020. Converts to H.264 video and AAC 320kbps audio with the 
		   "fast start" option enabled and with settings optimized for
		   Youtube uploading and conversion. The results are packed into a
		   MPEG4 MP4 container. This preset is preconfigured to output at
		   1920x1080 resolution and 60mbps bitrate as per Youtube's
		   reccomendations.

-dnxhr   : Transcodes into Avid DNxHR-HQ 4:2:2 format, which is a workhorse
		   "intermediate" format for many NLEs. This format produces extremely 
		   high-detail working files that recompress well, albeit at the cost 
		   of enormous file sizes (multiple gigabytes per minute of runtime
		   at 1080p60) so make sure you have a lot of storage space. The 
		   results are packed into a Quicktime MOV container.

-prores  : Transcodes into Apple ProRes (4444 profile) format, which is a
		   workhorse "intermediate" format for many NLEs. This format 
		   produces extremely high-detail working files that recompress 
		   well, albeit at the cost of enormous file sizes (multiple 
		   gigabytes per minute of runtime ato 1080p60) so make sure you
		   have a lot of storage space. The results are packed into a 
		   Quicktime MOV container.

-plexhd/-plexsd : Transcodes into MP4 files optimized for delivery over Plex streaming 
                   servers with minimal need for server-side transcoding. These formats
		   use MPEG4 video and AAC audio, in either 1808p (-plexhd) or 720p
		   (-plexsd) with settings intended to work without further server-side
		   transcoding on the vast majority of Plex clients, including game
		   consoles. Video that is in a different aspect ratio than 16x9 is
		   automatically letterboxed or pillarboxed as required, and the
		   framerate is adjusted to 30FPS.

This script also supports the use of a configuration file for all of its
commandline options, and the config file also grants the capability to
use a custom ffmpeg commandline and container selection. For more info
on this, see CONFIGFILE.md.


## REQUIREMENTS

This script requires the following:

- Python 3.8+. It may work on other (especially older) versions, but was 
  built on version 3.8.5.
  
- A reasonably recent installation of ffmpeg. Again, other/older versions
  may work, but this script was built against version 4.2.4 for Linux and
  4.3.1 for Windows.
  
- FOR LINUX USERS: A reasonably recent installation of fuser. Many distros
  include it, but if it's missing, "sudo apt install psmisc" (or whatever
  package manager your distro uses) will fetch and install it. NOTE: This
  is not needed for Windows.
  
- A Linux distribution or Windows version that supports all of the above.
  This script was tested against Ubuntu 20.04 LTS and Windows 10 Pro
  version 1909. Yet again, other distros/version may work.
  
- Elevated permissions on the host OS. For Linux, this script should be
  run via sudo (but NOT in a root shell - sudo only the script!), and for
  Windows, administrator rights will be required and UAC may prompt for
  this. This is because files are getting created/renamed and access
  controls or badly set permissions may interfere.
  
- A ridiculous amount of very fast storage, especially if using DNxHR or
  ProRes transcodes. Filesizes on these can easily reach into the 250+GB
  per hour range at 1080p60.    


## PLEASE SUPPORT MY PROJECTS

If this script helps your workflow, please consider donating to help 
support my projects, including this one. Any amount helps and will be
very much appreciated.

As a thank-you for supporting my work, donators and Patrons get early access
to updates to this script, as well as having a means to directly request
features.

To donate via PayPal, please follow this link:

https://www.paypal.com/donate?hosted_button_id=GMFCGQALGUNYG

To donate via Patreon, please follow this link:

https://www.patreon.com/webmaka

