#include <iostream>
#include <filesystem>
#include <fstream>
#include <string>
#include <sstream>
#include <utility>


namespace fl = std::filesystem;


void print(std::string content){
    std::cout << content << "\n";
}


std::string trim(const std::string& str){
    size_t first = str.find_first_not_of(" \t\r\n");
    if (first == std::string::npos)
        return "";

    size_t last = str.find_last_not_of(" \t\r\n");
    return str.substr(first, last - first + 1);
}


std::pair<std::string, std::string> get_blender_exec_and_project(){
    std::ifstream file("config.txt");

    if (!file.is_open())
    {
        std::cout << "|x| Arquivo de configuração não encontrado." << std::endl;
        return {"", ""};
    }

    std::string blender_exec;
    std::string blender_project;
    std::string line;

    while (std::getline(file, line))
    {
        line = trim(line);

        // Ignora linhas vazias e comentários
        if (line.empty() || line[0] == '#')
            continue;

        size_t pos = line.find(':');

        if (pos == std::string::npos)
            continue;

        std::string title = trim(line.substr(0, pos));
        std::string content = trim(line.substr(pos + 1));

        if (title == "blender_exec")
            blender_exec = content;
        else if (title == "blender_project")
            blender_project = content;
    }

    file.close();

    return {blender_exec, blender_project};
}


std::string scriptString(){
    
    std::string st1 = "import bpy\nfrom sys import path as sys_path\n\n";
    std::ostringstream st2;
    st2 << "PROJECT_PATH=" << fl::current_path() << "\n\n";
    std::string st3 = "if PROJECT_PATH in sys_path:\n\tprint('Path já configurado')\n";
    std::string st4 = "else:\n\tsys_path.append(PROJECT_PATH)\n\tprint('Path foi adicionado')\n\n";
    std::string st5 = "bpy.ops.script.python_file_run(filepath=f'{PROJECT_PATH}/blender_scripts/create_gui_blender.py')\n";

    return st1 + st2.str() + st3 + st4 + st5;
}

std::string pythonScriptBody(){
    std::string st1 = "import bpy\n\nSCRIPT_NAME = 'mocap_exec.py'\nSCRIPT = \"\"\"\n";
    std::string st2 = scriptString();
    std::string st3 = "\"\"\"\n\n";
    std::string st4 = "text = bpy.data.texts.new(SCRIPT_NAME)\ntext.write(SCRIPT)\n";
    std::string st5 = "for screen in bpy.data.screens:\n\tfor area in screen.areas:\n";
    std::string st6 = "\t\tif area.type == 'TEXT_EDITOR':\n\t\t\tarea.spaces.active.text = text\n\n";
    std::string st7 = "bpy.ops.wm.save_mainfile()\n\nprint('>> Script inserido no projeto')\n";

    return st1 + st2 + st3 + st4 + st5 + st6 + st7;
}


int main(){

    auto [blenderExec, blenderProjectPath] = get_blender_exec_and_project();
    bool error = false;

    // Executavel do blender
    if (!fl::exists(blenderExec)){
        print("|x| Executável do Blender não encontrado");
        error = true;
    }

    // Projeto do blender
    if (!fl::exists(blenderProjectPath)){
        print("|x| Projeto Blender não encontrado");
        error = true;
    }

    if (error)
        return 1;
    

    // Escrever script temporario
    std::ofstream file("temp_script.py");

    if (!file) {
        std::cerr << "Erro ao abrir o arquivo.\n";
        return 1;
    }

    file << pythonScriptBody();
    file.close();
    
    // Executar blender por linha de comando no terminal
    std::string command = blenderExec + " " + blenderProjectPath + " --background --python temp_script.py";    
    std::system(command.c_str());

    // Remover script temporario
    if (!fl::remove("temp_script.py"))
        print("|!| script temporário não foi removido.");
    



    return 0;
}
