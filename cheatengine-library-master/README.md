---------------------------- ANNOUNCE (30/07/2016) ----------------------------

You have probably notice that this project has not been updated for a while.

You were probably looking for updates but i don't have the time to create new versions.

It has been for me a time-consuming project. I'm sorry to let you know that this project will not receive any bug fixes or updates in the future.

The website cheatalk.com will be removed very soon but the project will still be available on github.

If anyone is interested in pursuing this project you can fork the source code (just remember : it's open source and the original project was initiated by dark byte : http://www.cheatengine.org/)

If you want to contact me you can send me an mail at : [p-yohann][@][hotmail.fr]

Thanks to all who were supporting this project,

Best regards.

Fenix

-------------------------------------------------------------------------------


cheatengine-library
===================

Cheat Engine Library is the first open source library based on Cheat Engine a powerfull memory editing software. You may found the original software here http://cheatengine.org/

The first goal of this project is to give you the ability to make your own software with advanced features like auto assemble, dll injections, memory scanner etc. As you know, Cheat Engine doesn't provide any library and it could be very frustrating for a developer. This library is supported for both platform (x86/x64) and it is usable with popular programming languages (c#, c++, delphi).

![scanner_c](https://cloud.githubusercontent.com/assets/5822286/3718740/268557f8-163a-11e4-8585-ad3105b28859.png)

##Features :
* **manage a virtual cheat engine table**
 * add an address manually
 * add an autoassemble script
 * activate, desactivate, freeze and unfreeze any address or script
* **inject auto assemble script**
 * **supported symbols :**
    * ALLOC
    * DEALLOC
    * LABEL
    * DEFINE
    * REGISTERSYMBOL
    * UNREGISTERSYMBOL
    * INCLUDE
    * READMEM
    * LOADLIBRARY
    * CREATETHREAD
* **Scan the memory to find specific addresses**
 * **Scan type :**
    * Exact value
    * Smaller than
    * Bigger than
    * Value between
    * Unknown initial value
    * Increase value
    * Increase value by
    * Decrease value
    * Decrease value by
    * Changed value
    * Unchanged value
 * **Value type :**
    * Binary
    * Byte
    * 2 Bytes
    * 4 Bytes
    * 8 Bytes
    * Float
    * Double
    * String
  * **Memory scan options :**
    * Start address, Stop address
    * Writable, Executable, CopyOnWrite
    * Fast scan, Align and Not Align
    * Unicode, Case Sensitive

##What's new ?
**Please refer to the CHANGELOG file to get informations about the last release**

##Where should I begin ?

1. If you need an turnkey solution you should download :
 * one example (delphi, c#, or c++)
 * a wrapper for communicating with the library
 * the library available in the release page : https://github.com/fenix01/cheatengine-library/releases

2. If you need your own solution :
 * Download Lazarus 64 bits or Lazarus 32 bits
 * Copy the library and the dll directory

##Do you provide a documentation ?

Yes, I made a description of the cheat engine library apis. Follow this link https://github.com/fenix01/cheatengine-library/wiki/Guideline
