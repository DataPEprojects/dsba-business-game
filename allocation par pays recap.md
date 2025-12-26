# Récapitulatif : Nouvelle Logique de Vente par Produit

**Date de modification :** 26 décembre 2025

---

## 📋 Changement Principal

**AVANT :** Chaque produit pouvait être vendu dans plusieurs pays simultanément avec des prix différents par pays.

**MAINTENANT :** Chaque produit ne peut être vendu que dans **UN SEUL pays** par entreprise.

---

## 🔧 Fichiers Modifiés

### 1. **entities/company.py** - Structure de données simplifiée

#### AVANT
```python
# Structure : self.sales_decisions[Pays][Produit] = {"price": 0, "marketing": 0}
self.sales_decisions = {} 

def get_decision(self, country, product):
    if country not in self.sales_decisions:
        self.sales_decisions[country] = {}
    if product not in self.sales_decisions[country]:
        self.sales_decisions[country][product] = {"price": 0, "marketing": 0}
    return self.sales_decisions[country][product]

def set_decision(self, country, product, field, value):
    self.get_decision(country, product)
    self.sales_decisions[country][product][field] = value
```

#### APRÈS
```python
# NOUVELLE STRUCTURE : self.sales_decisions[Produit] = {"country": "...", "price": 0}
# Chaque produit ne peut être vendu que dans UN SEUL pays
self.sales_decisions = {} 

def get_decision(self, product):
    if product not in self.sales_decisions:
        self.sales_decisions[product] = {"country": "", "price": 0}
    return self.sales_decisions[product]

def set_decision(self, product, field, value):
    self.get_decision(product)
    self.sales_decisions[product][field] = value
```

**Impact :** Suppression de la dimension "pays" dans la clé principale. Chaque produit a maintenant un pays assigné comme attribut.

---

### 2. **templates/market.html** - Interface utilisateur repensée

#### AVANT
- Organisation par **pays** (une carte par pays)
- Chaque pays contient tous les produits avec leur prix
- Un produit apparaît dans plusieurs cartes de pays

#### APRÈS
- Organisation par **produit** (une carte par produit)
- Chaque produit a **2 menus déroulants** :
  1. **Pays de commercialisation** (Target Country)
  2. **Prix de vente** (Selling Price)
- Affichage dynamique de la demande du pays sélectionné
- Message d'avertissement sur la nouvelle règle

**Nouveaux éléments visuels :**
- Card header avec gradient violet pour chaque produit
- Badge de stock disponible
- Zone d'information sur la demande qui apparaît après sélection du pays
- Rechargement automatique de la page après changement de pays pour afficher les infos de demande

---

### 3. **main.py** - Endpoint AJAX mis à jour

#### AVANT
```python
@app.route('/update_sales_ajax', methods=['POST'])
def update_sales_ajax():
    data = request.json
    country = data.get('country')
    product = data.get('product')
    field = data.get('field')  # 'price' ou 'marketing'
    value = int(data.get('value'))
    
    # Structure : player.sales_decisions[country][product][field] = value
    if country not in player.sales_decisions:
        player.sales_decisions[country] = {}
    if product not in player.sales_decisions[country]:
        player.sales_decisions[country][product] = {"price": 0, "marketing": 0}
    
    player.sales_decisions[country][product][field] = value
    return jsonify({'status': 'saved', 'value': value})
```

#### APRÈS
```python
@app.route('/update_sales_ajax', methods=['POST'])
def update_sales_ajax():
    data = request.json
    product = data.get('product')
    field = data.get('field')  # 'country' ou 'price'
    value = data.get('value')
    
    # Validation spécifique pour le prix
    if field == 'price':
        value = int(value)
    
    # Structure : player.sales_decisions[product][field] = value
    player.set_decision(product, field, value)
    return jsonify({'status': 'saved', 'value': value})
```

**Changements :**
- Le paramètre `country` a été supprimé de la requête
- Le paramètre `product` est maintenant la clé principale
- Le champ `field` peut être `"country"` ou `"price"` (plus de `"marketing"`)
- Validation différenciée selon le type de champ (string pour pays, int pour prix)

---

### 4. **engine/world.py** - Logique de résolution adaptée

#### Section 1 : Application des actions IA

**AVANT**
```python
# 3. Définir les prix de vente
for country, products in turn_data["sales_prices"].items():
    for product, price in products.items():
        company.set_decision(country, product, "price", price)
```

**APRÈS**
```python
# 3. Définir les décisions de vente (pays + prix)
sales = turn_data.get("sales", {})
for product, decision in sales.items():
    country = decision.get("country", "")
    price = decision.get("price", 0)
    if country:
        company.set_decision(product, "country", country)
    if price > 0:
        company.set_decision(product, "price", price)
```

#### Section 2 : Résolution des ventes (`_resolve_sales`)

**AVANT**
```python
def _resolve_sales(self):
    # Pour chaque marché (pays) et produit
    for country in params["countries"].keys():
        for product in params["products_meta"].keys():
            base_demand = params["countries"][country]["products"].get(product, {}).get("base_demand", 0)
            
            # Collecter les offres pour ce couple (pays, produit)
            offers = []
            for company in self.companies:
                decision = company.get_decision(country, product)
                price = decision.get("price", 0)
                stock = company.stock.get(product, 0)
                
                if price > 0 and stock > 0:
                    offers.append({"company": company, "price": price, "stock": stock})
            
            # ... Résolution des ventes ...
```

