# p2pp - **Palette2 Post Processing tool for PrusaSlicer/Slic3r PE**

## IMPORTANT
This is a backup and continuation of Tom Vandeneed's repository, as they decided p2pp was no longer working with newer slicers. 
I have put up this repository with the last version of Tom's code. 
I will be fixing stuff I personally have problems with if i am able.
I will take this down if Tom wants me to.
There are still references to Tom Vandeneed, please do not bother him, he is no longer responsible for P2PP
There are no wikies anymore, but the pdf's still exist in this repo under docs
A list of fixes and features will be added to the bottom as they happen.

**ONLY THE PYTHON (.py) FILES WORK AT THE MOMENT**
Use ```python3 p2pp/p2pp.py ...``` instead of ```p2pp.exe ...``` 

## Getting strarted
TODO:
Have a look at the [P2PP Wiki pages](https://github.com/ThomasNyk/p2ppUnofficial) to get youstarted.


## Acknowledgements

Thanks to.....
Tim Brookman for the co-development of this plugin.
Klaus, Khalil ,Casey, Jermaul, Paul, Gideon,   (and all others) for the endless testing and valuable feedback and the ongoing P2PP support to the community...it's them driving the improvements...
Kurt for making the instructional video n setting up and using p2pp.

## Make a donation...

If you like this software and want to support its development you can make a small donation to support further development of P2PP.

[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=t.vandeneede@pandora.be&lc=EU&item_name=Donation+to+P2PP+Developer&no_note=0&cn=&currency_code=EUR&bn=PP-DonationsBF:btn_donateCC_LG.gif:NonHosted)



## **Good luck & happy printing !!!**

#Extra Features and fixes so far:
- Fixed accessory mode ping accuracy
- Added pressure advance control(for klipper only) - Eg(in printer start gcode): ;P2PP PRESSURE_ADVANCE_AMOUNT=0.05. You will also have to make a gcode substitution for: "SET_PRESSURE_ADVANCE ADVANCE=0" to ""(nothing) in prusaslicer under print -> output options -> Other




