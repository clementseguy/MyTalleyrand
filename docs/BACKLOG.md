# 📋 BACKLOG MyTalleyrand

**Date de mise à jour :** 22 décembre 2025  
**Version :** 1.0  
**Sprint actuel :** Sprint 0 - MVP Technique

---

## 📊 Vue d'ensemble

| Métrique | Valeur |
|----------|--------|
| **Total User Stories** | 14 |
| **Points totaux** | 115 |
| **US Terminées** | 0 |
| **US En cours** | 0 |
| **US À faire** | 14 |
| **Progression** | 0% |

### Répartition par Epic

| Epic | US | Points | Priorité | Statut |
|------|-----|--------|----------|--------|
| EPIC 1 : Fondations techniques | 3 | 21 | 🔴 P0 | 📝 À faire |
| EPIC 2 : Interface utilisateur | 2 | 26 | 🟠 P1 | 📝 À faire |
| EPIC 3 : Logique du coach | 3 | 26 | 🟡 P1 | 📝 À faire |
| EPIC 4 : Optimisation | 4 | 34 | 🟢 P3-P4 | 📝 À faire |
| EPIC 5 : Documentation | 2 | 18 | 🔵 P1-P2 | 📝 À faire |

### Légende des statuts
- 📝 **À faire** : Non démarré
- 🔄 **En cours** : Développement actif
- ✅ **Terminé** : Validé et testé
- ⏸️ **En attente** : Bloqué ou en pause
- 🚫 **Abandonné** : Non retenu

---

## 🔴 EPIC 1 : Fondations techniques

**Objectif :** Mettre en place l'infrastructure de base permettant la communication entre Civ5 et l'application coach.

**Statut global :** 📝 À faire (0/3)  
**Points :** 0/21

---

### US-001 : Collecte de données de jeu

**Statut :** 📝 À faire  
**Priorité :** 🔴 P0 (Bloquant)  
**Estimation :** 5 points  
**Assigné à :** _Non assigné_  
**Sprint :** Sprint 0

**User Story :**
> En tant que **mod Lua**  
> Je veux **exporter l'état du jeu dans un format structuré**  
> Afin que **l'application externe puisse l'analyser**

#### Tâches techniques

- [ ] **T1.1** Rechercher API Lua disponible dans Civ5
  - Documentation des fonctions `Game.*`, `Players.*`, `Map.*`
  - Identifier les limitations de sécurité Lua
  - Tester accès aux données en mode mod
  
- [ ] **T1.2** Créer fonction `CollectGameState()` en Lua
  - Structure de données cohérente
  - Gestion des données nulles/undefined
  - Optimisation performance
  
- [ ] **T1.3** Extraire paramètres de partie
  - Difficulté (`Game.GetHandicapType()`)
  - Taille de carte (`Map.GetWorldSize()`)
  - Civilisation joueur (`Players[0]:GetCivilizationType()`)
  - Vitesse de jeu (`Game.GetGameSpeedType()`)
  
- [ ] **T1.4** Extraire état du joueur
  - Ressources (or, science, culture, foi)
  - Liste des villes avec détails
  - Liste des unités avec positions
  - Technologies recherchées/acquises
  - Bâtiments construits
  
- [ ] **T1.5** Extraire relations diplomatiques
  - Liste des civilisations en vie
  - État des relations (paix/guerre/allié)
  - Accords commerciaux actifs
  
- [ ] **T1.6** Exporter en JSON dans dossier accessible ⚠️ **Spécifique macOS**
  ```lua
  -- Chemin macOS pour Civ5
  local exportPath = os.getenv("HOME") .. "/Documents/Aspyr/Sid Meier's Civilization 5/MODS/MyTalleyrand/export/"
  ```
  - Vérifier droits d'écriture sur macOS
  - Gérer permissions Gatekeeper
  - Tester avec SIP activé (System Integrity Protection)
  
- [ ] **T1.7** Implémenter encodage JSON en Lua
  - Créer module JSON encoder (pas de lib native)
  - Gérer caractères spéciaux
  - Valider format sortie
  
- [ ] **T1.8** Gérer les erreurs d'écriture fichier
  - Try/catch Lua (`pcall`)
  - Logs d'erreurs dans `Lua.log`
  - Fallback si échec d'écriture

#### Critères d'acceptation

✅ Fichier JSON généré à chaque tour  
✅ Toutes les données nécessaires présentes et valides  
✅ Format JSON validé (via jsonlint ou équivalent)  
✅ Performance < 100ms par export (mesuré)  
✅ Fonctionne sur macOS 13+ (Ventura, Sonoma)  
✅ Pas de crash du jeu lors de l'export

