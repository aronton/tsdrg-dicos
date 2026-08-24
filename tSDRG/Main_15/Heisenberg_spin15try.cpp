#include <iostream>
#include <fstream>
#include <sstream>
#include <random>
#include <iomanip>
#include <cmath>
#include <chrono>
#include <ctime>
#include <algorithm>
#include <uni10.hpp>
#include "../MPO/mpo.h"
#include "../tSDRG_tools/tSDRG_tools.h"
#include "../tSDRG_tools/measure.h"
#include <vector>
#include <string>
#include <utility>
#include <fcntl.h>      // open()
#include <unistd.h>     // close()
#include <sys/file.h>   // flock()
#include <errno.h>
#include <unordered_map>
#include <sys/stat.h>

using namespace std;

const string dicos_path = "/ceph/work/NTHU-qubit/LYT/tSDRG_random/tSDRG/Main_15";
const string tSDRG_path = "/home/aronton/tSDRG_random//tSDRG/Main_15";

string group_path;
string my_path;


bool dir_exists(const std::string &path) {
    struct stat info;
    if (stat(path.c_str(), &info) != 0) {
        return false; // 無法取得資訊 → 不存在
    }
    return (info.st_mode & S_IFDIR) != 0; // 確認是資料夾
}



void setPath()
{
    if(dir_exists(dicos_path))
    {
        group_path = dicos_path;
        my_path = dicos_path;
    }

    if(dir_exists(tSDRG_path))
    {
        group_path = tSDRG_path;
        my_path = tSDRG_path;
    }
}

string get_first_five_lines(const string& raw) {
    istringstream iss(raw);
    string line;
    vector<string> lines;
    int count = 0;
    
    while (getline(iss, line) && count < 5) {
        lines.push_back(line);
        count++;
    }

    // 合併成一個字串
    string result;
    for (const auto& l : lines) {
        result += l + ",";
    }
    return result;
}

std::string get_first_100_chars(const std::string& raw) {
    return raw.substr(0, 100);
}

bool safe_file_access(const std::string& filename, const std::string& mode, const std::string& message = "") {
    int flags = (mode == "r") ? O_RDONLY : O_WRONLY | O_CREAT | O_APPEND;
    int fd = open(filename.c_str(), flags, 0644);
    if (fd == -1) {
        std::cerr << "Failed to open file: " << strerror(errno) << "\n";
        return false;
    }

    // Apply exclusive lock
    if (flock(fd, LOCK_EX) == -1) {
        std::cerr << "Failed to acquire lock: " << strerror(errno) << "\n";
        close(fd);
        return false;
    }

    if (mode == "w") {
        // 寫入模式
        FILE* fp = fdopen(fd, "a");
        if (!fp) {
            std::cerr << "Failed to open FILE stream: " << strerror(errno) << "\n";
            flock(fd, LOCK_UN);
            close(fd);
            return false;
        }
        fprintf(fp, "%s\n", message.c_str());
        fflush(fp);
        fclose(fp);  // 也會關閉 fd
    } else {
        // 讀取模式
        char buffer[1024];
        ssize_t bytes = read(fd, buffer, sizeof(buffer) - 1);
        if (bytes >= 0) {
            buffer[bytes] = '\0';
            std::cout << "[Read] " << buffer << "\n";
        } else {
            std::cerr << "Failed to read: " << strerror(errno) << "\n";
        }
        close(fd);
    }

    // 解鎖（實際上 fclose 也會解，但這裡保險一點）
    // 不需要額外 unlock，fclose/close 會自動解
    return true;
}


struct paralist {
    double spin;
    double J;
    double D;
    int L;
    string Jstr;
    string Dstr;
    string Lstr;
    int Pdis;
    string BC;
    int chi;
    int sample;
    string check;
    vector<double> J_list;
    double dimerization;
    std::unordered_map<std::string, std::string> path;
};

struct datalist {
    double ZL;
    double ZLI;
    double ZLC;
    double SOP;
    long long seed;
    string w_loc;
    string corr1;
    string corr2;
    string message;
    int L;
    vector<vector<double>> corrV1;
    vector<vector<double>> corrV2;
    vector<double> J_list;
    vector<double> energy;
    std::chrono::duration<double> treeTime;
    std::chrono::duration<double> corrTime;
    std::chrono::duration<double> zlTime;
    

