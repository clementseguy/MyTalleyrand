-- GameplayScript.lua: export d'état de partie pour MyTalleyrand

print("MyTalleyrand Mod chargé")

local SCHEMA_VERSION = "0.1.0"
local EXPORT_PATH = "../MODS/MyTalleyrand/export/gamestate.json"
local TEMP_EXPORT_PATH = "../MODS/MyTalleyrand/export/gamestate.tmp.json"

local function JsonEscape(value)
    local escaped = tostring(value)
    escaped = string.gsub(escaped, "\\", "\\\\")
    escaped = string.gsub(escaped, '"', '\\"')
    escaped = string.gsub(escaped, "\n", "\\n")
    escaped = string.gsub(escaped, "\r", "\\r")
    escaped = string.gsub(escaped, "\t", "\\t")
    return escaped
end

local function BuildGameState(activePlayerId)
    local player = Players[activePlayerId]
    if not player then
        return nil
    end

    local turnNumber = Game.GetGameTurn() + 1
    local turnId = turnNumber
    local timestamp = os.date("!%Y-%m-%dT%H:%M:%SZ")

    local civType = "UNKNOWN"
    local leaderType = "UNKNOWN"

    if player.GetCivilizationType then
        local civId = player:GetCivilizationType()
        if civId and civId >= 0 and GameInfo.Civilizations[civId] then
            civType = GameInfo.Civilizations[civId].Type or civType
        end
    end

    if player.GetLeaderType then
        local leaderId = player:GetLeaderType()
        if leaderId and leaderId >= 0 and GameInfo.Leaders[leaderId] then
            leaderType = GameInfo.Leaders[leaderId].Type or leaderType
        end
    end

    local gold = 0
    if player.GetGold then
        gold = player:GetGold()
    end

    local science = 0
    if player.GetScience then
        science = player:GetScience()
    elseif Teams and player.GetTeam and Teams[player:GetTeam()] and Teams[player:GetTeam()].GetTeamTechs then
        local teamTechs = Teams[player:GetTeam()]:GetTeamTechs()
        if teamTechs and teamTechs.GetResearchProgress then
            science = teamTechs:GetResearchProgress(0) or 0
        end
    end

    local json = string.format(
        '{"schema_version":"%s","turn_id":%d,"turn_number":%d,"timestamp_utc":"%s","player":{"id":%d,"civilization":"%s","leader":"%s"},"resources":{"gold":%d,"science":%d}}',
        JsonEscape(SCHEMA_VERSION),
        turnId,
        turnNumber,
        JsonEscape(timestamp),
        activePlayerId,
        JsonEscape(civType),
        JsonEscape(leaderType),
        gold,
        science
    )

    return json, turnId
end

local function AtomicWrite(content)
    local tempFile = io.open(TEMP_EXPORT_PATH, "w")
    if not tempFile then
        return false, "impossible de créer le fichier temporaire"
    end

    tempFile:write(content)
    tempFile:flush()
    tempFile:close()

    local renamed, renameError = os.rename(TEMP_EXPORT_PATH, EXPORT_PATH)
    if not renamed then
        return false, renameError or "rename échoué"
    end

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
        print("[MyTalleyrand] Export échoué: " .. tostring(err))
        return
    end

    print("[MyTalleyrand] Export gamestate.json réussi pour turn_id=" .. tostring(turnId))
end

local function OnPlayerDoTurn(playerId)
    local activePlayer = Game.GetActivePlayer()
    if playerId ~= activePlayer then
        return
    end

    CollectGameState(activePlayer)
end

function Initialize()
    print("Initialisation du mod MyTalleyrand")
end

Events.LoadScreenClose.Add(Initialize)
GameEvents.PlayerDoTurn.Add(OnPlayerDoTurn)
