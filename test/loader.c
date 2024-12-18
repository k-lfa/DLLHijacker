#include <windows.h>
#include <stdio.h>

int main() {
    // Charger la bibliothèque nouvellement crée
    HMODULE hModule = LoadLibrary("DLLTOTEST");

    // Vérifier si le chargement a réussi
    if (hModule != NULL) {
        printf("La bibliothèque DLLTOTEST a été chargée avec succès.\n");
        // Libérer la bibliothèque après l'utilisation
        FreeLibrary(hModule);
    } else {
        printf("Le chargement de la bibliothèque DLLTOTEST a échoué.\n");
    }

    return 0;
}