**APRÈS**
```python
def _resolve_sales(self):
    # Pour chaque produit
    for product in params["products_meta"].keys():
        
        # Collecter toutes les offres pour ce produit
        offers = []
        for company in self.companies:
            decision = company.get_decision(product)
            country = decision.get("country", "")
            price = decision.get("price", 0)
            stock = company.stock.get(product, 0)
            
            # Le produit doit avoir un pays assigné, un prix > 0 et du stock
            if country and price > 0 and stock > 0:
                if country in params["countries"]:
                    base_demand = params["countries"][country]["products"].get(product, {}).get("base_demand", 0)
                    if base_demand > 0:
                        offers.append({
                            "company": company,
                            "country": country,
                            "price": price,
                            "stock": stock,
                            "base_demand": base_demand
                        })
        
        # Grouper les offres par pays
        offers_by_country = {}
        for offer in offers:
            country = offer["country"]
            if country not in offers_by_country:
                offers_by_country[country] = []
            offers_by_country[country].append(offer)
        
        # Pour chaque pays où le produit est commercialisé
        for country, country_offers in offers_by_country.items():
            # ... Résolution des ventes pour ce pays ...
```

**Logique clé :**
1. On parcourt d'abord les **produits** (au lieu de pays × produits)
2. On trouve le **pays assigné** pour chaque entreprise pour ce produit
3. On groupe les offres par pays (plusieurs entreprises peuvent vendre le même produit dans différents pays)
4. On résout les ventes **pays par pays** avec l'algorithme du prix le plus bas inchangé

---

### 5. **data/ai_behaviors.json** - Format des décisions IA

#### AVANT
```json
"sales_prices": {
    "USA": {"A": 18, "B": 78},
    "France": {"A": 19},
    "China": {"A": 19}
}
```
*Problème : Un produit peut avoir plusieurs prix dans plusieurs pays*

#### APRÈS
```json
"sales": {
    "A": {"country": "USA", "price": 18},
    "B": {"country": "USA", "price": 78}
}
```
*Chaque produit est associé à UN SEUL pays*

**Exemple complet (AI_Alpha, turn 1) :**
```json
{
  "buy_factories": ["USA"],
  "production_lines": {
    "USA": {"A": 10, "B": 5}
  },
  "sales": {
    "A": {"country": "USA", "price": 18},
    "B": {"country": "USA", "price": 78}
  }
}
```

---

## 📊 Impact sur la Résolution des Tours

### Algorithme de vente (inchangé dans son principe)

L'algorithme du **prix le plus bas** reste identique :
1. Tri des vendeurs par prix croissant
2. Vente alternée pour les vendeurs au même prix
3. Vente par unité jusqu'à épuisement de la demande ou du stock

### Ce qui change

**Avant :**
- On résolvait les ventes pour chaque couple `(pays, produit)`
- Exemple : Produit A aux USA, Produit A en France, Produit A en Chine → 3 résolutions indépendantes pour le même produit

**Maintenant :**
- On résout les ventes par **produit**
- On groupe ensuite par pays les entreprises qui vendent ce produit
- Exemple : Produit A → Entreprise 1 vend aux USA, Entreprise 2 vend en France → 2 résolutions (une par pays)

**Conséquence :** Une entreprise ne peut plus "tester" plusieurs marchés simultanément avec le même produit. Elle doit **choisir stratégiquement** son marché cible.

---

## 🎯 Implications Stratégiques

### Pour le joueur
- ✅ **Simplification** : Moins de décisions à prendre (1 pays par produit au lieu de N pays)
- ⚠️ **Choix stratégique** : Doit identifier le meilleur marché pour chaque produit
- 📊 **Analyse requise** : Doit comparer la demande et la concurrence entre pays

### Pour la simulation
- ✅ **Réalisme** : Une entreprise ne peut pas être présente partout simultanément
- ✅ **Concentration** : Encourage la spécialisation géographique
- ⚠️ **Risque** : Si toutes les entreprises choisissent le même pays pour un produit, la concurrence y est féroce

---

## ✅ Tests Recommandés

1. **Interface** : Vérifier que les 2 dropdowns (pays + prix) s'affichent pour chaque produit
2. **Sauvegarde** : Vérifier que les choix sont bien enregistrés (bordure verte)
3. **Affichage demande** : Vérifier que les infos de demande apparaissent après sélection du pays
4. **Résolution** : Lancer un tour complet et vérifier que les ventes sont correctement résolues
5. **IA** : Vérifier que les IA prennent bien leurs décisions selon le nouveau format

---

## 📝 Notes Techniques

- **Rétrocompatibilité** : ❌ Les anciennes sauvegardes utilisant `sales_decisions[pays][produit]` ne fonctionneront plus
- **Migration** : Si des sauvegardes existent, elles devront être converties vers le nouveau format
- **Validation** : Le système accepte maintenant des strings (pays) et des int (prix) dans l'endpoint AJAX

---

**Dernière mise à jour :** 26 décembre 2025 par GitHub Copilot