#### Dépendances
- Aucune (première US)

#### Risques
- ⚠️ Limitations API Lua non documentées
- ⚠️ Performance sur grandes parties (200+ tours)
- ⚠️ Permissions fichiers sur macOS

---

### US-002 : Application coach externe - Squelette

**Statut :** 📝 À faire  
**Priorité :** 🔴 P0 (Bloquant)  
**Estimation :** 8 points  
**Assigné à :** _Non assigné_  
**Sprint :** Sprint 0

**User Story :**
> En tant qu'**utilisateur**  
> Je veux **une application qui tourne en arrière-plan**  
> Afin de **recevoir des conseils pendant ma partie**

#### Tâches techniques

- [ ] **T2.1** Choisir stack technique ⚠️ **Décision macOS**
  
  **Option A : Python (Recommandée)** ✅
  ```bash
  # Installation macOS
  brew install python@3.11
  pip3 install flask watchdog openai
  ```
  - ✅ Natif sur macOS
  - ✅ PyQt6 fonctionne bien sur Apple Silicon
  - ✅ Pas de notarization nécessaire pour dev
  - ⚠️ Nécessite code signing pour distribution
  
  **Option B : Electron + Node**
  ```bash
  # Installation macOS
  brew install node
  npm init
  npm install electron express chokidar
  ```
  - ✅ UI moderne native
  - ✅ Distribution facile (.app)
  - ⚠️ Notarization obligatoire pour macOS 10.15+
  - ⚠️ Taille application plus lourde
  
  **→ Recommandation : Python pour MVP, Electron pour v2**

- [ ] **T2.2** Créer projet avec structure modulaire
  ```
  coach-app/
  ├── src/
  │   ├── __init__.py
  │   ├── file_watcher.py      # Surveillance gamestate.json
  │   ├── llm_client.py         # Appels API LLM
  │   ├── game_analyzer.py      # Logique d'analyse
  │   └── ui/
  │       ├── overlay.py        # Interface overlay
  │       └── assets/           # Images, CSS
  ├── config/
  │   └── settings.json         # Config utilisateur
  ├── tests/
  ├── requirements.txt
  └── main.py
  ```

- [ ] **T2.3** Implémenter lecture fichier gamestate.json
  ```python
  import json
  from pathlib import Path
  
  GAMESTATE_PATH = Path.home() / "Documents/Aspyr/Sid Meier's Civilization 5/MODS/MyTalleyrand/export/gamestate.json"
  
  def read_gamestate():
      if GAMESTATE_PATH.exists():
          with open(GAMESTATE_PATH) as f:
              return json.load(f)
  ```

- [ ] **T2.4** Créer système de polling (check nouveau tour)
  ```python
  from watchdog.observers import Observer
  from watchdog.events import FileSystemEventHandler
  
  class GameStateWatcher(FileSystemEventHandler):
      def on_modified(self, event):
          if event.src_path.endswith('gamestate.json'):
              self.process_new_turn()
  ```

- [ ] **T2.5** Logger les états de jeu détectés
  ```python
  import logging
  logging.basicConfig(
      filename='coach.log',
      level=logging.INFO,
      format='%(asctime)s - %(levelname)s - %(message)s'
  )
  ```

- [ ] **T2.6** Créer interface de lancement macOS
  - Script `start_coach.command` double-cliquable
  - Icône macOS (`.icns`)
  - Lancement via menu bar (optionnel)

#### Spécificités macOS

⚠️ **Points d'attention macOS :**

1. **Permissions Gatekeeper**
   ```bash
   # Pour dev, désactiver temporairement pour l'app
   xattr -d com.apple.quarantine coach-app
   ```

2. **Accès fichiers**
   - Demander "Full Disk Access" dans Préférences Système
   - Ou utiliser dossier Documents (autorisé par défaut)

3. **Overlay sur jeu plein écran**
   - Mode fenêtré requis pour overlay PyQt
   - Alternative : UIKit pour overlay natif (complexe)

4. **Distribution future**
   ```bash
   # Code signing
   codesign --deep --force --sign "Developer ID" coach-app.app
   
   # Notarization
   xcrun notarytool submit coach-app.zip --apple-id xxx --wait
   ```

#### Critères d'acceptation

✅ Application démarre sans erreur sur macOS 13+  
✅ Détecte nouveaux états de jeu en < 2s  
✅ Logs clairs et debuggables dans `~/coach.log`  
✅ Fonctionne avec Civ5 en mode fenêtré  
✅ CPU < 5% en idle  
✅ Mémoire < 200MB

#### Dépendances
- US-001 (nécessite gamestate.json)

