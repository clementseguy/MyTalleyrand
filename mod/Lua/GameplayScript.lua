-- GameplayScript.lua: export d'état de partie pour MyTalleyrand

print("MyTalleyrand Mod chargé")

local SCHEMA_VERSION = "0.1.0"
local EXPORT_DIR = "../MODS/MyTalleyrand/export"
local EXPORT_PATH = EXPORT_DIR .. "/gamestate.json"
local TEMP_EXPORT_PATH = EXPORT_DIR .. "/gamestate.tmp.json"
local ACTIVITY_LOG_PATH = EXPORT_DIR .. "/gamestate_activity.log"

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
    local player = Players[activePlayerId]
    if not player then return nil end

    local turnNumber = Game.GetGameTurn() + 1
    local turnId = turnNumber
    local timestamp = os.date("!%Y-%m-%dT%H:%M:%SZ")

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

local function AppendActivityLog(message)
    local logFile = io.open(ACTIVITY_LOG_PATH, "a")
    if not logFile then
        print("[MyTalleyrand] Journal d’activité indisponible: " .. tostring(ACTIVITY_LOG_PATH))
        return
    end
    local timestamp = os.date("!%Y-%m-%dT%H:%M:%SZ")
    logFile:write("[" .. timestamp .. "] " .. message .. "\n")
    logFile:flush()
    logFile:close()
end

local function AtomicWrite(content)
    local tempFile = io.open(TEMP_EXPORT_PATH, "w")
    if not tempFile then return false, "impossible de créer le fichier temporaire" end
    tempFile:write(content)
    tempFile:flush()
    tempFile:close()
    local renamed, renameError = os.rename(TEMP_EXPORT_PATH, EXPORT_PATH)
    if not renamed then return false, renameError or "rename échoué" end
    return true
end

function CollectGameState(activePlayerId)
    local gameStateJson, turnId = BuildGameState(activePlayerId)
    if not gameStateJson then
        print("[MyTalleyrand] CollectGameState: joueur invalide")
        return
    end
    local ok, err = AtomicWrite(gameStateJson)
    if not ok then
        AppendActivityLog("export échoué turn_id=" .. tostring(turnId) .. ": " .. tostring(err))
        print("[MyTalleyrand] Export échoué: " .. tostring(err))
        return
    end
    AppendActivityLog("export créé/mis à jour turn_id=" .. tostring(turnId))
    print("[MyTalleyrand] Export gamestate.json réussi pour turn_id=" .. tostring(turnId))
end

local function OnPlayerDoTurn(playerId)
    local activePlayer = Game.GetActivePlayer()
    if playerId ~= activePlayer then return end
    local ok, err = pcall(CollectGameState, activePlayer)
    if not ok then print("[MyTalleyrand] Erreur inattendue: " .. tostring(err)) end
end

Events.LoadScreenClose.Add(function() print("[MyTalleyrand] Mod initialisé") end)
GameEvents.PlayerDoTurn.Add(OnPlayerDoTurn)
