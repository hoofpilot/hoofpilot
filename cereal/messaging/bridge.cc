#include <cassert>

#include "cereal/messaging/msgq_to_zmq.h"
#include "cereal/services.h"
#include "common/util.h"

ExitHandler do_exit;

static std::vector<std::string> get_services(const std::string &whitelist_str, bool zmq_to_msgq) {
  std::vector<std::string> service_list;
  for (const auto& it : services) {
    std::string name = it.second.name;
    bool in_whitelist = whitelist_str.find(name) != std::string::npos;
    if (zmq_to_msgq && !in_whitelist) {
      continue;
    }
    service_list.push_back(name);
  }
  return service_list;
}

void msgq_to_zmq(const std::vector<std::string> &endpoints, const std::string &ip) {
  MsgqToZmq bridge;
  bridge.run(endpoints, ip);
}

void zmq_to_msgq(const std::vector<std::string> &endpoints, const std::string &ip) {
  auto poller = std::make_unique<BridgeZmqPoller>();
<<<<<<< HEAD
  auto pub_context = std::unique_ptr<Context>(Context::create());
=======
  auto pub_context = std::make_unique<Context>();
>>>>>>> b3878fb211f3a3a03acd061096da049cae17f6c3
  auto sub_context = std::make_unique<BridgeZmqContext>();
  std::map<BridgeZmqSubSocket *, PubSocket *> sub2pub;

  for (auto endpoint : endpoints) {
<<<<<<< HEAD
    auto pub_sock = PubSocket::create(pub_context.get(), endpoint, true, services.at(endpoint).queue_size);
    auto sub_sock = new BridgeZmqSubSocket();
=======
    auto pub_sock = new PubSocket();
    auto sub_sock = new BridgeZmqSubSocket();
    size_t queue_size = services.at(endpoint).queue_size;
    pub_sock->connect(pub_context.get(), endpoint, true, queue_size);
>>>>>>> b3878fb211f3a3a03acd061096da049cae17f6c3
    sub_sock->connect(sub_context.get(), endpoint, ip, false);
    if (pub_sock == nullptr) {
      delete sub_sock;
      continue;
    }

    poller->registerSocket(sub_sock);
    sub2pub[sub_sock] = pub_sock;
  }

  while (!do_exit) {
    for (auto sub_sock : poller->poll(100)) {
      std::unique_ptr<Message> msg(sub_sock->receive(true));
      if (msg) {
        sub2pub[sub_sock]->sendMessage(msg.get());
      }
    }
  }

  // Clean up allocated sockets
  for (auto &[sub_sock, pub_sock] : sub2pub) {
    delete sub_sock;
    delete pub_sock;
  }
}

int main(int argc, char **argv) {
  bool is_zmq_to_msgq = argc > 2;
  std::string ip = is_zmq_to_msgq ? argv[1] : "127.0.0.1";
  std::string whitelist_str = is_zmq_to_msgq ? std::string(argv[2]) : "";
  std::vector<std::string> endpoints = get_services(whitelist_str, is_zmq_to_msgq);

  if (is_zmq_to_msgq) {
    zmq_to_msgq(endpoints, ip);
  } else {
    msgq_to_zmq(endpoints, ip);
  }
  return 0;
}