    datalist(int L_) : L(L_), corrV1(L_, vector<double>(L_)), corrV2(L_, vector<double>(L_)) {};

};

void writeDatalistToFile(const datalist& data, const std::string& filename) {
    std::ofstream outFile(filename);
    if (!outFile) {
        std::cerr << "無法開啟檔案: " << filename << std::endl;
        return;
    }

    outFile << "ZL: " << data.ZL << std::endl;
    outFile << "ZLI: " << data.ZLI << std::endl;
    outFile << "ZLC: " << data.ZLC << std::endl;
    outFile << "SOP: " << data.SOP << std::endl;
    outFile << "Seed: " << data.seed << std::endl;
    outFile << "w_loc: " << data.w_loc << std::endl;
    outFile << "corr1: " << data.corr1 << std::endl;
    outFile << "corr2: " << data.corr2 << std::endl;

    outFile << "J_list:";
    for (const auto& j : data.J_list) {
        outFile << ' ' << j;
    }
    outFile << std::endl;

    outFile << "Energy:";
    for (const auto& e : data.energy) {
        outFile << ' ' << e;
    }
    outFile << std::endl;

    outFile << "Message: " << data.message << std::endl;

    outFile.close();
}

void createPath(paralist& para, datalist& data)
{
    std::string file_name = para.Lstr + "_P" + to_string(para.Pdis) + "_m" + to_string(para.chi) + "_" + to_string(para.sample);
    std::string base_path = group_path + "/data_random/" + para.BC + "/" + para.Jstr + "/" + para.Dstr + "/" + file_name + "/";

    para.path["dir"] = base_path;
    para.path["ZL"] = base_path + file_name + "_ZL.txt";
    para.path["string"] = base_path + file_name + "_string.txt";
    para.path["corr1"] = base_path + file_name + "_corr1.txt";
    para.path["corr2"] = base_path + file_name + "_corr2.txt";
    para.path["w_loc"] = base_path + file_name + "_w_loc.txt";
    para.path["energy"] = base_path + file_name + "_energy.txt";
    para.path["J_list"] = base_path + file_name + "_J_list.txt";
    para.path["seed"] = base_path + file_name + "_seed.txt";
    para.path["dimerization"] = base_path + file_name + "_dimerization.txt";

    return;
}


// bool seedcheck(paralist& para, datalist& data)
// {
//     string path = group_path + "/data_random" + "/" + para.BC + "/"

//     return;
// }

void parameterRead(string filename, vector<pair<string, string>>& parameter) {
    ifstream file(filename);
    if (!file) {
        cerr << "無法開啟檔案: " << filename << endl;
        return;
    }

    string line;
    while (getline(file, line)) { // 逐行讀取
        // cout << "讀取到: " << line << endl; // 除錯用，確認讀取內容

        istringstream iss(line);
        string key, value_str;

        if (getline(iss, key, ':') && getline(iss, value_str)) {
            // cout << "解析後: " << key << " -> " << value_str << endl; // 確認解析是否成功
            parameter.push_back(make_pair(key, value_str));
        }
    }

    file.close();
}

void bulk_corr(paralist& para, datalist& data, vector<uni10::UniTensor<double> >& w_up, vector<uni10::UniTensor<double> >& w_down, vector<int>& w_loc)
{
    /// bulk correlation and string order parameter print
    double corr, corr1 ,corr2;
    vector<double> corr12;
    for (int i = 0; i < para.J_list.size(); i++)
    {
        corr12.push_back(Correlation_St(i, w_up, w_down, w_loc) );
    }
    string file;
    file = para.path["corr1"];
    ofstream fout1(file);
    file = para.path["corr2"];
    ofstream fout2(file);
    // file = para.path["string"]
    // ofstream foutS(file);
    // ofstream fout1(file_name1);
    // ofstream fout2(file_name2);
    // ofstream foutS(file_nameS);
    fout1 << "x1,x2,corr" << endl;
    fout2 << "x1,x2,corr" << endl;
    int site1;
    int site2;
    int r;
    /// TODO: for OBC. Now is good for PBC.
    for (site1 = 0; site1 < para.L; site1 += 1)
    {

        for (site2 = 0; site2 < para.L; site2 += 1)
        {
            r = site2 - site1;
            //cout << r << endl;
            if (r == para.L/2)
            {
                corr = Correlation_StSt(site1, site2, w_up, w_down, w_loc);
                corr1 = corr12[site1];
                corr2 = corr12[site2];
                data.corr1 += (to_string(site1) + "," + to_string(site2) + "," + to_string(corr) + ";");
                data.corr2 += (to_string(site1) + "," + to_string(site2) + "," + to_string(corr - corr1*corr2)+ ";");
                fout1 << setprecision(16) << site1 << "," << site2 << "," << corr << endl;
                fout2 << setprecision(16) << site1 << "," << site2 << "," << corr - corr1*corr2 << endl;
            }
        }
    }
    fout1.flush();
    fout2.flush();
    // foutS.flush();
    fout1.close();
    fout2.close();
    // foutS.close();
}

