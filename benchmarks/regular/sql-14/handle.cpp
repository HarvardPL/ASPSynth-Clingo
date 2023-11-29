#include <souffle/SouffleInterface.h>

extern "C" {
void *newProgramInstance() {
    return souffle::ProgramFactory::newInstance("bench");
}
}
