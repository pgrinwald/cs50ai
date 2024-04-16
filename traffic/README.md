Systematically experimented with the following:

1. The number of convolutional layers.
2. The number of pooling layers in between convolutional layers.
3. The numbers of hidden layers in between convolutional layers and output layers.
4. The dropout percentage.

Conclusions:
- Adding convolutional layers did not improve accuracy.  It often creates negative
  dimension sizes beween the layers. 
- Adding a pooling layer after each convolutional layer improved performance of the 
  model significantly.  Accuracy was approximately the same.
- Adding Dense layers before the output layer had an adverse effect on accuracy.
- A dropout percentage of 0.4 appears to be optimal.