void SOP(paralist& para, datalist& data, vector<uni10::UniTensor<double> >& w_up, vector<uni10::UniTensor<double> >& w_down, vector<int>& w_loc)
{
    /// bulk correlation and string order parameter print
    double corr, corr1 ,corr2;

    string file;
    file = para.path["string"];
    ofstream foutS(file);

    // ofstream foutS(file_nameS);

    foutS << "x1,x2,corr" << endl;
    int site1;
    int site2;
    int r;
    /// TODO: for OBC. Now is good for PBC.
    for (site1 = 0; site1 < para.L; site1 += 1)
    {

        for (site2 = 0; site2 < para.L; site2 += 1)
        {
            r = site2 - site1;
            //cout << r << endl;
            if (r == para.L/2)
            {
                data.SOP = Correlation_String(site1, site2, w_up, w_down, w_loc);
                foutS << setprecision(16) << site1 << "," << site2 << "," << data.SOP << endl;

            }
        }
    }

    foutS.flush();
    foutS.close();
}

void etoe_corr(paralist& para, datalist& data, const vector<uni10::UniTensor<double> >& w_up, const vector<uni10::UniTensor<double> >& w_down, const vector<int>& w_loc)
{
    /// bulk correlation and string order parameter print
    double corr, corr1 ,corr2;
    vector<double> corr12;
    for (int i = 0; i < para.J_list.size(); i++)
    {
        corr12.push_back(Correlation_St(i, w_up, w_down, w_loc) );
    }
    string file;
    file = para.path["corr1"];
    ofstream fout1(file);
    file = para.path["corr2"];
    ofstream fout2(file);
    // file = para.path["string"]
    // ofstream foutS(file);
    // ofstream fout1(file_name1);
    // ofstream fout2(file_name2);
    // ofstream foutS(file_nameS);
    fout1 << "x1,x2,corr" << endl;
    fout2 << "x1,x2,corr" << endl;
    // for(int i = 0; i <= para.L-1; i++)
    // {
    //     for(int j = 0; j <= para.L-1; j++)
    //     {
    //         corr = Correlation_StSt(i, j, w_up, w_down, w_loc);
    //         corr1 = corr12[i];
    //         corr2 = corr12[j];
    //         data.corrV2[i][j] = corr - corr1[i]*corr1[j];
    //         data.corrV1[i][j] = corr;
    //     }        
    // }

    for(int i = para.L - 4; i <= para.L-1; i++)
    {

        int site1 = 0;
        int site2 = i;
        if(site2>site1)
        {
            corr = Correlation_StSt(site1, site2, w_up, w_down, w_loc);
            corr1 = corr12[site1];
            corr2 = corr12[site2];
            data.corr1 += (to_string(site1) + "," + to_string(site2) + "," + to_string(corr) + ";");
            data.corr2 += (to_string(site1) + "," + to_string(site2) + "," + to_string(corr - corr1*corr2)+ ";");
            fout1 << setprecision(16) << site1 << "," << site2 << "," << corr << endl;
            fout2 << setprecision(16) << site1 << "," << site2 << "," << corr - corr1*corr2 << endl;
            // fout1.flush();
            // fout2.flush();
            // // foutS.flush();
            // fout1.close();
            // fout2.close();
            // foutS.close();
        }
    }

    // for(int i = 0; i <= para.L-1; i++)
    // {
    //     for(int j = 0; j <= para.L-1; j++)
    //     {
    //         int site1 = i;
    //         int site2 = j;
    //         if(site2>site1)
    //         {
    //             corr = Correlation_StSt(site1, site2, w_up, w_down, w_loc);
    //             corr1 = corr12[site1];
    //             corr2 = corr12[site2];
    //             data.corr1 += (to_string(site1) + "," + to_string(site2) + "," + to_string(corr) + ";");
    //             data.corr2 += (to_string(site1) + "," + to_string(site2) + "," + to_string(corr - corr1*corr2)+ ";");
    //             fout1 << setprecision(16) << site1 << "," << site2 << "," << corr << endl;
    //             fout2 << setprecision(16) << site1 << "," << site2 << "," << corr - corr1*corr2 << endl;
    //             // fout1.flush();
    //             // fout2.flush();
    //             // // foutS.flush();
    //             // fout1.close();
    //             // fout2.close();
    //             // foutS.close();
    //         }
    //     }        
    // }
    fout1.flush();
    fout2.flush();
    // foutS.flush();
    fout1.close();
    fout2.close();
    // int site1 = 0;
    // int site2 = para.L-1;

    // corr = Correlation_StSt(site1, site2, w_up, w_down, w_loc);
    // corr1 = corr12[site1];
    // corr2 = corr12[site2];
    // data.corr1 += (to_string(site1) + "," + to_string(site2) + "," + to_string(corr) + ";");
    // data.corr2 += (to_string(site1) + "," + to_string(site2) + "," + to_string(corr - corr1*corr2)+ ";");
    // fout1 << setprecision(16) << site1 << "," << site2 << "," << corr << endl;
    // fout2 << setprecision(16) << site1 << "," << site2 << "," << corr - corr1*corr2 << endl;
    // fout1.flush();
    // fout2.flush();
    // // foutS.flush();
    // fout1.close();
    // fout2.close();
    // // foutS.close();
}