#### Risques
- ⚠️ Overlay complexe sur macOS Sonoma
- ⚠️ Performance file watching sur gros fichiers
- ⚠️ Code signing pour distribution

---

### US-003 : Intégration API LLM

**Statut :** 📝 À faire  
**Priorité :** 🔴 P0 (Bloquant)  
**Estimation :** 8 points  
**Assigné à :** _Non assigné_  
**Sprint :** Sprint 0

**User Story :**
> En tant que **coach**  
> Je veux **envoyer l'état du jeu à un LLM**  
> Afin d'**obtenir des recommandations stratégiques**

#### Tâches techniques

- [ ] **T3.1** Choisir provider LLM
  
  **Options évaluées :**
  
  | Provider | Modèle | Coût/1M tokens | Latence | Qualité conseils |
  |----------|--------|----------------|---------|------------------|
  | OpenAI | GPT-4o | $2.50 | ~2s | ⭐⭐⭐⭐⭐ |
  | OpenAI | GPT-4o-mini | $0.15 | ~1s | ⭐⭐⭐⭐ |
  | Anthropic | Claude 3.5 Sonnet | $3.00 | ~2s | ⭐⭐⭐⭐⭐ |
  | Anthropic | Claude 3 Haiku | $0.25 | ~1s | ⭐⭐⭐ |
  | Local | Ollama (llama3) | Gratuit | ~5s | ⭐⭐⭐ |
  
  **→ Recommandation : GPT-4o-mini (MVP) + fallback Ollama**

- [ ] **T3.2** Créer module d'appel API
  ```python
  # llm_client.py
  import openai
  from anthropic import Anthropic
  
  class LLMClient:
      def __init__(self, provider='openai', model='gpt-4o-mini'):
          self.provider = provider
          self.model = model
          
      def send_request(self, prompt: str, context: dict) -> str:
          if self.provider == 'openai':
              return self._call_openai(prompt, context)
          elif self.provider == 'anthropic':
              return self._call_anthropic(prompt, context)
  ```

- [ ] **T3.3** Définir prompt système pour le coach
  ```python
  SYSTEM_PROMPT = """
  Tu es Talleyrand, conseiller diplomatique et stratégique expert de Civilization V.
  Tu analyses l'état d'une partie en cours et fournis des recommandations claires.
  
  Ton rôle :
  - Analyser la situation géopolitique
  - Proposer des objectifs à court terme (10 tours)
  - Recommander des actions concrètes (constructions, techs, diplomatie)
  - Adapter les conseils au type de victoire visé
  
  Style :
  - Concis et actionnable
  - Diplomatique mais ferme
  - Justifications stratégiques brèves
  """
  ```

- [ ] **T3.4** Structurer les requêtes (état → prompt)
  ```python
  def build_prompt(gamestate: dict) -> str:
      turn = gamestate['turn']
      player = gamestate['player']
      
      prompt = f"""
      === SITUATION (Tour {turn}) ===
      Civilisation : {player['civ']}
      Ressources : {player['gold']} or, {player['science']} science
      Villes : {len(player['cities'])}
      Objectif : {player['victory_type']}
      
      === ANALYSE DEMANDÉE ===
      1. Évaluation de la situation
      2. Objectif pour 10 prochains tours
      3. Top 5 actions prioritaires
      """
      return prompt
  ```

- [ ] **T3.5** Parser les réponses du LLM
  ```python
  import re
  
  def parse_llm_response(response: str) -> dict:
      return {
          'analysis': extract_section(response, 'SITUATION'),
          'objective': extract_section(response, 'OBJECTIF'),
          'actions': extract_actions(response)
      }
  ```

- [ ] **T3.6** Gérer retry et erreurs réseau
  ```python
  from tenacity import retry, stop_after_attempt, wait_exponential
  
  @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
  def call_llm_with_retry(prompt):
      # ...
  ```

- [ ] **T3.7** Implémenter rate limiting
  ```python
  from ratelimit import limits, sleep_and_retry
  
  @sleep_and_retry
  @limits(calls=10, period=60)  # 10 calls/minute
  def call_llm(prompt):
      # ...
  ```

- [ ] **T3.8** Gérer clés API de manière sécurisée ⚠️ **macOS Keychain**
  ```python
  import keyring
  
  # Stocker
  keyring.set_password("MyTalleyrand", "openai_api_key", "sk-...")
  
  # Récupérer
  api_key = keyring.get_password("MyTalleyrand", "openai_api_key")
  ```

#### Critères d'acceptation

