from os import listdir


def cast_int(string:str) -> int | None:
    try:
        return int(float(string))

    except:
        return None


def file_name_check_extension(file_name:str, extension:str) -> str:
    
    if len(extension) < 2:
        return file_name

    if extension.rfind(".") == -1:
        extension = f".{extension}"

    index = file_name.rfind(".")

    if index == 0:
        # refazer verificacao novamente, por causa de problema com diretorios locais por exemplo: ./meu/diretorio
        index = file_name[1:].rfind(".")
    
    if index == -1:
        return f"{file_name}{extension}"
    
    else:
        check_ext = file_name[index:]

        if check_ext == extension:
            return file_name

        else:
            return f"{file_name[:index]}{extension}"


def get_progress_bar(progress_bar_total:int, progress_bar_value):

    PROGRESS_BAR_SIZE = 20

    percent = progress_bar_value / progress_bar_total

    amt = int((PROGRESS_BAR_SIZE * percent))
    rest = PROGRESS_BAR_SIZE - amt

    return f"[{'#'*amt}{" "*rest}]"
