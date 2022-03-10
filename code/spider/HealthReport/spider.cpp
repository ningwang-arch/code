#include "spider.h"

Spider::Spider()
    : m_from(username) {
    curl_global_init(CURL_GLOBAL_ALL);
    m_curl = curl_easy_init();
    if (!m_curl) exit(-1);
    m_headers = nullptr;
    builder.settings_["emitUTF8"] = true;
    m_mailFormatter.parse(mail_template);
    init();
    // std::cout << default_data << std::endl;
}

void Spider::handle(UserInfo info) {
    Json::Value data = fixtemplate(info.data);

    int rt = checkBind(info.sn, info.idcard);
    if (rt != -1) {
        if (rt == 0) { bindUserInfo(info.sn, info.idcard); }

        // rt = isNeedCard();
        // if (rt == 1)
        //     std::cout << "已完成打卡: " << respData << std::endl;
        // else if (rt == 0) {

        monitorRegister(data);
        std::stringstream ss;
        // strToJson(, info.data);
        ss << "打卡信息: " << Json::writeString(builder, data) << std::endl;
        // resp_data = resp_data.erase(0, 2);
        // resp_data.pop_back();
        Json::Value root;
        strToJson(respData, root);
        root["data"] = base64_decode(root.get("data", "").asString());
        ss << "打卡结果: " << Json::writeString(builder, root) << std::endl;
        // std::cout << ss.str() << std::endl;
        sendEmail(info.mail, ss.str());
        // }
        cancelBind();
    }
}

Spider::~Spider() {
    curl_slist_free_all(m_headers);
    curl_easy_cleanup(m_curl);
    curl_global_cleanup();
}


void Spider::init() {
    curl_easy_setopt(m_curl, CURLOPT_WRITEFUNCTION, getData);
    curl_easy_setopt(m_curl, CURLOPT_WRITEDATA, &respData);

    curl_easy_setopt(m_curl, CURLOPT_VERBOSE, 1);
    for (auto& i : list_headers) { m_headers = curl_slist_append(m_headers, i.c_str()); }

    if (m_headers != NULL) { curl_easy_setopt(m_curl, CURLOPT_HTTPHEADER, m_headers); }
}

size_t payload_source(char* ptr, size_t size, size_t nmemb, void* userp) {
    struct upload_status* upload_ctx = (struct upload_status*)userp;
    const char* data;
    size_t room = size * nmemb;

    if ((size == 0) || (nmemb == 0) || ((size * nmemb) < 1)) { return 0; }

    data = &mailContent[upload_ctx->bytes_read];

    if (data) {
        size_t len = strlen(data);
        if (room < len) len = room;
        memcpy(ptr, data, len);
        upload_ctx->bytes_read += len;

        return len;
    }

    return 0;
}

bool Spider::strToJson(const std::string& body, Json::Value& root) {
    root.clear();
    Json::CharReaderBuilder builder;
    Json::CharReader* reader = builder.newCharReader();

    std::string errors;

    bool parsingSuccessful =
        reader->parse(body.c_str(), body.c_str() + body.size(), &root, &errors);
    delete reader;

    if (!parsingSuccessful) {
        std::cout << "Failed to parse the JSON, errors:" << std::endl;
        std::cout << errors << std::endl;
        return false;
    }
    return true;
}

// std::string Spider::base64_encode(const std::string& in) {
//     std::string out;

//     int val = 0, valb = -6;
//     for (auto c : in) {
//         val = (val << 8) + c;
//         valb += 8;
//         while (valb >= 0) {
//             out.push_back(
//                 "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"[(val >> valb)
//                 &
//                                                                                    0x3F]);
//             valb -= 6;
//         }
//     }
//     if (valb > -6)
//         out.push_back("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
//                           [((val << 8) >> (valb + 8)) & 0x3F]);
//     while (out.size() % 4) out.push_back('=');
//     return out;
// }
// std::string Spider::base64_decode(const std::string& in) {
//     std::string out;

//     std::vector<int> T(256, -1);
//     for (int i = 0; i < 64; i++)
//         T["ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"[i]] = i;

//     int val = 0, valb = -8;
//     for (auto c : in) {
//         if (T[c] == -1) break;
//         val = (val << 6) + T[c];
//         valb += 6;
//         if (valb >= 0) {
//             out.push_back(char((val >> valb) & 0xFF));
//             valb -= 8;
//         }
//     }
//     return out;
// }
size_t getData(char* ptr, size_t size, size_t num, std::string* stream) {
    if (stream == NULL) return 0;
    stream->append(ptr, size * num);
    return size * num;
}


int Spider::checkBind(const std::string& sn, const std::string& idCard) {
    respData.clear();
    curl_easy_setopt(m_curl, CURLOPT_URL, (base_url + chaeckBind_url).c_str());


    curl_easy_setopt(m_curl, CURLOPT_POST, 1);
    Json::Value json = default_data["loginInfo"];
    json["sn"] = sn;
    json["idCard"] = idCard;
    std::string encode_data = base64_encode(Json::writeString(builder, json));
    curl_easy_setopt(m_curl, CURLOPT_POSTFIELDS, encode_data.c_str());
    CURLcode res = curl_easy_perform(m_curl);
    if (strToJson(respData, json)) {
        int status = json.get("status", 0).asInt();
        std::string data = json.get("data", "").asString();
        Json::Value value;
        strToJson(base64_decode(data), value);
        json["data"] = value;
        if (status == 0) { return -1; }
        else {
            std::string cookie = "Cookie: JSESSIONID=" + value.get("sessionId", "").asString();
            curl_slist_append(m_headers, cookie.c_str());
            curl_easy_setopt(m_curl, CURLOPT_HTTPHEADER, m_headers);
            int bind = value.get("bind", 0).asInt();
            if (bind == 0) { return 0; }
            else {
                return 1;
            }
        }
    }
    return -1;
}

