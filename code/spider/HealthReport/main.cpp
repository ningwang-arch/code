#include "spider.h"
int main(int argc, char const* argv[]) {
    Config config("");
    // std::cout << default_data << std::endl;
    Spider spider;
    auto users = config.getAll();
    for (auto& user : users) { spider.handle(user); }
    return 0;
}
