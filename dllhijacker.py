import argparse
import pefile
import os
import re

def list_dll_functions(executable_path):
    try:
        pe = pefile.PE(executable_path)
        dlls = {}

        if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
            for entry in pe.DIRECTORY_ENTRY_IMPORT:
                dll_name = entry.dll.decode('utf-8')
                functions = [imp.name.decode('utf-8') for imp in entry.imports if imp.name]
                dlls[dll_name] = {'functions': functions}

        # Trouver les 3 DLLs avec le moins de fonctions
        sorted_dlls = sorted(dlls.items(), key=lambda item: len(item[1]['functions']))
        top_3_dlls = sorted_dlls[:3]

        return [dll[0] for dll in top_3_dlls]

    except Exception as e:
        print(f"Erreur lors de l'analyse du fichier : {e}")
        return []

def validate_dll_path(dll_path):
    # Vérifier que le chemin contient uniquement des antislash par couple
    if not re.match(r'^(?:[a-zA-Z]:\\|\\\\|\\).*$', dll_path):
        raise ValueError("Le chemin de la DLL doit utiliser des antislashs (\\) uniquement par couple.")
    if '\\' not in dll_path:
        raise ValueError("Le chemin de la DLL doit contenir au moins un couple d'antislashs (\\).")

def generate_proxify_code(dll_path, dll_image, template_path):
    try:
        validate_dll_path(dll_path)

        dll_path_windows = dll_path.replace('\\', '\\\\')
        pe = pefile.PE(dll_image)

        exported_functions = []
        for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
            if exp.name is not None:
                exported_functions.append((exp.ordinal, exp.name.decode()))

        proxify_lines = []
        for ordinal, name in exported_functions:
            proxify_lines.append(f'#pragma comment(linker,"/export:{name}={dll_path_windows}.{name},@{ordinal}")')

        with open(template_path, 'r') as template_file:
            template_content = template_file.read()

        # Ajouter les lignes au début du template
        final_content = '#pragma once\n' + '\n'.join(proxify_lines) + '\n' + template_content

        # Sauvegarder dans un fichier spécifique au dossier release
        release_dir = "release"
        os.makedirs(release_dir, exist_ok=True)
        dll_basename = os.path.basename(dll_image)
        output_file = os.path.join(release_dir, f"{os.path.splitext(dll_basename)[0]}.c")

        with open(output_file, 'w') as output:
            output.write(final_content)

        print(f"Les lignes de proxification ont été ajoutées au fichier : {output_file}")
        return output_file, os.path.splitext(dll_basename)[0]
    except ValueError as ve:
        print(f"Erreur de validation du chemin : {ve}")
    except Exception as e:
        print(f"Erreur lors de la génération du code de proxification : {e}")

def main():
    parser = argparse.ArgumentParser(description="Script pour l'analyse de DLL et la proxification.")

    subparsers = parser.add_subparsers(dest="command", required=True, help="Sous-commandes disponibles")

    # Première fonctionnalité
    parser_analyse = subparsers.add_parser("analyse", help="Analyse les DLL d'un exécutable")
    parser_analyse.add_argument("--executable", required=True, help="Chemin de l'exécutable à analyser")

    # Deuxième fonctionnalité
    parser_proxify = subparsers.add_parser("proxify", help="Génère le code de proxification pour une DLL")
    parser_proxify.add_argument("--dllpath", required=True, help="Chemin de la DLL cible")
    parser_proxify.add_argument("--dllimage", required=True, help="Chemin de l'image DLL à analyser")
    parser_proxify.add_argument("--template", required=True, help="Chemin du fichier template")

    args = parser.parse_args()

    if args.command == "analyse":
        dll_list = list_dll_functions(args.executable)
        if dll_list:
            script_name = os.path.basename(__file__)
            print("Analyse terminée, maintenant cherche et récupère l'une de ces DLL (sur le système cible):")
            for dll in dll_list:
                print(f"- {dll}")
            print("pour t'aider : dir /s /b file.dll\n")
            print("N'oublie pas de noter le chemin absolu de la DLL !\n")
            print(f"Next step : {script_name} proxify --dllpath \"path_of_dll\" --dllimage \"dlltoproxify\" --template template.c")
            print(f"Exemple : {script_name} proxify --dllpath \"C:\\\Windows\\\System32\\\winmm.dll\" --dllimage winmm.dll --template template.c")
        else:
            print("Aucune DLL n'a pu être analysée.")

    elif args.command == "proxify":
        output_file, dll_base = generate_proxify_code(args.dllpath, args.dllimage, args.template)
        if output_file:
            print(f"Compilation 64 bits : x86_64-w64-mingw32-gcc -shared -o release/{dll_base}.dll {output_file} -Wl,--subsystem,windows")
            print(f"Compilation 32 bits : i686-w64-mingw32-gcc -shared -o release/{dll_base}.dll {output_file} -Wl,--subsystem,windows")

if __name__ == "__main__":
    main()
