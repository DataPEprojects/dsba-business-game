# RAPPORT TECHNIQUE - IMPLÉMENTATION SYSTÈME DE RÉSOLUTION DE TOURS
**Projet DSBA Business Game - Décembre 2025**

---

##  OBJECTIF GLOBAL

Implémenter un système complet de résolution de tours avec :
- 5 entreprises IA concurrentes avec comportements pré-définis
- Logique automatique de production (usines  stock)
- Algorithme de vente au prix le plus bas
- Système de classement et rapports détaillés

---

##  FICHIERS MODIFIÉS/CRÉÉS

### 1. `data/ai_behaviors.json`  **NOUVEAU FICHIER**

**Objectif** : Configuration des comportements de 5 entreprises IA sur 5 tours.

**Structure** :
```json
{
  "AI_Alpha": {
    "strategy": "Description de la stratégie",
    "turns": {
      "1": {
        "buy_factories": ["USA", "China"],
        "production_lines": {
          "USA": {"A": 10, "B": 5}
        },
        "sales_prices": {
          "USA": {"A": 18, "B": 78}
        }
      }
    }
  }
}
```

**5 Profils créés** :
- **AI_Alpha** : Spécialiste USA, volume élevé produit A
- **AI_Beta** : Approche équilibrée multi-pays
- **AI_Gamma** : Production low-cost en Chine
- **AI_Delta** : Premium France, focus produits B et C
- **AI_Epsilon** : Stratégie agressive de dumping

**Données** : ~200 lignes de configuration stratégique

---

### 2. `engine/world.py`  **RÉÉCRITURE COMPLÈTE**

#### **Modifications dans `__init__()`** :
```python
def __init__(self):
    self.parameters = Parameters()
    self.turn = 1
    self.ai_behaviors = self._load_ai_behaviors()      #  AJOUT
    self.companies = self._initialize_companies()       #  AJOUT
    self.sales_history = []                             #  AJOUT
```

#### **Nouvelles méthodes créées** :

##### `_load_ai_behaviors()` 
- Charge le fichier JSON des comportements IA
- Gestion encodage UTF-8-sig (BOM)

##### `_initialize_companies()`
- Crée 1 joueur humain + 5 IA
- Initialise les stocks pour tous les produits

##### `_apply_ai_actions(turn_number)`
**Rôle** : Exécute automatiquement les actions pré-enregistrées des IA
- Achat d'usines (vérification cash disponible)
- Allocation des lignes de production
- Définition des prix de vente par marché

##### `_calculate_production()`
**Formule** : `Production = Lignes  100  Efficacité_Pays`
- Parcourt toutes les usines de chaque entreprise
- Ajoute la production au stock

##### `_apply_maintenance_costs()`
- Calcule la maintenance totale par entreprise
- Déduit du cash
- Enregistre dans `company.costs["maintenance"]`

##### `_resolve_sales()`  **ALGORITHME COMPLEXE**
**Logique de vente** :
1. Pour chaque couple (pays, produit) :
   - Récupère la `base_demand` depuis le JSON
   - Collecte toutes les offres (entreprise, prix, stock disponible)
   
2. Tri des offres par prix croissant

3. Algorithme de vente :
   ```python
   while (demand restante > 0) AND (offres disponibles) :
       prix_min = offre la moins chère
       vendeurs_au_prix_min = tous les vendeurs à ce prix
       
       # Vente alternée (équité à prix égal)
       for vendeur in vendeurs_au_prix_min:
           vendre 1 unité
           mettre à jour stock et cash
           enregistrer dans sales_history
   ```

4. **Tracking détaillé** : Chaque vente enregistre :
   - Pays, produit
   - Entreprise vendeuse
   - Prix et quantité
   - Flag `is_player` pour identifier le joueur

##### `get_ranking()`
- Trie les 6 entreprises par cash décroissant
- Retourne : rang, nom, cash, is_player

##### `resolve_turn()` - **ORCHESTRATION**
```python
def resolve_turn(self):
    self.turn += 1
    
    self._apply_ai_actions(self.turn)      # 1. Actions IA
    self._calculate_production()           # 2. Production  Stock
    self._apply_maintenance_costs()        # 3. Coûts maintenance
    self._resolve_sales()                  # 4. Résolution ventes
    
    # 5. Reset indicateurs pour tour suivant
    for company in self.companies:
        company.reset_all_past_inf()
```

**Lignes de code** : ~180 lignes ajoutées, ~30 modifiées

---

### 3. `main.py` - **MODIFICATIONS BACKEND**

#### **Route `/market`** - Modification
```python
# AJOUT
countries_data=current_params["countries"]  # Pour base_demand

# RETRAIT
marketing_meta=current_params["marketing_meta"]  # Non utilisé en V0
```