double sum(vector<double> &J_list, int oddness)
{
    double sum = 0;
    int L = J_list.size();
    for (int i = 0; i < L; i++)
    {
        if(i%2==oddness)
            sum += J_list[i];
    }

    return sum;
}

void Jlist(paralist& para, datalist& data)
{
    random_device rd;             // non-deterministic generator.
    long long seed = rd();
    // long long seed = para.sample;
    data.seed = seed;
    mt19937 genRandom(seed);    // use mersenne twister and seed is rd.
    // mt19937 genFixed(Jseed);     // use mersenne twister and seed is fixed!

    uniform_real_distribution<double> uniform_dis(nextafter(0.0, 1.0), 1.0); // probability distribution of J rand(0^+ ~ 1)

    normal_distribution<double> normal_dis(0,1.0); 
    // if(Pdis==10)
    //     cout << "J_i=(1+d*(-1)^i)eta_i^R" << endl;
    // if(Pdis==20)
    //     cout << "J_i=(1+d*(-1)^i)exp(eta_i*R)" << endl;
    if(para.BC == "PBC")
    {
        for(int i=0; i<para.L; i++)
        {
            double jvar;
            if(para.Pdis==10)
                jvar = uniform_dis(genRandom);
            if(para.Pdis==20)
                jvar = normal_dis(genRandom);
            // double jvar = normal_dis(genRandom);
            jvar = (1 + para.D * pow(-1,i+1)) * Distribution_Random_Variable(para.Pdis, jvar, para.J);
            // cout << jvar << "\n";
            para.J_list[i] = jvar;
        }
    }
    else
    {
        for(int i=0; i<para.L-1; i++)
        {
            double jvar;
            if(para.Pdis==10)
                jvar = uniform_dis(genRandom);
            if(para.Pdis==20)
                jvar = normal_dis(genRandom);
            // double jvar = normal_dis(genRandom);
            jvar = (1 + para.D * pow(-1,i+1)) * Distribution_Random_Variable(para.Pdis, jvar, para.J);
            // cout << jvar << "\n";
            para.J_list[i] = jvar;
        }
    }
    para.dimerization = abs(abs(sum(para.J_list,0)) - abs(sum(para.J_list,1)))/(abs(sum(para.J_list,0)) + abs(sum(para.J_list,1)));
}

