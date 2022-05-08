# The Responder:

[Link to repository](https://github.com/ddcroft73/Responder)<br>
The responder is a sister app to Tizzle. It is not required but offers extra functionality in that it allows user that receive recurring texts the option to disable said texts if they would like to. Alternatively since I designed Tizzle to be wary of spam abuse the user could just let the recurring texts play out. Still the functionality is there. I developed it in a seperate directory than Tizzle because it just seems to perform better that way. It was likely a moot decision and will work fine but this is just how I ended up doing it. It needs to at this point be ran in its own terminal window. I am working with multi threading to get Tizzle to launch it but as it is now it will only launch it once. As soon as you stop it (It must be stopped with Tizzle.), it will no longer occupy that thread. And as of now I havent put a lot of effort int o threading. But it's on the agenda. My main focus is getting the responder to respond texts sent from the Tizzle receivers and do its job.