#### **Route `/overview`** - Réécriture complète
**Avant** : Affichage basique sans données

**Après** : Préparation tableau à double entrée
```python
@app.route("/overview")
def view_overview():
    player = get_player()
    ranking = world.get_ranking()
    
    # Agrégation des ventes par (pays, produit)
    sales_matrix = {}
    for sale in world.sales_history:
        key = (sale["country"], sale["product"])
        if key not in sales_matrix:
            sales_matrix[key] = {
                "country": sale["country"],
                "product": sale["product"],
                "base_demand": ...,
                "sales": {}  # {company_name: quantity}
            }
        sales_matrix[key]["sales"][sale["company_name"]] += sale["quantity"]
    
    sales_table = list(sales_matrix.values())
    all_companies = [c.name for c in world.companies]
    
    return render_template(..., sales_table, all_companies)
```

**Impact** : Transformation de centaines de lignes en tableau compact (pays-produit  joueurs)

---

### 4. `templates/market.html` - **SIMPLIFICATION INTERFACE**

#### **Changement 1 : Retrait du marketing**
```html
<!-- AVANT : 2 selects -->
<select>Prix</select>
<select>Marketing</select>

<!-- APRÈS : 1 select -->
<select>Selling Price</select>
```

#### **Changement 2 : Affichage Stock + Base Demand**
```html
<div style="display:flex; gap:10px;">
    <span style="background:#ebf5fb;">
         Stock: {{ player.stock.get(product, 0) }}
    </span>
    <span style="background:#fef5e7;">
         Max Demand: {{ base_demand }}
    </span>
</div>
```

#### **Changement 3 : Correction variables Jinja2**
- Bug : `get(''price'', 0)`  doubles quotes
- Fix : `get('price', 0)`  simples quotes

#### **Changement 4 : Source des données**
```html
<!-- AVANT (incorrect) -->
{% set base_demand = meta.base_demand %}

<!-- APRÈS (correct) -->
{% set base_demand = countries_data[market_country]["products"][product]["base_demand"] %}
```

---

### 5. `templates/turn_overview.html` - **NOUVEAUX RAPPORTS**

#### **Ajout 1 : Styles CSS**
```css
.ranking-table { /* Tableau propre avec box-shadow */ }
.rank-badge { /* Badges circulaires pour les rangs */ }
.rank-1 { background: #f39c12; }  /*  Or */
.rank-2 { background: #95a5a6; }  /*  Argent */
.rank-3 { background: #cd7f32; }  /*  Bronze */
.player-row { background: #e8f8f5; font-weight: 600; }  /* Ligne joueur */
```

#### **Ajout 2 : Tableau à double entrée des ventes**

**Structure** :
| Market - Product | Player | AI_Alpha | AI_Beta | AI_Gamma | AI_Delta | AI_Epsilon |
|------------------|--------|----------|---------|----------|----------|------------|
| USA - Product A (20000) | **1500** | **3200** | - | **5000** | - | **2100** |
| France - Product B (5000) | **200** | - | **800** | - | **1200** | **150** |

**Code Jinja2** :
```html
<table>
    <thead>
        <tr>
            <th>Market - Product</th>
            {% for company in all_companies %}
            <th>{{ company }}</th>
            {% endfor %}
        </tr>
    </thead>
    <tbody>
        {% for row in sales_table %}
        <tr>
            <td>
                {{ row.country }} - Product {{ row.product }}
                <br>(Max demand: {{ row.base_demand }})
            </td>
            {% for company in all_companies %}
            <td style="{% if company == 'Player' %}background: #e8f8f5;{% endif %}">
                {% if row.sales.get(company, 0) > 0 %}
                    <strong>{{ row.sales[company] }}</strong>
                {% else %}
                    <span>-</span>
                {% endif %}
            </td>
            {% endfor %}
        </tr>
        {% endfor %}
    </tbody>
</table>
```

#### **Ajout 3 : Tableau du classement**
```html
<table class="ranking-table">
    {% for entry in ranking %}
    <tr {% if entry.is_player %}class="player-row"{% endif %}>
        <td>
            <span class="rank-badge rank-{{ entry.rank }}">
                {{ entry.rank }}
            </span>
        </td>
        <td>{{ entry.name }}</td>
        <td>${{ "{:,.0f}".format(entry.cash) }}</td>
    </tr>
    {% endfor %}
</table>
```

---

##  BUGS CORRIGÉS

### **Bug 1 : JSONDecodeError - UTF-8 BOM**
**Erreur** : `Unexpected UTF-8 BOM (decode using utf-8-sig)`

