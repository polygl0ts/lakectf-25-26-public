# Beyond Root

+ Author: Hackin7
+ Category: onsite
+ Intended difficulty: easy/medium
+ Solves during competition: 6/10

Setup
1. Place the camera & a wifi hotspot in an unspecified location
2. Point the camera such that people can find where it is from the location
3. Configure the camera to connect to the challenge server

Solve Path
1. Get the camera image from the web portal
2. Configure the camera to send config.json (with WiFi Credentials)
3. Go to onsite and connect to the camera shell
4. Connect to the camera shell. There will be hint of SPIFFS shell (so no directories)
5. get the flag at `/../flag.txt`

To Fix
1. improve authentication between challenge server and camera
2. Make the challenge either less guessy or maybe harder idk

Considerations
1. Need to regularly update the camera to avoid participants corrupting the config.json or the flag
