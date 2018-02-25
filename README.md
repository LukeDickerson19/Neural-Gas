# Neural-Gas
Neural Gas is method of data representation with applications in vector quantization, clustering, and interpolation.

<img src="https://github.com/PopeyedLocket/Neural-Gas/blob/master/Videos_and_Images/video1.gif" width="600" height="400">

The data (as seen in the top left plot) is inserted into the plot according to a random normal distribution along both the horizontal and vertical axes. The data is then placed into the bins of a 2d histogram (as seen in the top right plot). Neural Gas is grown from the data (as seen in the bottom left plot) according to the algorithm described in the paper "A Growing Neural Gas Network Learns Topologies" by Bernd Fritzke. A histogram is create from the neural gas (as seen in the bottom right plot) by doing a fourier series of the nodes in the neural gas network where a guassian normal distribution is the base function of the series and the coordinates of each node is the mean of each guassian with a constant standard deviation. 

As seen in the plots above the 2 histograms do not look particularly similar. The neural gas histogram also moves a lot while the data's histogram eventually becomes quite stable. This could be due to the fact that the data is that of a normal distribution, that itself moves a lot. Another topology was created and the hyper parameters were tuned to try to find a more stable representation of the data. The results of an I shaped topology is shown below.


<img src="https://github.com/PopeyedLocket/Neural-Gas/blob/master/Videos_and_Images/I_topology_0.png" width="400" height="250"> <img src="https://github.com/PopeyedLocket/Neural-Gas/blob/master/Videos_and_Images/I_topology_1.png" width="400" height="250">


On the left is results for the hyperparameters used in the paper, and on the right are modified hyper parameters. Modifying the hyper parameters seems to have made the neural gas, and its histogram, a more stable and accurate representation of the data for the I shaped topology. The current hyper parameter settings require more memory to store the neural gas however. Using these same hyper parameter values on the normal distribution topology yields a more stable neural gas as well, and not much change in accuracy (as can be seen in video3.mp4).

Further research will be conducted to explore better ways to convert the neural gas into a histogram. The goal is to find a method where the neural gas's histogram is very similar to the histogram of the data itself for most or all topologies.

Considering that neural gas is basically a sparser version of the data itself, other future research into other ways to create a sparser version of the data will be explored and documented in the repository Neural-Mercury (comming soon ...) to test an idea that could lead to accurately represent data as it comes in, in real time, instead of how neural gas must grow to fit the data over time.