✅ Appel API réussi avec gamestate complet  
✅ Réponse parsée et structurée en JSON  
✅ Gestion des erreurs (timeout, quota, network)  
✅ Temps de réponse < 10s (95e percentile)  
✅ Clés API stockées de manière sécurisée (Keychain macOS)  
✅ Rate limiting fonctionnel (pas de ban API)  
✅ Coût estimé < $0.05 par analyse

#### Dépendances
- US-002 (nécessite application coach)

#### Risques
- ⚠️ Coût LLM si partie longue (200+ tours)
- ⚠️ Latence réseau variable
- ⚠️ Qualité réponses à valider

---

## 🟠 EPIC 2 : Interface utilisateur

**Objectif :** Créer une interface overlay élégante et fonctionnelle.

**Statut global :** 📝 À faire (0/2)  
**Points :** 0/26

---

### US-004 : Overlay de base

**Statut :** 📝 À faire  
**Priorité :** 🟠 P1  
**Estimation :** 13 points  
**Assigné à :** _Non assigné_  
**Sprint :** Sprint 1

**User Story :**
> En tant qu'**utilisateur**  
> Je veux **voir les conseils du coach superposés sur le jeu**  
> Afin de **ne pas avoir à alt-tab**

#### Tâches techniques

- [ ] **T4.1** Rechercher solutions overlay macOS
  
  **Options techniques :**
  
  1. **PyQt6 (Recommandé pour MVP)**
     ```python
     from PyQt6.QtWidgets import QWidget
     from PyQt6.QtCore import Qt
     
     class OverlayWindow(QWidget):
         def __init__(self):
             super().__init__()
             self.setWindowFlags(
                 Qt.WindowType.WindowStaysOnTopHint |
                 Qt.WindowType.FramelessWindowHint |
                 Qt.WindowType.Tool
             )
             self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
     ```
     - ✅ Fonctionne sur Apple Silicon
     - ✅ Transparent background supporté
     - ⚠️ Nécessite mode fenêtré pour Civ5
  
  2. **Rumps (Menu Bar App)**
     ```python
     import rumps
     
     class TalleyrandApp(rumps.App):
         @rumps.clicked("Afficher conseils")
         def show_advice(self, _):
             # ...
     ```
     - ✅ Natif macOS
     - ✅ Léger et performant
     - ⚠️ Moins "overlay", plus popup
  
  3. **Electron (Future v2)**
     - ✅ Overlay puissant
     - ⚠️ Plus complexe

- [ ] **T4.2** Créer fenêtre overlay transparente
  ```python
  # overlay.py
  import sys
  from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
  from PyQt6.QtCore import Qt, QTimer
  from PyQt6.QtGui import QPalette, QColor
  
  class CoachOverlay(QWidget):
      def __init__(self):
          super().__init__()
          self.setup_ui()
          
      def setup_ui(self):
          # Flags pour overlay
          self.setWindowFlags(
              Qt.WindowType.WindowStaysOnTopHint |
              Qt.WindowType.FramelessWindowHint |
              Qt.WindowType.Tool
          )
          
          # Background semi-transparent
          self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
          
          # Ignorer clics (passthrough)
          self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
  ```

- [ ] **T4.3** Détecter position de la fenêtre Civ5 ⚠️ **macOS spécifique**
  ```python
  from AppKit import NSWorkspace
  import Quartz
  
  def find_civ5_window():
      """Trouve la fenêtre Civ5 sur macOS"""
      options = Quartz.kCGWindowListOptionOnScreenOnly
      window_list = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)
      
      for window in window_list:
          if 'Civilization V' in window.get('kCGWindowOwnerName', ''):
              bounds = window['kCGWindowBounds']
              return {
                  'x': bounds['X'],
                  'y': bounds['Y'],
                  'width': bounds['Width'],
                  'height': bounds['Height']
              }
  ```

- [ ] **T4.4** Afficher texte par-dessus le jeu
  ```python
  def show_advice(self, text: str):
      # Zone de texte stylisée
      label = QLabel(text)
      label.setStyleSheet("""
          QLabel {
              background-color: rgba(0, 0, 0, 180);
              color: #FFD700;
              padding: 20px;
              border-radius: 10px;
              font-size: 14pt;
              font-family: 'Trajan Pro', serif;
          }
      """)
  ```

- [ ] **T4.5** Rendre l'overlay cliquable/déplaçable
  ```python
  def mousePressEvent(self, event):
      if event.button() == Qt.MouseButton.LeftButton:
          self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
          
  def mouseMoveEvent(self, event):
      if event.buttons() == Qt.MouseButton.LeftButton:
          self.move(event.globalPosition().toPoint() - self.drag_position)
  ```

