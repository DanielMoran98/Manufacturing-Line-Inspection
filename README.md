# Manufacturing Line Inspection (Computer Vision)
A computer vision project that inspects O-rings in a manufacturing line and provides automated quality assurance by detecting defective and faulty O-rings.

***All of this project was done manually. The only thing OpenCV was used for was reading in and displaying the images.***

## Approach
To detect faulty o-rings I used a number of computer vision techniques including:

- Dynamic thresholding
- Binary morphism
- Semantic segmentation
- Image classification





## Demonstration

![Output gif](https://i.imgur.com/sfcvX7L.gif)

Since this program is using vanilla python, it takes a while to process compared to using OpenCV which is just a wrapper for high performance C++ code.


## Running

To run the program on each O-ring, use ```python main.py```

To run the program on a certain O-ring, use ```python main.py <o-ring-number>```

## Built With

* [Python 3.7](https://nodejs.org/en/)


## Author

**Daniel Moran**


