-- GameplayScript.lua : export d'état de partie pour MyTalleyrand (contexte InGameUIAddin)
--
-- IMPORTANT (plateforme macOS / Aspyr) :
--   Le bac à sable Lua du contexte UI n'expose NI `io` NI `os.execute` sur ce build,
--   même avec EnableLuaDebugLibrary=1. L'écriture directe de fichiers est donc
--   impossible. On utilise à la place `Modding.OpenUserData()` : une base SQLite
--   persistante (ModUserData/<ModID>-<version>.db) que le coach Python lit ensuite.
--   Une écriture fichier best-effort est aussi tentée (utile sous Windows).

local SCHEMA_VERSION = "0.1.0"
local MOD_ID = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

print("[MyTalleyrand] >>> GameplayScript.lua chargé (contexte UI)")

-- --- Sonde de capacités -----------------------------------------------------
local function T(v) return type(v) end
local HAS_IO_OPEN   = (type(io) == "table" and type(io.open) == "function")
local HAS_OS_EXEC   = (type(os) == "table" and type(os.execute) == "function")
local HAS_OS_GETENV = (type(os) == "table" and type(os.getenv) == "function")
local HAS_USERDATA  = (type(Modding) == "table" and type(Modding.OpenUserData) == "function")
print("[MyTalleyrand] CAPS io.open=" .. (type(io)=="table" and T(io.open) or "n/a")
    .. " os.execute=" .. (type(os)=="table" and T(os.execute) or "n/a")
    .. " Modding.OpenUserData=" .. (type(Modding)=="table" and T(Modding.OpenUserData) or "n/a"))

-- Chemin d'export fichier (best-effort ; marchera surtout sous Windows).
local HOME = (HAS_OS_GETENV and os.getenv("HOME")) or ""
local EXPORT_DIR = HOME .. "/Library/Application Support/Sid Meier's Civilization 5/MODS/MyTalleyrand/export"
local EXPORT_PATH = EXPORT_DIR .. "/gamestate.json"

-- --- Voie principale : ModUserData (SQLite) --------------------------------
local g_userData = nil
local g_writeSeq = 0

local function GetUserData()
    if g_userData ~= nil then return g_userData end
    if not HAS_USERDATA then return nil end
    local version = 1
    if Modding.GetActivatedModVersion then
        version = Modding.GetActivatedModVersion(MOD_ID) or 1
    end
    local ok, ud = pcall(Modding.OpenUserData, MOD_ID, version)
    if ok and ud then g_userData = ud end
    return g_userData
end

-- Écrit une paire clé/valeur dans la base ModUserData. Renvoie true/false + détail.
local function UserDataSet(pairs_list)
    local ud = GetUserData()
    if not ud then return false, "Modding.OpenUserData indisponible" end
    local ok, err = pcall(function()
        for _, kv in ipairs(pairs_list) do
            ud.SetValue(kv[1], kv[2])
        end
    end)
    if ok then return true, "Modding.UserData(SQLite)" end
    return false, "SetValue a échoué: " .. tostring(err)
end

-- --- Voie secondaire : écriture fichier (best-effort) ----------------------
local function ShellQuote(s)
    return "'" .. tostring(s):gsub("'", "'\\''") .. "'"
end

local function TryWriteFile(path, content)
    if HAS_IO_OPEN then
        local f = io.open(path, "w")
        if f then f:write(content); f:flush(); f:close(); return true, "io.open" end
    end
    if HAS_OS_EXEC then
        local rc = os.execute("printf '%s' " .. ShellQuote(content) .. " > " .. ShellQuote(path))
        if rc == true or rc == 0 then return true, "os.execute" end
    end
    return false, "indisponible"
end

-- ---------------------------------------------------------------------------
-- Sérialisation JSON minimale
-- ---------------------------------------------------------------------------
local function SafeCall(fn, default)
    local ok, result = pcall(fn)
    if ok and result ~= nil then return result end
    return default