void parameterSet(paralist& plist, datalist& data, const vector<pair<string, string>>& parameter) {
    if (parameter.empty()) {
        cerr << "[ERROR] parameter list is empty!" << endl;
        return;
    }
    std::ostringstream oss;
    for (size_t i = 0; i < parameter.size(); ++i) {
        const string& para = parameter[i].first;
        const string& value = parameter[i].second;

        data.message += ("[DEBUG] parameter[i] = (para, value)\n");

        try {
            if (para == "L") {
                plist.L = stoi(value);
                plist.Lstr = "L" + to_string(plist.L);
            }
            else if (para == "chi") {
                plist.chi = stoi(value);
            }
            else if (para == "BC") {
                plist.BC = value;
            }
            else if (para == "Pdis") {
                plist.Pdis = stoi(value);
            }
            else if (para == "J") {
                plist.J = stod(value);
                ostringstream oss;
                oss << fixed << setprecision(2) << plist.J;
                string str = oss.str();
                str.erase(remove(str.begin(), str.end(), '.'), str.end());
                plist.Jstr = "Jdis" + str;
            }
            else if (para == "D") {
                plist.D = stod(value);
                ostringstream oss;
                oss << fixed << setprecision(2) << plist.D;
                string str = oss.str();
                str.erase(remove(str.begin(), str.end(), '.'), str.end());
                plist.Dstr = "Dim" + str;
            }
            else {
                oss << "[WARNING] Unknown parameter: " << para << endl;
                data.message += oss.str();
            }
        } catch (const exception& e) {
            cerr << "[ERROR] Failed to parse (" << para << ", " << value << "): " << e.what() << endl;
        }
    }
}