int Spider::bindUserInfo(const std::string& sn, const std::string& idCard) {
    respData.clear();
    curl_easy_setopt(m_curl, CURLOPT_POST, 1);
    curl_easy_setopt(m_curl, CURLOPT_URL, (base_url + bindUserInfo_url).c_str());
    Json::Value json = default_data["loginInfo"];
    json["sn"] = sn;
    json["idCard"] = idCard;
    std::string encode_data = base64_encode(Json::writeString(builder, json));
    curl_easy_setopt(m_curl, CURLOPT_POSTFIELDS, encode_data.c_str());
    CURLcode res = curl_easy_perform(m_curl);
    return 0;
}

int Spider::cancelBind() {
    respData.clear();
    curl_easy_setopt(m_curl, CURLOPT_POST, 1);
    curl_easy_setopt(m_curl, CURLOPT_URL, (base_url + cancelBind_url).c_str());
    curl_easy_setopt(m_curl, CURLOPT_POSTFIELDS, "");
    CURLcode res = curl_easy_perform(m_curl);

    return 0;
}

int Spider::isNeedCard() {
    respData.clear();
    curl_easy_setopt(m_curl, CURLOPT_POST, 0);
    curl_easy_setopt(m_curl, CURLOPT_URL, (base_url + isNeedCard_url).c_str());
    CURLcode res = curl_easy_perform(m_curl);

    Json::Value root;
    if (strToJson(respData, root)) {
        int status = root.get("status", 0).asInt();
        return status;
    }
    else {
        std::cout << "parse error" << std::endl;
        return -1;
    }

    return 0;
}

void Spider::sendEmail(const std::string& to, const std::string& msg) {
if(to.empty()) return;    
CURLcode res = CURLE_OK;
    struct curl_slist* recipients = NULL;
    struct upload_status upload_ctx = {0};

    mailContent = (m_mailFormatter % to % m_from % to % msg).str();

    if (m_curl) {
        curl_easy_setopt(m_curl, CURLOPT_USERNAME, username.c_str());
        curl_easy_setopt(m_curl, CURLOPT_PASSWORD, passwd.c_str());
        curl_easy_setopt(m_curl, CURLOPT_URL, server.c_str());
        curl_easy_setopt(m_curl, CURLOPT_MAIL_FROM, m_from.c_str());
        curl_easy_setopt(m_curl, CURLOPT_LOGIN_OPTIONS, "AUTH=LOGIN");
        recipients = curl_slist_append(recipients, to.c_str());
        recipients = curl_slist_append(recipients, to.c_str());
        curl_easy_setopt(m_curl, CURLOPT_MAIL_RCPT, recipients);
        curl_easy_setopt(m_curl, CURLOPT_READFUNCTION, payload_source);
        curl_easy_setopt(m_curl, CURLOPT_READDATA, &upload_ctx);
        curl_easy_setopt(m_curl, CURLOPT_UPLOAD, 1L);
        // curl_easy_setopt(m_curl, CURLOPT_VERBOSE, 1L);
        res = curl_easy_perform(m_curl);

        if (res != CURLE_OK)
            fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));

        curl_slist_free_all(recipients);
    }
}

int Spider::monitorRegister(Json::Value data) {
    curl_easy_setopt(m_curl, CURLOPT_POST, 1);
    curl_easy_setopt(m_curl, CURLOPT_URL, (base_url + monitorRegister_url).c_str());


    std::string e_data = base64_encode(Json::writeString(builder, data));
    curl_easy_setopt(m_curl, CURLOPT_POSTFIELDS, e_data.c_str());
    // TODO resend when error
    int status = 1;
    int cnt=0;
    do{    
        respData.clear();
        CURLcode res = curl_easy_perform(m_curl);
        Json::Value root;
        strToJson(respData,root);
        status = root.get("status",0).asInt();
        cnt++;
        if(cnt>=10){break;}
    }while(!status);
    return 0;
}


Json::Value Spider::fixtemplate(Json::Value data) {
    Json::Value root = default_data["monitorRegister"];
    Json::Value::Members members;
    members = data.getMemberNames();
    for (auto item : members) { root[item] = data[item]; }
    return root;
}

Config::Config(std::string filename) {
    Json::Value root;
    Json::Reader reader;
    std::ifstream ifs(filename, std::ios::binary);
    if (!ifs) { exit(-1); }
    if (reader.parse(ifs, root)) {

        Json::Value sender = root["sender"];
	    server = root.get("smtp_server","").asString();
        username = sender.get("username","").asString();
        passwd = sender.get("passwd","").asString();

        default_data = root["default_data"];
        Json::Value users = root["users"];

        for (auto item : users) {
            UserInfo ui = {.sn = item.get("sn", "").asString(),
                           .idcard = item.get("idCard", "").asString(),
                           .mail = item.get("mail", "").asString(),
                           .data = item["data"]};
            m_infos.push_back(ui);
        }
    }
}

Config::~Config(){
    if(!m_infos.empty()){
        m_infos.clear();
    }
}