end

local function JsonEscape(value)
    local escaped = tostring(value or "")
    escaped = string.gsub(escaped, "\\", "\\\\")
    escaped = string.gsub(escaped, '"', '\\"')
    escaped = string.gsub(escaped, "\n", "\\n")
    escaped = string.gsub(escaped, "\r", "\\r")
    escaped = string.gsub(escaped, "\t", "\\t")
    escaped = string.gsub(escaped, "%z", "")
    return escaped
end

local function JsonValue(value)
    local valueType = type(value)
    if valueType == "number" then return tostring(value) end
    if valueType == "boolean" then return value and "true" or "false" end
    if value == nil then return "null" end
    return '"' .. JsonEscape(value) .. '"'
end

local function JsonObject(fields)
    local parts = {}
    for _, field in ipairs(fields) do
        table.insert(parts, '"' .. JsonEscape(field[1]) .. '":' .. JsonValue(field[2]))
    end
    return "{" .. table.concat(parts, ",") .. "}"
end

local function LookupType(tableRef, id, fallback)
    if id and id >= 0 and tableRef and tableRef[id] then
        return tableRef[id].Type or tableRef[id].Description or fallback
    end
    return fallback
end

-- ---------------------------------------------------------------------------
-- Collecte de l'état de jeu
-- ---------------------------------------------------------------------------
local function CollectGameParameters()
    local handicapId = SafeCall(function() return Game.GetHandicapType and Game.GetHandicapType() end, nil)
    if handicapId == nil then
        handicapId = SafeCall(function() return PreGame.GetHandicap and PreGame.GetHandicap(Game.GetActivePlayer()) end, nil)
    end
    local speedId = SafeCall(function() return Game.GetGameSpeedType and Game.GetGameSpeedType() end, nil)
    local worldId = SafeCall(function() return Map.GetWorldSize and Map.GetWorldSize() end, nil)
    return JsonObject({
        {"difficulty", LookupType(GameInfo.HandicapInfos, handicapId, "UNKNOWN")},
        {"map_size", LookupType(GameInfo.Worlds, worldId, "UNKNOWN")},
        {"game_speed", LookupType(GameInfo.GameSpeeds, speedId, "UNKNOWN")}
    })
end

local function CollectCities(player)
    local parts = {}
    if player.Cities then
        for city in player:Cities() do
            table.insert(parts, JsonObject({
                {"id", SafeCall(function() return city:GetID() end, 0)},
                {"name", SafeCall(function() return city:GetName() end, "UNKNOWN")},
                {"population", SafeCall(function() return city:GetPopulation() end, 0)},
                {"production", SafeCall(function() return city:GetProductionName() end, "UNKNOWN")}
            }))
        end
    end
    return "[" .. table.concat(parts, ",") .. "]"
end

local function CollectUnits(player)
    local parts = {}
    if player.Units then
        for unit in player:Units() do
            local unitTypeId = SafeCall(function() return unit:GetUnitType() end, -1)
            table.insert(parts, JsonObject({
                {"id", SafeCall(function() return unit:GetID() end, 0)},
                {"type", LookupType(GameInfo.Units, unitTypeId, "UNKNOWN")},
                {"x", SafeCall(function() return unit:GetX() end, 0)},
                {"y", SafeCall(function() return unit:GetY() end, 0)},
                {"moves", SafeCall(function() return unit:MovesLeft() end, 0)}
            }))
        end
    end
    return "[" .. table.concat(parts, ",") .. "]"
end

