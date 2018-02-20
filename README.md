# Neural-Gas
Neural Gas is method of data representation with applications in vector quantization, clustering, and interpolation.

<img src="https://github.com/PopeyedLocket/Neural-Gas/blob/master/video1.gif" width="600" height="400">

The data (as seen in the top left plot) is inserted into the plot according to a random normal distribution along both the horzontal and vertical axes. The data is then placed into the bins of a 2d histogram (as seen in the top right plot). Neural Gas is grown from the data (as seen in the bottom left plot) according to the algorithm described in the paper "A Growing Neural Gas Network Learns Topologies" by Bernd Fritzke. A histogram is create from the neural gas (as seen in the bottom right plot) by doing a fourier series of the nodes in the neural gas network where a guassian normal distribution is the base function of the series and the coordinates of each node is the mean of each guassian with a constant standard deviation. 

As seen in the plots above the 2 histograms do not look particularly similar. The neural gas histogram also moves a lot while the data's histogram eventually becomes quite stable. This could be due to the fact that the data is that of a normal distribution. Other topologies could yield better results.

Further research will be conducted to determine the histograms of different data topologies, and to explore better ways to convert the neural gas into a histogram. The goal of which is to find a method where the neural gas's histogram is very similar to the histogram of the data itself for most or all topologies.