void tSDRG_XXZ1(paralist& para, datalist& data)
{

    int sample = para.sample;  
    int L = para.L;                      // system size
    int chi = para.chi;                    // keep state of isometry
    string BC = para.BC;                  // boundary condition
    int Pdis = para.Pdis;                   // model of random variable disturbution
    double J = para.J;                // J-coupling disorder strength
    double D = para.D; 			        // Dimerization constant
    double S = para.spin;        // spin dimension
    std::ostringstream oss;
    
    oss << "\n------------------------------sample: " << sample << "------------------------------\n";
    
    data.message = oss.str();

    if(BC == "PBC")
    {
        for(int i = 0; i<L;i++)
        {
            para.J_list.push_back(0);
        }
    }
    else
    {
        for(int i = 0; i<L-1;i++)
        {
            para.J_list.push_back(0);
        }
    }

    

    Jlist(para,data);
    
    string str = "mkdir -p " + para.path["dir"];
    const char *mkdir = str.c_str();
    const int dir_err = system(mkdir);
    if (dir_err == -1)
    {
        cout << "Error creating directory!" << endl;
        exit(1);
    }

    
    // s_tempt = abs(abs(sum(para.J_list,0)) - abs(sum(para.J_list,1)))/(abs(sum(para.J_list,0)) + abs(sum(para.J_list,1)));
    // long long seed = data.seed;    
    // para.dimerization = s_tempt;

    ofstream fout(para.path["seed"]);
    if (!fout)
    {
        ostringstream err;
        err << "Error: Fail to save (maybe need mkdir " << para.path["seed"] << ")";
        throw runtime_error(err.str());
    }
    fout << "seed" << endl;
    fout << setprecision(16) << data.seed << endl;
    fout.flush();
    fout.close();

    data.message += ("seed:" + to_string(data.seed) + "\n");

    fout.open(para.path["J_list"]);
    if (!fout)
    {
        ostringstream err;
        err << "Error: Fail to save (maybe need mkdir " << para.path["J_list"] << ")";
        throw runtime_error(err.str());
    }
    fout << "J_list" << endl;
    for (int i=0; i<para.J_list.size(); i++)
    {
        fout << setprecision(16) << para.J_list[i] << endl;
    }
    fout.flush();
    fout.close(); 

    data.message += ("Jlist : " + to_string(para.J_list[0]) + ", " + to_string(para.J_list[1]) + ", " + to_string(para.J_list[2]) \
    + ", " + to_string(para.J_list[3]) + ", " + to_string(para.J_list[4]) \
    + "..." + to_string(para.J_list[-2]) + "," + to_string(para.J_list[-1]) + "\n");

    fout.open(para.path["dimerization"]);
    if (!fout)
    {
        ostringstream err;
        err << "Error: Fail to save (maybe need mkdir " << para.path["dimerization"] << ")";
        throw runtime_error(err.str());
    }
    fout << "dimerization" << endl;
    fout << setprecision(16) << para.dimerization << endl;
    fout.flush();
    fout.close();

    data.message += ("dimerization:" + to_string(para.dimerization) + "\n");
    
    // /// STEP.1: Decompose the Hamiltonian into MPO blocks
    vector<MPO> MPO_chain;
    MPO_chain = generate_MPO_chain(L, "XXZ_" + BC, S, para.J_list, 1.0, 0);
    

    vector<uni10::UniTensor<double> > w_up;      // w_up is isometry tensor = VT
    vector<int> w_loc;    
    // vector<double> rgJlist = data.rgJlist;
    // vector<double> En = data.energy;                 // J_list will earse to one, and return ground energy.
    for(int i = 0; i<para.J_list.size();i++)
    {
        data.J_list.push_back(para.J_list[i]);
    }
    bool info = 1;                               // True; if tSDRG can not find non-zero gap, info return 0, and stop this random seed.
    bool save_RG_info = 0;                       // save gaps at RG stage 
    // cout << data.message;

    /*tSDRG*/

    auto start = std::chrono::steady_clock::now();

    tSDRG(MPO_chain, data.J_list, data.energy, w_up, w_loc, chi, to_string(J), Pdis, sample, save_RG_info, info);

    auto end = std::chrono::steady_clock::now();


    data.treeTime = end - start;

    /// check info if can not RG_J
    fout.open(para.path["die"]);
    if (info == 0)
    {
        fout << "dead seed" << endl;
        fout << data.seed << endl;
        fout.flush();
        fout.close();
        cout << "random seed " + to_string(data.seed)  + " died (can not find non-zero gap) " << endl;
        return;
    }
    else
    {   
        data.message += ("\nfinish in " + para.path["dir"] + "\n");
    }
     data.message += ("tree_time: " + to_string(data.treeTime.count()) + " seconds\n");

    /*energy save*/
    fout.open(para.path["energy"]);
    if (!fout)
    {
        ostringstream err;
        err << "Error: Fail to save (maybe need mkdir " << para.path["energy"] << ")";
        throw runtime_error(err.str());
    }
    fout << "energy" << endl;
    for (int i=0; i<data.energy.size(); i++)
    {
        fout << setprecision(16) << data.energy[i] << endl;
    }
    fout.flush();
    fout.close(); 


    /*w_loc*/
    fout.open(para.path["w_loc"]);
    if (!fout)
    {
        ostringstream err;
        err << "Error: Fail to save (maybe need mkdir " << para.path["w_loc"] << ")";
        throw runtime_error(err.str());
    }
    fout << "w_loc" << endl;
    for (int i=0; i<w_loc.size(); i++)
    {
        fout << setprecision(16) << w_loc[i] << endl;
    }
    fout.flush();
    fout.close(); 

    data.message += ("energy : " + to_string(data.energy[0]) + ", " + to_string(data.energy[1]) + ", " + to_string(data.energy[2]) \
    + ", " + to_string(data.energy[3]) + ", " + to_string(data.energy[4])\
    + "..." + to_string(data.energy[-2]) + "," + to_string(data.energy[-1]) + "\n");

    //string top1 = Decision_tree(w_loc, true);

    /*create isometry of other part to calculate physical quantity*/
    vector<uni10::UniTensor<double> > w_down;    // w_down
    uni10::UniTensor<double> kara;
    w_down.assign(L-1, kara);
    for (int i = 0; i < w_up.size(); i++)
    {
        w_down[i] = w_up[i];
        uni10::Permute(w_down[i], {-3, -1, 1}, 2, uni10::INPLACE);
    }

    /*Correlation calculation ( include OBC and PBC )*/

    start = std::chrono::steady_clock::now();

    if(para.BC == "PBC")
    {
        bulk_corr(para, data, w_up, w_down, w_loc);
        SOP(para, data, w_up, w_down, w_loc);
        data.message += "bulk_corr:" + get_first_100_chars(data.corr1) + "\n";
    }
    else
    {
        etoe_corr(para, data, w_up, w_down, w_loc);
        data.message += "etoe_corr:" + get_first_100_chars(data.corr1) + "\n";
    }

    end = std::chrono::steady_clock::now();


    data.corrTime = end - start;

    data.message += ("correlation_time: " + to_string(data.corrTime.count()) + " seconds\n");

    /*ZL calculation*/

    start = std::chrono::steady_clock::now();

    fout.open(para.path["ZL"]);    
    if (!fout)
    {
        ostringstream err;
        err << "Error: Fail to save (maybe need mkdir " << para.path["ZL"] << ")";
        throw runtime_error(err.str());
    }

    end = std::chrono::steady_clock::now();

    data.zlTime = end - start;

    fout << "ZL" << endl;
    double ZL = Correlation_ZL(w_up, w_down, w_loc);
    data.ZL = ZL;
    fout << setprecision(16) << data.ZL << endl;
    fout.flush();
    fout.close();
    data.message += ("ZL:" + to_string(data.ZL) + "\n"); 
    data.message += ("ZL_time: " + to_string(data.zlTime.count()) + " seconds\n");
    /*messenage out*/

    cout << data.message + "\n\n";
}