local function BuildGameState(activePlayerId)
    local player = Players and Players[activePlayerId]
    if not player then return nil end

    local turnNumber = SafeCall(function() return Game.GetGameTurn() + 1 end, 1)
    local turnId = turnNumber
    local timestamp = (os.date and os.date("!%Y-%m-%dT%H:%M:%SZ")) or ""

    local civId = SafeCall(function() return player:GetCivilizationType() end, -1)
    local leaderId = SafeCall(function() return player:GetLeaderType() end, -1)
    local gold = SafeCall(function() return player:GetGold() end, 0)
    local science = SafeCall(function() return player:GetScience() end, nil)
    if science == nil then
        science = SafeCall(function()
            local teamTechs = Teams[player:GetTeam()]:GetTeamTechs()
            return teamTechs:GetResearchProgress(0)
        end, 0)
    end

    local json = string.format(
        '{"schema_version":"%s","turn_id":%d,"turn_number":%d,"timestamp_utc":"%s","game_parameters":%s,"player":{"id":%d,"civilization":"%s","leader":"%s"},"resources":{"gold":%d,"science":%d},"cities":%s,"units":%s}',
        JsonEscape(SCHEMA_VERSION), turnId, turnNumber, JsonEscape(timestamp), CollectGameParameters(), activePlayerId,
        JsonEscape(LookupType(GameInfo.Civilizations, civId, "UNKNOWN")), JsonEscape(LookupType(GameInfo.Leaders, leaderId, "UNKNOWN")),
        gold, science, CollectCities(player), CollectUnits(player)
    )
    return json, turnId
end

local function ExportGameState(activePlayerId)
    local gameStateJson, turnId = BuildGameState(activePlayerId)
    if not gameStateJson then
        print("[MyTalleyrand] Export ignoré: joueur actif invalide")
        return
    end
    g_writeSeq = g_writeSeq + 1

    -- Voie principale : ModUserData (SQLite), lue par le coach.
    local okUD, howUD = UserDataSet({
        {"schema_version", SCHEMA_VERSION},
        {"turn_number", turnId},
        {"write_seq", g_writeSeq},
        {"gamestate_json", gameStateJson},
    })
    if okUD then
        print("[MyTalleyrand] Export UserData OK (turn=" .. tostring(turnId) .. ", seq=" .. g_writeSeq .. ")")
    else
        print("[MyTalleyrand] Export UserData ÉCHOUÉ: " .. tostring(howUD))
    end

    -- Voie secondaire best-effort : fichier (silencieux si impossible).
    local okF, howF = TryWriteFile(EXPORT_PATH, gameStateJson)
    if okF then print("[MyTalleyrand] (bonus) fichier écrit via " .. howF) end
end

-- ---------------------------------------------------------------------------
-- Hooks : contexte UI (InGameUIAddin)
-- ---------------------------------------------------------------------------
local function OnActivePlayerTurnStart()
    local activePlayer = SafeCall(function() return Game.GetActivePlayer() end, -1)
    if activePlayer == nil or activePlayer < 0 then return end
    local ok, err = pcall(ExportGameState, activePlayer)
    if not ok then print("[MyTalleyrand] Erreur inattendue dans l'export: " .. tostring(err)) end
end

-- Preuve d'écriture au chargement (avant tout tour).
local okInit, howInit = UserDataSet({{"loaded_at_turn", SafeCall(function() return Game.GetGameTurn() end, -1)}})
if okInit then
    print("[MyTalleyrand] UserData initialisée via " .. howInit)
else
    print("[MyTalleyrand] !!! UserData indisponible: " .. tostring(howInit))
end

if Events then
    if Events.LoadScreenClose then
        Events.LoadScreenClose.Add(function()
            print("[MyTalleyrand] LoadScreenClose : mod initialisé en jeu")
            OnActivePlayerTurnStart()
        end)
    end
    if Events.ActivePlayerTurnStart then
        Events.ActivePlayerTurnStart.Add(OnActivePlayerTurnStart)
        print("[MyTalleyrand] Hook Events.ActivePlayerTurnStart posé")
    else
        print("[MyTalleyrand] !!! Events.ActivePlayerTurnStart absent dans ce contexte")
    end
else
    print("[MyTalleyrand] !!! Table Events absente : mauvais contexte de chargement")
end
