#include <opencv2/opencv.hpp>
#include <stdio.h>

#include <client_comm.h>

using namespace cv;

int main(int argc, char** argv) {
  if (argc != 2) {
    printf("usage: DisplayImage.out <Image_Path>\n");
    return -1;
  }

  Mat image;
  image = imread(argv[1], 1);

  if (!image.data) {
    printf("No image data \n");
    return -1;
  }
  namedWindow("Display Image", WINDOW_AUTOSIZE);
  imshow("Display Image", image);

  socket_comm::Client client = socket_comm::Client();
  bool connected_to_server = client.init();
  if (connected_to_server) {
    client.send_image(image);
  }

  waitKey(0);

  return 0;
}