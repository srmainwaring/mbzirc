#include <ignition/utils/cli/CLI.hpp>

#include <iostream>
#include <string>
#include <vector>

#include <ignition/transport/Node.hh>
#include <ignition/msgs/image.pb.h>
#include <ignition/common/Image.hh>

using namespace ignition;

class ImageSaver
{
public:
  ImageSaver();

  std::vector<std::string> ListMatchingTopics(const std::string &_type);

  void SetTopic(const std::string &_topic);
  void SetFilename(const std::string &_filename) { this->filename = _filename; };

  bool Saved() const { return this->saved; };


private:
  void OnImageMsg(const msgs::Image &_msg);

private:
  transport::Node node;
  std::string filename = {"image.png"};
  std::atomic<bool> saved {false};
};

ImageSaver::ImageSaver() = default;

std::vector<std::string> 
ImageSaver::ListMatchingTopics(const std::string &_type)
{
  std::vector<std::string> matchingTopics, allTopics;
  this->node.TopicList(allTopics);
  for (auto topic : allTopics)
  {
    std::vector<transport::MessagePublisher> publishers;
    this->node.TopicInfo(topic, publishers);
    for (auto pub : publishers)
    {
      if (pub.MsgTypeName() == _type)
      {
        matchingTopics.push_back(topic);
      }
    }
  }
  return matchingTopics;
}

void
ImageSaver::SetTopic(const std::string &_topic)
{
  if(!this->node.Subscribe(_topic, &ImageSaver::OnImageMsg, this))
  {
    std::cerr << "Couldn't subscribe to topic: " << _topic << std::endl;
    return;
  }
  std::cout << "Saving from: " << _topic << std::endl;
}

void
ImageSaver::OnImageMsg(const msgs::Image &_msg)
{
  unsigned int height = _msg.height();
  unsigned int width = _msg.width();

  common::Image output;

  switch (_msg.pixel_format_type())
  {
    case msgs::PixelFormatType::RGB_INT8:
      break;
    default:
      std::cerr << "RGB8 only" << std::endl;
  }

 auto pixelFormat = common::Image::ConvertPixelFormat(
     msgs::ConvertPixelFormatType(_msg.pixel_format_type()));

 const unsigned char *data = 
   reinterpret_cast<const unsigned char*>(_msg.data().c_str());
 output.SetFromData(data, width, height, pixelFormat);

 std::cout << "Saving : " << this->filename << std::endl;

 output.SavePNG(this->filename);
 this->saved = true;
}

int main(int argc, char** argv)
{
  CLI::App app{"Ignition image saver"};

  std::string topic, filename;
  auto topicOpt = app.add_option("topic", topic, "Topic to capture");
  auto filenameOpt = app.add_option("filename", filename, "Filename to use capture");
  CLI11_PARSE(app, argc, argv);

  ImageSaver saver;

  if (!filename.empty())
  {
    saver.SetFilename(filename);
  }

  if (topic.empty())
  {
    auto topics = saver.ListMatchingTopics("ignition.msgs.Image");
    for (auto topic: topics)
    {
      std::cout << topic << std::endl;
    }
  }
  else
  {
    saver.SetTopic(topic);
    while (!saver.Saved())
    {
      std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
  }
}
