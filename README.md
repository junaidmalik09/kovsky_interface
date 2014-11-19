# Web Interface for Kovsky Bowling Machine

<p align="center">
<img src="http://s13.postimg.org/5fzsswb6f/Screen_Shot_2014_11_19_at_2_18_15_AM.png" />
</p>

<p align="center">
<img src="http://picoolio.net/images/2014/11/19/Capturge.jpg" />
</p>

The python script, running on Beagle bone, initializes the serial and Bluetooth connections, instantiates the web server class and creates a user interface using HTML 

<p align="center">
<img src="http://picoolio.net/images/2014/11/19/ScreenShot2014-11-19at2.24.33AM.png" />
</p>

The user sets the required parameters for the ball to be bowled and presses the bowl button. That event is picked up by java script which reads the values of delivery parameters and sends them to servers request handler

<p align="center">
<img src="http://picoolio.net/images/2014/11/19/ScreenShot2014-11-19at2.24.43AM.png" />
</p>

The customized HTTP request handler receives the parameters and uses them as arguments for python functions that communicate these parameters to the bowling unit over serial connections on beagle bone peripherals

<p align="center">
<img src="http://picoolio.net/images/2014/11/19/ScreenShot2014-11-19at2.25.01AM.png" />
</p>
