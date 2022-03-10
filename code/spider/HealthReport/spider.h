#include "base64.h"
#include <boost/format.hpp>
#include <curl/curl.h>
#include <fstream>
#include <iostream>
#include <jsoncpp/json/json.h>
// #include <json/json.h>
#include <list>
#include <sstream>
#include <string.h>
#include <vector>

const std::list<std::string> list_headers = {
    "content-type: application/json", "encode: true", "X-Tag: flyio"};

const std::string base_url = "https://zhxg.whut.edu.cn/yqtjwx";
const std::string chaeckBind_url = "/api/login/checkBind";
const std::string bindUserInfo_url = "/api/login/bindUserInfo";
const std::string cancelBind_url = "/api/login/cancelBind";
const std::string isNeedCard_url = "/isNeedCrad";
const std::string monitorRegister_url = "/monitorRegister";

static std::string mail_template = "To: %s\r\n"
                                   "From: %s\r\n"
                                   "Cc: %s\r\n"
                                   "Message-ID: <dcd7cb36-11db-487a-9f3a-e652a9458efd@"
                                   "rfcpedant.example.org>\r\n"
                                   "Subject: Health Report\r\n"
                                   "\r\n"
                                   "%s\r\n";

static std::string mailContent;
static std::string respData;
static Json::Value default_data;

static std::string server;
static std::string username;
static std::string passwd;

struct upload_status
{
    size_t bytes_read;
};
static size_t getData(char* ptr, size_t size, size_t num, std::string* stream);
static size_t payload_source(char* ptr, size_t size, size_t nmemb, void* userp);


struct UserInfo
{
    std::string sn;
    std::string idcard;
    std::string mail;
    Json::Value data;
};



class Spider
{
public:
    Spider();
    void handle(UserInfo info);

    ~Spider();

private:
    bool strToJson(const std::string& body, Json::Value& root);
    void init();
    int checkBind(const std::string& sn, const std::string& idCard);
    int bindUserInfo(const std::string& sn, const std::string& idCard);
    int cancelBind();
    int isNeedCard();
    Json::Value fixtemplate(Json::Value data);
    void sendEmail(const std::string& to, const std::string& msg);
    int monitorRegister(Json::Value data);

private:
    CURL* m_curl;
    Json::StreamWriterBuilder builder;
    curl_slist* m_headers;
    std::string m_from;
    boost::format m_mailFormatter;
};

class Config
{
public:
    Config(std::string filename = "config.json");
    std::vector<UserInfo> getAll() { return m_infos; }
    ~Config();

private:
    std::vector<UserInfo> m_infos;
};
