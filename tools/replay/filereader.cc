#include "tools/replay/filereader.h"

#include "common/util.h"
#include "tools/replay/py_downloader.h"

std::string FileReader::read(const std::string &file, std::atomic<bool> *abort) {
  const bool is_remote = (file.find("https://") == 0) || (file.find("http://") == 0);
  const std::string local_file = is_remote ? cacheFilePath(file) : file;
  std::string result;

  if ((!is_remote || cache_to_local_) && util::file_exists(local_file)) {
    result = util::read_file(local_file);
  } else if (is_remote) {
    result = download(file, abort);
    if (cache_to_local_ && !result.empty()) {
      std::ofstream fs(local_file, std::ios::binary | std::ios::out);
      fs.write(result.data(), result.size());
    }
  }
  return result.empty() && !is_remote ? util::read_file(file) : result;
}
