#ifndef Field_hpp

#include "Cam.hpp"
#include "Robot.hpp"

#include <algorithm>

class Field{
private:
  Cam m_cam;
  std::map<int,Robot> m_robots;

  void parseOptions(int argc, char* argv[]);
  void updateRobots();
public:
  Field(int argc, char* argv[]);
  void loop();
};

#endif