void errMsg(char *arg) 
{
    cerr << "Usage: " << arg << " [options]" << endl;
    cerr << "Need 9-parameter:" << endl;
    cerr << "./job.exe <system size> <keep state of RG procedure> <Prob distribution> <disorder> <dimerization> <algo> <seed1> <seed2>\n" << endl;
    cerr << "Example:" << endl;
    cerr << "./job.exe 32 8 10 0.1 0.1 PBC 1 1\n" << endl;
}

int main(int argc, char *argv[])
{
    int L;                      // system size
    int chi;                    // keep state of isometry
    string BC;                  // boundary condition
    int Pdis;                   // model of random variable disturbution
    double Jdis;                // J-coupling disorder strength
    double Dim;			        // Dimerization constant
    int seed1;                  // random seed number in order to repeat data
    int seed2;                  // random seed number in order to repeat data
    double S      = 1.5;        // spin dimension
    double Jz     = 1.0;        // XXZ model
    double h      = 0.0;        // XXZ model
    string filePath;
    stringstream(argv[1]) >> filePath;

    // for(int i=0; i < parameter.size(); i++)
    // {
    //     cout << parameter[i].first << ", " << parameter[i].second << "\n";
    // }
    // cout << parameter[0].second;
    // cout << filePath <<endl;
    seed1 = stoi(argv[2]);
    seed2 = stoi(argv[3]);

    // struct datalist {
    //     double ZL;
    //     double ZLI;
    //     double ZLC;
    //     double SOP;
    //     long long seed;
    //     string w_loc;
    //     string corr1;
    //     string corr2;
    //     vector<double> J_list;
    //     vector<double> energy;
    //     string  message;
    // };
    // plist.s1 = seed1;
    // plist.s2 = seed2;
    // std::cout << "seed1:" << seed1 << std::endl;
    // std::cout << "seed2:" << seed2 << std::endl;
    // cout << plist.spin << "_" << plist.L << "_" << plist.J << "_" << plist.D; 
    for (int i = seed1; i <= seed2; i++) 
    {
    
        // datalist dlist = {0,0,0,0,0,"","","",{},{},""};
        datalist dlist(L);
        paralist plist = {};
        // plist.spin = S;
        // ofstream fin(filePath); 
        vector<pair<string, string>> parameter;
        // std::cout << "seed1:" << seed1 << std::endl;
        // std::cout << "seed2:" << seed2 << std::endl;
        parameterRead(filePath, parameter);
        // cout << filePath << "\n";
        // std::cout << "seed1:" << seed1 << std::endl;
        // std::cout << "seed2:" << seed2 << std::endl;
        parameterSet(plist, dlist, parameter);
        plist.sample = i;
        // std::cout << "seed1:" << seed1 << std::endl;
        // std::cout << "seed2:" << seed2 << std::endl;
        plist.spin = S;
        // std::cout << "seed1:" << seed1 << std::endl;
        // std::cout << "seed2:" << seed2 << std::endl;
        // cout << "plist.sample:" <<plist.sample;
        setPath();
        createPath(plist, dlist);
        // if (plist.path.find("ZL") != plist.path.end()) {
        //     const string& path_to_file = plist.path["ZL"];
        //     ifstream file(path_to_file);
        //     if (file.good()) {
        //         cout << "ZL exists at path: " << path_to_file << endl;
        //         return 0;
        //     }
        // }
        if (plist.path.find("ZL") != plist.path.end()) {
            const string& path_to_file = plist.path["ZL"];

            struct stat st;
            if (stat(path_to_file.c_str(), &st) == 0) {   // 檔案存在
                if (st.st_size == 0) {
                    cout << "ZL exists but is empty: " << path_to_file << endl;
                    // 不 return，繼續執行
                } else {
                    cout << "ZL exists and is not empty: " << path_to_file << endl;
                    return 0;
                }
            }
        }
        tSDRG_XXZ1(plist, dlist);
        // cout << "Process " << world_rank << " is handling iteration " << i << endl;
    }

    return 0;
}