- [ ] **T4.6** Gérer multi-écrans macOS
  ```python
  from PyQt6.QtGui import QScreen
  
  def position_on_correct_screen():
      # Déterminer quel écran contient Civ5
      screens = QApplication.screens()
      civ5_bounds = find_civ5_window()
      
      for screen in screens:
          if screen.geometry().contains(civ5_bounds['x'], civ5_bounds['y']):
              return screen
  ```

- [ ] **T4.7** Optimiser performance overlay
  - Update rate max 30 FPS
  - Pas de redraw si pas de changement
  - Utiliser QTimer pour updates

- [ ] **T4.8** Gérer permissions macOS
  ```python
  # Vérifier accès Accessibility
  from ApplicationServices import AXIsProcessTrusted
  
  if not AXIsProcessTrusted():
      print("Activer 'Accessibility' dans Préférences Système")
  ```

#### Spécificités macOS

⚠️ **Configuration requise :**

1. **Civ5 en mode fenêtré**
   - Settings → Graphics → Display Mode : Windowed
   - Fullscreen rendra l'overlay invisible

2. **Permissions système**
   ```bash
   # Préférences Système → Confidentialité
   # - Accessibilité : Cocher l'app coach
   # - Enregistrement écran : Si screenshots
   ```

3. **Performance**
   - Désactiver shadows pour overlay
   - Utiliser Metal pour rendering si possible

#### Critères d'acceptation

✅ Overlay visible par-dessus Civ5 (mode fenêtré)  
✅ Transparent sauf zone de conseils  
✅ Ne bloque pas les clics sur le jeu  
✅ Position persistante entre sessions  
✅ Fonctionne sur multi-écrans  
✅ FPS stable (pas de lag du jeu)  
✅ Permissions système gérées gracieusement

#### Dépendances
- US-002 (application coach)
- US-003 (contenu à afficher)

#### Risques
- ⚠️ Complexité overlay sur macOS Sonoma
- ⚠️ Mode plein écran incompatible
- ⚠️ Performance sur écrans Retina

---

### US-005 : Interface style conseiller Civ5

**Statut :** 📝 À faire  
**Priorité :** 🟠 P2  
**Estimation :** 13 points  
**Assigné à :** _Non assigné_  
**Sprint :** Sprint 3

**User Story :**
> En tant qu'**utilisateur**  
> Je veux **une UI qui ressemble aux conseillers natifs**  
> Afin d'**avoir une expérience cohérente**

#### Tâches techniques

- [ ] **T5.1** Analyser les assets des conseillers Civ5
  - Extraire sprites depuis le jeu
  - Analyser couleurs et fonts utilisées
  - Identifier animations (fade in/out)

- [ ] **T5.2** Créer mockups de l'interface
  - Figma/Sketch pour design
  - Variantes : popup, sidebar, bottom bar
  - Validation UX

- [ ] **T5.3** Implémenter design (PyQt6)
  ```python
  # Style inspiré Civ5
  ADVISOR_STYLE = """
  QWidget#advisor {
      background: qlineargradient(
          x1:0, y1:0, x2:0, y2:1,
          stop:0 rgba(20, 20, 40, 230),
          stop:1 rgba(10, 10, 20, 230)
      );
      border: 2px solid #8B7355;
      border-radius: 15px;
  }
  
  QLabel#title {
      color: #FFD700;
      font-family: 'Trajan Pro', serif;
      font-size: 18pt;
      font-weight: bold;
  }
  
  QLabel#advice {
      color: #E8E8E8;
      font-family: 'Garamond', serif;
      font-size: 12pt;
      line-height: 1.4;
  }
  """
  ```

- [ ] **T5.4** Ajouter portrait de Talleyrand
  - Trouver/créer portrait style Civ5
  - Format PNG transparent
  - Résolution adaptée Retina (2x, 3x)
  - Animation subtile (breathing effect)

- [ ] **T5.5** Animer l'apparition des conseils
  ```python
  from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
  
  def fade_in_animation(widget):
      animation = QPropertyAnimation(widget, b"windowOpacity")
      animation.setDuration(500)
      animation.setStartValue(0)
      animation.setEndValue(1)
      animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
      animation.start()
  ```

- [ ] **T5.6** Ajouter boutons (fermer, réduire, historique)
  ```python
  # Boutons custom style Civ5
  close_btn = QPushButton("✕")
  close_btn.setStyleSheet("""
      QPushButton {
          background-color: #8B0000;
          color: white;
          border-radius: 15px;
          padding: 5px 10px;
      }
      QPushButton:hover {
          background-color: #CD5C5C;
      }
  """)
  ```

- [ ] **T5.7** Implémenter système d'historique
  - Carousel des conseils précédents
  - Navigation ← →
  - Timestamps

