-- GameplayScript.lua: Logique principale du mod
-- Ce fichier contient la logique de gameplay personnalisée

print("MyTalleyrand Mod chargé")

-- Fonction d'initialisation
function Initialize()
    print("Initialisation du mod MyTalleyrand")
    -- Ajoutez votre logique d'initialisation ici
end

-- Enregistrer les événements
Events.LoadScreenClose.Add(Initialize)
