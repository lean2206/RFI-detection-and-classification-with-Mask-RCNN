# RFI Detection with Mask-RCNN
This software is capable of detecting and classifying radio frecuency interference, present in spectrograms. The software uses the Mask RCNN framework (https://github.com/matterport/Mask_RCNN) to do the RFI detection and clasification, and AWS EC2 servers for storage and processing. This software was developed to assist the Chineese-argentinian Radio Telescope (CART)  (http://cart.unsj.edu.ar/proyecto.php) located in San Juan - Argentina.

Specifically, this software detects every RFI present in the spectrogram and classify them as Narrow Band (NB), Intermediate Band (IB) or Wide Band (WB) according to their band width. This system, is a very useful tool for those professionals in charge of preventing the CART to damage because of powerful RFI, present in the location. 

# Results

![](Results/res1.PNG)

![](Results/res2.PNG)

![](Results/res3.PNG)

![](Results/res4.PNG)

# System Architecture

![](system-architecture.PNG)