- [ ] **T5.8** Adapter pour HiDPI/Retina
  ```python
  # Support écrans Retina macOS
  QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
  QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
  ```

#### Critères d'acceptation

✅ Ressemble visuellement aux conseillers Civ5  
✅ Responsive sur différentes résolutions  
✅ Animations fluides (60 FPS)  
✅ Tous les boutons fonctionnels  
✅ Portrait de Talleyrand intégré  
✅ Lisible sur écran Retina  
✅ Thème cohérent avec le jeu

#### Dépendances
- US-004 (overlay de base)

#### Risques
- ⚠️ Droits d'auteur sur assets Civ5
- ⚠️ Font "Trajan Pro" non libre

---

## 🟡 EPIC 3 : Logique du coach

**Objectif :** Implémenter l'intelligence et les recommandations du coach.

**Statut global :** 📝 À faire (0/3)  
**Points :** 0/26

---

### US-006 : Dialogue d'initialisation (Tour 1)

**Statut :** 📝 À faire  
**Priorité :** 🟡 P1  
**Estimation :** 5 points  
**Assigné à :** _Non assigné_  
**Sprint :** Sprint 1

**User Story :**
> En tant que **joueur**  
> Je veux **indiquer ma stratégie de victoire au tour 1**  
> Afin que **le coach adapte ses conseils**

#### Tâches techniques

- [ ] **T6.1** Créer popup au tour 1 dans l'overlay
  ```python
  def show_initial_dialog(self):
      if self.gamestate['turn'] == 1 and not self.initialized:
          dialog = VictoryTypeDialog(self)
          dialog.exec()
  ```

- [ ] **T6.2** Proposer choix de victoire
  - Domination 🗡️
  - Science 🔬
  - Culture 🎭
  - Diplomatie 🤝
  - Time (score)

- [ ] **T6.3** Détecter automatiquement paramètres de partie
  - Difficulté
  - Taille carte
  - Vitesse
  - DLC activés

- [ ] **T6.4** Sauvegarder les préférences du joueur
  ```python
  import json
  
  preferences = {
      'victory_type': 'science',
      'playstyle': 'aggressive',  # peaceful/balanced/aggressive
      'detail_level': 'expert'     # beginner/intermediate/expert
  }
  
  with open('user_preferences.json', 'w') as f:
      json.dump(preferences, f)
  ```

- [ ] **T6.5** Envoyer ces infos au LLM pour contexte
  - Ajouter au prompt système
  - Personnaliser recommandations

#### Critères d'acceptation

✅ Popup s'affiche au tour 1 uniquement  
✅ Tous les types de victoire proposés  
✅ Détection auto des paramètres fonctionne  
✅ Préférences sauvegardées et réutilisées  
✅ Peut être modifié en cours de partie

#### Dépendances
- US-004 (overlay)

---

### US-007 : Analyse cyclique (tous les 10 tours)

**Statut :** 📝 À faire  
**Priorité :** 🟡 P1  
**Estimation :** 8 points  
**Assigné à :** _Non assigné_  
**Sprint :** Sprint 2

**User Story :**
> En tant que **coach**  
> Je veux **analyser la partie tous les 10 tours**  
> Afin de **proposer un objectif à 10 tours**

#### Tâches techniques

- [ ] **T7.1** Implémenter déclencheur tous les 10 tours
  ```python
  def should_analyze(self, turn: int) -> bool:
      return turn == 1 or turn % 10 == 0
  ```

- [ ] **T7.2** Créer prompt "analyse de situation"
  ```
  Analyse la situation actuelle :
  - Position par rapport aux autres civs
  - Forces et faiblesses
  - Opportunités immédiates
  - Menaces à surveiller
  
  Propose UN objectif principal pour les 10 prochains tours.
  ```

- [ ] **T7.3** Demander au LLM un objectif pour 10 prochains tours
  - Objectif SMART (Spécifique, Mesurable, etc.)
  - Aligné avec type de victoire

- [ ] **T7.4** Afficher l'objectif dans l'overlay
  - Section "Objectif actuel"
  - Progress bar si quantifiable

- [ ] **T7.5** Sauvegarder historique des objectifs
  ```python
  objectives_history = [
      {'turn': 1, 'objective': 'Fonder 2 villes', 'status': 'completed'},
      {'turn': 10, 'objective': 'Rechercher Writing', 'status': 'in_progress'},
  ]
  ```

#### Critères d'acceptation

✅ Analyse tous les 10 tours exactement  
✅ Objectif clair et actionnable  
✅ Affiché dans l'UI de manière prominente  
✅ Historique accessible et consultable

#### Dépendances
- US-003 (LLM)
- US-004 (overlay)