**Cause** : PowerShell ajoute un BOM en UTF-8

**Solution** :
```python
# world.py, ligne 23
with open("data/ai_behaviors.json", "r", encoding="utf-8-sig") as f:
```

### **Bug 2 : TemplateSyntaxError - Doubles quotes**
**Erreur** : `expected token ',', got 'price'`

**Cause** : Échappement automatique PowerShell  `''price''`

**Solution** : Réécriture manuelle avec quotes simples

### **Bug 3 : Tour initial incohérent**
**Problème** : `self.turn = 0` mais affichage "Turn 1"

**Solution** : `self.turn = 1` dès l'initialisation

---

##  MÉTRIQUES

| Fichier | Lignes ajoutées | Lignes modifiées | Lignes supprimées |
|---------|----------------|------------------|-------------------|
| `ai_behaviors.json` | 200 | 0 | 0 |
| `engine/world.py` | 180 | 30 | 20 |
| `main.py` | 35 | 10 | 5 |
| `templates/market.html` | 20 | 30 | 40 |
| `templates/turn_overview.html` | 90 | 10 | 5 |
| **TOTAL** | **525** | **80** | **70** |

**Temps de développement** : ~3 heures  
**Complexité** : Moyenne-Élevée (algorithme de vente)

---

##  FONCTIONNALITÉS LIVRÉES

 **5 entreprises IA** avec stratégies diversifiées sur 5 tours  
 **Production automatique** : calcul et ajout au stock  
 **Algorithme de vente** au prix le plus bas avec équité  
 **Déduction maintenance** automatique  
 **Tracking ventes** (qui, quoi, où, combien, prix)  
 **Classement temps réel** avec badges Or/Argent/Bronze  
 **Tableau à double entrée** : lisibilité optimale  
 **Affichage stocks** dans interface Sales Market  
 **Interface simplifiée** : focus prix (marketing retiré)  

---

##  FLUX D'EXÉCUTION

```

 TOUR N - Joueur fait ses choix     
 (usines, lignes, prix)              

               
               

 Clic "EXECUTE TURN N"               

               
               

 resolve_turn() appelé               
                                     
 1  _apply_ai_actions()            
     IA achètent usines/lignes      
     IA définissent prix            
                                     
 2  _calculate_production()        
     Lignes  100  Efficacité      
     Stock mis à jour               
                                     
 3  _apply_maintenance_costs()     
     Cash déduit                    
                                     
 4  _resolve_sales()                
     Algorithme prix le plus bas    
     Ventes enregistrées            
     sales_history alimenté         

               
               

 Redirection vers /factories         
 Tour N+1 commence                   

               
               

 Joueur visite /overview             
                                     
 Affichage :                         
 - Classement 6 entreprises          
 - Tableau ventes (paysjoueurs)     

```

---

##  TESTS RECOMMANDÉS

### Test 1 : Comportement IA
- Vérifier achats d'usines tour par tour
- Contrôler allocation lignes selon `ai_behaviors.json`
- Valider prix définis automatiquement

### Test 2 : Algorithme de vente
- Cas 1 : Prix différents  le moins cher vend tout
- Cas 2 : Prix égaux  vente alternée 1 par 1
- Cas 3 : Stock insuffisant  saturation

### Test 3 : Cohérence comptable
- Cash initial = 100 000 pour tous
- Cash après tour = Initial - Achats - Maintenance + Ventes
- Stocks = Production cumulée - Ventes

### Test 4 : Interface
- Modifier `turn_1.json`  redémarrer  vérifier affichage
- Hard refresh (Ctrl+Shift+R) si cache navigateur
- Vérifier colonne "Player" surlignée en vert

---

##  DÉPENDANCES

**Python** :
- Flask (routes web)
- json (chargement configurations)
- uuid (IDs uniques usines)

**Frontend** :
- Jinja2 (templating)
- JavaScript vanilla (AJAX prix)
- CSS inline (styles rapides)

**Fichiers de configuration** :
- `data/parameters/turn_X.json` : Paramètres économiques par tour
- `data/ai_behaviors.json` : Stratégies pré-enregistrées IA

---

##  AMÉLIORATIONS FUTURES

**V2 potentielles** :
- Coûts de production (actuellement gratuit)
- Transport et taxes (matrices présentes mais non utilisées)
- Marketing avec bonus intégration
- Stocks cumulatifs entre tours
- Logs détaillés par entreprise
- Export résultats en CSV

---

##  CRÉDITS

**Développement** : Julie  
**Date** : Décembre 2025  
**Framework** : Flask + Jinja2  
**Projet** : DSBA Business Game  

---

*Document généré automatiquement - Version 1.0*