---

### US-008 : Recommandations d'actions

**Statut :** 📝 À faire  
**Priorité :** 🟡 P1  
**Estimation :** 13 points  
**Assigné à :** _Non assigné_  
**Sprint :** Sprint 2

**User Story :**
> En tant que **joueur**  
> Je veux **recevoir des actions concrètes à effectuer**  
> Afin de **progresser vers mon objectif**

#### Tâches techniques

- [ ] **T8.1** Créer prompt "recommandations d'actions"
  ```
  Fournis 5 actions prioritaires pour progresser vers l'objectif :
  
  Format souhaité :
  1. [CONSTRUCTION] Construire Bibliothèque à Paris
  2. [SCIENCE] Rechercher Philosophy
  3. [DIPLOMATIE] Ouvrir frontières avec Rome
  4. [MILITAIRE] Créer 2 archers à Lyon
  5. [EXPANSION] Fonder ville près de Marseille
  ```

- [ ] **T8.2** Structurer réponse LLM (liste d'actions)
  ```python
  actions = [
      {
          'category': 'construction',
          'description': 'Construire Bibliothèque à Paris',
          'priority': 'high',
          'reasoning': 'Booste science pour Philosophy'
      }
  ]
  ```

- [ ] **T8.3** Afficher actions dans l'UI (checklist)
  ```python
  # Checklist interactive
  for action in actions:
      checkbox = QCheckBox(action['description'])
      checkbox.stateChanged.connect(self.mark_action_done)
  ```

- [ ] **T8.4** Catégoriser actions
  - 🏗️ Construction
  - 🔬 Science
  - 🤝 Diplomatie
  - ⚔️ Militaire
  - 📈 Économie
  - 🏛️ Culture

- [ ] **T8.5** Ajouter tooltips explicatifs
  - Pourquoi cette action ?
  - Bénéfices attendus
  - Alternatives possibles

- [ ] **T8.6** Système de progression
  - Cocher actions réalisées
  - Calculer % de completion
  - Feedback positif

#### Critères d'acceptation

✅ Au moins 3-5 actions par analyse  
✅ Actions claires et réalisables dans le jeu  
✅ Catégorisées et priorisées  
✅ Affichées de manière lisible avec icônes  
✅ Tooltips informatifs disponibles

#### Dépendances
- US-007 (objectifs)

---

## 🟢 EPIC 4 : Optimisation et polish

**Statut global :** 📝 À faire (0/4)  
**Points :** 0/34

*(US-009 à US-012 : voir TODO.md pour détails)*

---

## 🔵 EPIC 5 : Documentation et tests

**Statut global :** 📝 À faire (0/2)  
**Points :** 0/18

---

### US-013 : Documentation utilisateur

**Statut :** 📝 À faire  
**Priorité :** 🔵 P1  
**Estimation :** 5 points  
**Assigné à :** _Non assigné_  
**Sprint :** Sprint 3

#### Tâches techniques

- [ ] **T13.1** README avec installation détaillée macOS
  ```markdown
  ## Installation (macOS)
  
  ### Prérequis
  - macOS 13+ (Ventura ou Sonoma)
  - Civilization V (Steam ou App Store)
  - Python 3.11+ (`brew install python@3.11`)
  
  ### Installation
  1. Installer le mod Lua
  2. Installer l'application coach
  3. Configurer clé API LLM
  4. Donner permissions système
  ```

- [ ] **T13.2** Guide de configuration LLM API
  - Créer compte OpenAI/Anthropic
  - Obtenir clé API
  - Configurer dans l'app
  - Vérifier fonctionnement

- [ ] **T13.3** Troubleshooting macOS
  ```markdown
  ## Problèmes fréquents (macOS)
  
  ### L'overlay ne s'affiche pas
  - Vérifier Civ5 en mode fenêtré
  - Donner accès "Accessibilité" à l'app
  
  ### Pas de gamestate.json généré
  - Vérifier permissions du dossier MODS
  - Consulter Lua.log
  ```

- [ ] **T13.4** Vidéo de démonstration
  - Screen recording
  - Voice-over explicatif
  - Upload YouTube

#### Critères d'acceptation

✅ README complet et clair  
✅ Installation testée sur Mac neuf  
✅ Troubleshooting couvre 90% des cas  
✅ Vidéo < 5 minutes, qualité HD

---

### US-014 : Tests et validation

**Statut :** 📝 À faire  
**Priorité :** 🔵 P2  
**Estimation :** 13 points  
**Assigné à :** _Non assigné_  
**Sprint :** Sprint 3

#### Tâches techniques

- [ ] **T14.1** Tests unitaires Python
  ```python
  # tests/test_file_watcher.py
  def test_gamestate_detection():
      watcher = GameStateWatcher()
      assert watcher.detect_new_turn() == True
  ```

- [ ] **T14.2** Tests d'intégration
  - Mod Lua → JSON export
  - JSON → Coach app
  - Coach app → LLM → Overlay

- [ ] **T14.3** Tests en partie réelle
  - Partie complète (0-200 tours)
  - Performance CPU/RAM
  - Pas de crash

- [ ] **T14.4** Validation performance
  - Export JSON < 100ms
  - LLM response < 10s
  - Overlay 60 FPS
  - RAM < 200MB

#### Critères d'acceptation

✅ Coverage tests > 70%  
✅ Tests intégration passent  
✅ Partie 200 tours sans crash  
✅ Performance targets atteints

---

## 📅 Roadmap & Sprints

### Sprint 0 : MVP Technique (2-3 semaines)
**Objectif :** Prouver la faisabilité technique

| US | Statut | Points |
|----|--------|--------|
| US-001 | 📝 | 5 |
| US-002 | 📝 | 8 |
| US-003 | 📝 | 8 |
| **Total** | **0%** | **21** |

**Critère de sortie :** Gamestate JSON → LLM → Réponse texte

---

### Sprint 1 : Interface de base (2 semaines)
**Objectif :** Première version utilisable

| US | Statut | Points |
|----|--------|--------|
| US-004 | 📝 | 13 |
| US-006 | 📝 | 5 |
| **Total** | **0%** | **18** |

**Critère de sortie :** Overlay fonctionnel affichant conseils

---

### Sprint 2 : Logique coach (2-3 semaines)
**Objectif :** Coach intelligent et utile

| US | Statut | Points |
|----|--------|--------|
| US-007 | 📝 | 8 |
| US-008 | 📝 | 13 |
| **Total** | **0%** | **21** |

**Critère de sortie :** Objectifs + actions recommandées

---

### Sprint 3 : Polish MVP (1-2 semaines)
**Objectif :** Version 1.0 publiable

| US | Statut | Points |
|----|--------|--------|
| US-005 | 📝 | 13 |
| US-013 | 📝 | 5 |
| US-014 | 📝 | 13 |
| **Total** | **0%** | **31** |

**Critère de sortie :** Documentation + tests validés

---

### Sprint 4+ : Améliorations
**Objectif :** Optimisations et fonctionnalités avancées

| US | Statut | Points |
|----|--------|--------|
| US-009 | 📝 | 5 |
| US-010 | 📝 | 8 |
| US-011 | 📝 | 8 |
| US-012 | 📝 | 13 |
| **Total** | **0%** | **34** |

---

## 🔧 Stack technique finale (macOS)

### Décisions prises

| Composant | Choix | Justification |
|-----------|-------|---------------|
| **App Coach** | Python 3.11+ | Natif macOS, simple pour MVP |
| **UI Overlay** | PyQt6 | Fonctionne sur Apple Silicon |
| **LLM Provider** | OpenAI GPT-4o-mini | Bon rapport qualité/coût |
| **File Watch** | watchdog | Cross-platform, mature |
| **Config Storage** | JSON + Keychain | Sécurisé pour API keys |

### Installation développement (macOS)

```bash
# Prérequis
brew install python@3.11

# Dépendances
pip3 install --upgrade pip
pip3 install PyQt6 openai watchdog keyring

# Vérifier
python3 --version  # 3.11+
```

---

## 📊 Métriques de suivi

### Vélocité par sprint
- Sprint 0 : _À mesurer_
- Sprint 1 : _À mesurer_
- Sprint 2 : _À mesurer_

### Burndown
- Total : 115 points
- Complétés : 0 points
- Restants : 115 points

### Qualité
- Tests : 0% coverage
- Bugs : 0 ouverts
- Dettes techniques : 0

---

## 🚨 Risques & Mitigations

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Overlay complexe sur Sonoma | 🟡 Moyen | 🔴 Haut | Fallback : menu bar app |
| Coût LLM trop élevé | 🟡 Moyen | 🟡 Moyen | Cache + modèle léger |
| Performance Lua export | 🟢 Faible | 🟡 Moyen | Optimisation + throttling |
| Permissions macOS | 🟡 Moyen | 🟡 Moyen | Doc claire + assistant UI |

---

## 📝 Notes de mise à jour

**22 décembre 2025**
- Création du backlog initial
- Spécifications macOS ajoutées
- 14 US définies, 115 points estimés
- Roadmap 4 sprints planifiée

---

**Prochaine revue de backlog :** _À planifier après Sprint 0_
