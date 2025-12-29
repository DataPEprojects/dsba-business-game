# Market_py_project - Business Strategy Game (V1)

## Overview
This is the **second functional version (V1)** of a turn-based business strategy game where players compete against AI opponents to manage factories, production, and sales across different countries. This version builds upon V0 by introducing AI competition, dynamic market generation, and a complete multi-turn gameplay experience.

## Work in progress
- **Work in progress**: This V1 branch is still evolving.
- **Transitional version**: We are progressively moving away from static JSON toward fully dynamic generation to simplify structure and make each game unique.
- **AI data source (this branch)**: AI strategies are **hardcoded in** `data/ai_behaviors.json` (turn-by-turn presets). There is **no `AI_manager.py`** in this branch.
- **Game over**: No dedicated game-over screen yet. The engine supports a turn limit, but the UI does not display an end-of-game state.

## Important Rule (V1)
- **Sales logic**: Each product can be sold in exactly **one country per turn**. Splitting a product’s sales across multiple countries is not allowed.

## Project Status - V1
**What Works:**
- ✅ **AI Opponents System** - 5 configurable AI opponents with distinct personalities
- ✅ **Dynamic Market Generation** - Procedurally generated turn parameters with economic cycles
- ✅ **Multi-Turn Gameplay** - Full game progression from Turn 1 to Turn 10 (configurable)
- ✅ **Complete Turn Resolution** - Production, sales, maintenance, and competition mechanics
- ✅ **Sales Competition Logic** - Price-based market resolution with demand constraints
- ✅ **Turn Overview & Ranking** - Detailed results page with company rankings and sales breakdowns
- ✅ **AJAX-powered UI** - Smooth, interactive production and sales management

**What's New in V1 vs V0:**
- **AI opponents via JSON presets** in `data/ai_behaviors.json` (predefined strategies per turn)
- **Dynamic market generator** replacing most static parameter JSON (transitional phase)
- **Economic events system** with growth, recession, boom, and recovery phases
- **Working turn progression** - players can complete multiple turns
- **Sales resolution engine** - competitive marketplace with price-based allocation
- **Company ranking system** - track performance against AI competitors
- **Turn overview page** - detailed sales history and financial breakdown

## Architecture

### Core Structure
The project follows a **modular, object-oriented architecture** separating game logic, entities, and presentation:
### Core Structure
The project follows a **modular, object-oriented architecture** separating game logic, entities, and presentation:

```
Market_py_project/
├── main.py                      # Flask application & routing
├── engine/                      # Game logic & mechanics
│   ├── parameters.py           # Dynamic parameter generator wrapper
│   ├── market_generator.py     # Procedural market/demand generator
│   ├── world.py                # Game coordinator & turn resolution
│   └── events.py               # Events system (placeholder)
├── entities/                    # Game object classes
│   ├── company.py              # Company/player management
│   ├── factory.py              # Factory mechanics & config
│   └── product.py              # Product configuration
├── data/
│   └── ai_behaviors.json       # AI behavior presets (optional)
├── templates/                   # HTML pages
│   ├── factories.html          # Factory management page
│   ├── production.html         # Production allocation page (AJAX-enabled)
│   ├── market.html             # Sales & pricing page (AJAX-enabled)
│   └── turn_overview.html      # Turn results & rankings
└── static/
    └── style.css               # Styling
```

### AI Data Source (This Branch)
- **JSON presets only**: `data/ai_behaviors.json` contains hardcoded, turn-by-turn AI strategies (deterministic for testing and demos).
- Note: We are gradually moving toward fully generated AI in future branches, but **not in this branch**.

### Design Philosophy

#### 1. **Engine vs Entities Separation**
- **`engine/`**: Contains game mechanics, rules, and procedural generation
  - `parameters.py`: Wrapper that uses MarketGenerator to provide turn data
  - `market_generator.py`: **NEW in V1** - Procedurally generates market conditions with economic cycles
  - `world.py`: Coordinates game simulation, manages AI actions, and resolves turns
  - `AI_manager.py`: **NEW in V1** - Creates and manages AI opponents with different strategies
  - `events.py`: Reserved for future random events (currently empty)

- **`entities/`**: Contains pure object classes representing game elements
  - `company.py`: Player/company state (cash, factories, inventory, sales decisions)
  - `factory.py`: Factory objects with country-specific costs, efficiency, and capacity
  - `product.py`: Product definitions and configuration

This separation keeps business logic distinct from data structures, making the codebase more maintainable and testable.

#### 2. **Dynamic Market Generation (V1 Innovation)**
**Major change from V0:** Instead of static JSON files, V1 uses **`MarketGenerator`** to procedurally create market conditions:

**Economic Cycle Phases:**
- **Stability (Turns 1-2)**: Steady baseline conditions for early game
- **Growth (Turns 3-60% of game)**: Expanding demand with random boom/dip events
- **Recession (60-80% of game)**: Significant demand contraction (0.65-0.85x multiplier)
- **Recovery (80-100% of game)**: Gradual market recovery

**What's Generated Per Turn:**
- Product pricing ranges (adjusted by economic multiplier)
- Country-specific demand levels (with random variation ±5%)
- Economic event indicators (Boom, Dip, Recession, Recovery, Growth)
- Transport cost matrix (fixed percentages between countries)
- Tax matrix for international trade

This creates **dynamic, unpredictable markets** that require strategic adaptation, unlike V0's static configurations.

#### 3. **Flask Web Interface with AJAX**
The web interface has been **enhanced in V1** with asynchronous updates:
- **`main.py`**: Contains all routes, including new AJAX endpoints
- **AJAX-enabled pages**: Production and Market pages update without full page reloads
- **Turn Overview page**: **NEW** - displays detailed results, rankings, and sales breakdowns
- **`templates/`**: HTML pages for each game screen
- **`static/style.css`**: Shared styling

The AJAX improvements make the interface **more responsive** when managing production lines and sales decisions.

## Game Mechanics (V1)

### Player vs AI Competition
**V1 introduces competitive gameplay** against 5 AI opponents, each with distinct strategies:

**AI Personality Types:**
1. **Aggressive** - High expansion rate (85%), focuses on low-priced Product A, prefers China/USA
2. **Balanced** - Moderate expansion (50%), diversified product mix, operates in all countries
3. **Conservative** - Low expansion (30%), focuses on high-margin Product C, prefers France
4. **Premium** - Focused on Product C (70%), high pricing strategy, targets USA/France
5. **Volume** - Maximum expansion (95%), ultra-low pricing, mass production of Product A in China

AI opponents make autonomous decisions each turn:
- Factory purchases based on expansion probability
- Production line allocation based on product focus
- Pricing decisions aligned with their strategy (very_low to premium)
- Market selection based on preferred countries

### Player Actions Per Turn

#### 1. **Factory Management** (`/factories`)
- Purchase factories in USA, China, or France
- Each country has different setup costs:
  - USA: $40,000 (high efficiency 1.5x, expensive maintenance $400/line)
  - China: $25,000 (lower efficiency 0.9x, cheap maintenance $100/line)
  - France: $30,000 (balanced efficiency 1.2x, moderate maintenance $300/line)
- Each factory has 20 production line capacity
- **Strategic consideration**: Country choice affects both initial investment and ongoing costs

#### 2. **Production Planning** (`/production`)
- Allocate production lines across products (A, B, C) in each factory
- Each line produces 100 base units per turn × country efficiency multiplier
- **AJAX-enabled interface**: Add/remove lines without page reload
- Production output:
  - USA factory with 10 lines on Product A → 1,500 units (10 × 100 × 1.5)
  - China factory with 10 lines on Product A → 900 units (10 × 100 × 0.9)
- Maintenance costs scale with active production lines
#### 3. **Market & Sales** (`/market`)
- **NEW V1 Decision Structure**: Each product can only be sold in ONE country per turn
- Set selling price for each product (A, B, C) from dynamically generated price ranges
- Choose target market (France, USA, or China) for each product
- **AJAX-enabled interface**: Decisions save automatically
- Prices and demand affected by economic cycle (visible on page via event indicator)
- Markets have different demand levels:
  - Product A: High-volume, low-margin (base price ~$18)
  - Product B: Medium-volume, medium-margin (base price ~$100)
  - Product C: Low-volume, high-margin (base price ~$230)

#### 4. **Turn Resolution & Competition**
When you click **"End Turn"**:

1. **AI Actions Phase**
   - All AI opponents make their factory, production, and sales decisions
   - AI strategies play out simultaneously

2. **Production Phase**
   - All companies (player + AIs) produce goods based on production line allocation
   - Products added to inventory

3. **Maintenance Costs**
   - All companies pay maintenance for active production lines
   - Costs deducted from cash reserves

4. **Sales Resolution Phase** (Competitive Market Logic)
   - For each country and product, the game aggregates all offers
   - **Lowest price wins**: Companies offering the lowest price sell first
   - If multiple companies have the same low price, they share demand
   - Sales continue at higher prices if demand remains
   - Companies earn revenue only for units actually sold
   - Unsold inventory carries over to next turn

5. **Turn Advancement**
   - Rankings updated based on cash
   - Turn counter increments
   - New market conditions generated for next turn

#### 5. **Turn Overview** (`/overview`)
**NEW in V1** - Comprehensive results page showing:
- **Company Rankings**: All companies ranked by cash (player highlighted)
- **Sales Breakdown**: Detailed table showing:
  - Which companies sold in which markets
  - Quantities sold per country/product combination
  - Base demand vs actual sales
- **Player Financial Summary**: Revenue, costs, and profit for the turn
- **Historical Context**: See how you performed against AI competitors

### Game Flow (V1)
1. Player starts with $100,000 cash
2. **Turn 1**: Buy initial factories, allocate production, set prices
3. Submit turn → AI opponents act simultaneously
4. View turn overview to see sales results and rankings
5. **Adapt strategy** based on:
   - AI competitor pricing
   - Economic events (boom, recession, etc.)
   - Your market position in rankings
6. Repeat for 10 turns (or configured total)
7. **Winner**: Company with highest cash at end of game

### Strategic Depth (V1 Additions)

**Pricing Strategy:**
- Price too high → AI undercuts you, you don't sell
- Price too low → You sell but sacrifice profit margins
- Must balance competitiveness with profitability

**Market Selection:**
- High-demand markets (USA) attract more competition
- Smaller markets (France for Product C) may have less competition
- Transportation costs (future feature) will matter

**Production Planning:**
- Over-produce → Inventory buildup, wasted maintenance costs
- Under-produce → Lost sales opportunities
- Must forecast demand considering economic cycles

**Economic Adaptation:**
- Recession phases → Reduce production, focus on efficiency
- Boom phases → Expand capacity, capture growing demand
- Recovery phases → Strategic expansion before full recovery

## Technical Details (V1)

### Key Classes

**`World`** (engine/world.py)
- **V1 Enhancement**: Manages AI opponents and competitive turn resolution
- Initializes with configurable turn count (default: 10 turns)
- Loads AI strategies from `data/ai_behaviors.json` and creates all company instances (player + AIs)
- Orchestrates complete turn resolution:
  - `_apply_ai_actions(turn)` - Applies predefined AI actions for the current turn
  - `_calculate_production()` - All companies produce goods
  - `_apply_maintenance_costs()` - Deduct factory maintenance
  - `_resolve_sales()` - Price-based competitive market resolution
- Tracks `sales_history` for turn overview page
- Provides `get_ranking()` to rank companies by cash

**`Company`** (entities/company.py)
- **V1 Enhancement**: Simplified sales decision structure
- Now supports `ai_behavior` attribute for AI-controlled companies
- Sales decisions changed from per-country-per-product to per-product only:
  - `sales_decisions[product] = {"country": "...", "price": 0}`
  - Each product sold in exactly one country per turn
- Methods:
  - `get_decision(product)` - Get or initialize decision for a product
  - `set_decision(product, field, value)` - Set country or price for a product
  - `ensure_all_products(products)` - Initialize stock for dynamic products
  - `reset_all_past_inf()` - Reset turn-specific metrics (revenue, costs)

**`Factories`** (entities/factory.py)
- **V1 Update**: Adjusted costs to match new game balance
- Country-specific configuration defines:
  - `base_line_cost` - Cost per production line
  - `efficiency_multiplier` - Production output multiplier
  - `max_capacity` - Maximum production lines (20)
  - `maintenance_cost` - Cost per active line per turn
- Methods:
  - `modify_lines(product, qty)` - Add/remove production lines with validation
  - Properties: `total_lines_used`, `free_space`, `maintenance_cost`

**`Parameters`** (engine/parameters.py)
- **V1 Complete Rewrite**: No longer loads JSON files
- Wraps `MarketGenerator` to provide procedural turn data
- Caches generated turn data to ensure consistency
- Method: `get_turn(turn_number)` returns full turn configuration

**`MarketGenerator`** (engine/market_generator.py) - **NEW in V1**
- Core innovation of V1 - procedural market generation
- Initialized with `total_turns` to plan economic cycles
- `get_turn_data(turn)` generates:
  - Economic multiplier and event type based on turn phase
  - Product price ranges (base price × economic multiplier ± spread)
  - Country-specific demand (base × multiplier × random variation)
  - Transport and tax matrices
- `_get_climate(turn)` determines economic phase:
  - Early stability, growth with random events, recession, recovery
  - Random boom/dip events during growth phase (30% boom, 20% dip chance)

**AI (from JSON)**
- AI behavior is **scripted via JSON** (`data/ai_behaviors.json`):
  - Per-turn: factory purchases, production line targets, sales decisions (country + price)
  - Deterministic: useful for testing and replicable demos
  - Named AIs (AI_Alpha, AI_Beta, etc.) reflect different high-level strategies defined in JSON

### Data Flow (V1)
1. Player interacts with HTML forms / AJAX requests
2. Flask routes handle submissions and update player's `Company` object
3. Player clicks "End Turn"
4. `world.resolve_turn()` executes:
   - AI companies make autonomous decisions via `AIBehavior`
   - Production calculated for all companies
   - Maintenance costs applied
   - **Sales resolution**: Competitive market with price-based allocation
   - Rankings updated
   - Turn counter incremented
5. Turn overview page displays detailed results
6. New turn begins with fresh market conditions from `MarketGenerator`

### Sales Resolution Algorithm (V1 Core Logic)
```python
For each product:
  Collect all offers (company, country, price, stock)
  Group offers by country
  
  For each country:
    Sort offers by price (lowest first)
    remaining_demand = base_demand
    
    While demand remains and offers exist:
      Find all sellers at minimum price
      For each seller at min price:
        Sell min(1, seller_stock, remaining_demand) units
        Deduct from seller stock
        Add revenue to seller cash
        Record sale in history
        Reduce remaining_demand
      
      Remove sold-out sellers
```

This ensures **competitive price-based allocation** - lowest prices always sell first, higher prices only sell if demand exceeds low-price supply.

## Evolution from V0 to V1

### What Changed

#### 1. **From Single-Player to Competitive**
- **V0**: Solo experience with no competition
- **V1**: 5 AI opponents with distinct strategies create competitive dynamics

#### 2. **From Static to Dynamic Markets**
- **V0**: Hardcoded JSON files with fixed market parameters
- **V1**: Procedural `MarketGenerator` with economic cycles and random events

#### 3. **From Test Environment to Full Game**
- **V0**: Could only test Turn 1 mechanics
- **V1**: Complete 10-turn game with progression, rankings, and end-game

#### 4. **From Simple to Strategic**
- **V0**: Make decisions, see basic results
- **V1**: Compete on price, adapt to economic changes, track competitive position

#### 5. **Sales Decision Structure**
- **V0**: `sales_decisions[Country][Product] = {"price": 0, "marketing": 0}`
- **V1**: `sales_decisions[Product] = {"country": "", "price": 0}` (one country per product)

#### 6. **Turn Resolution**
- **V0**: Incomplete, no actual market resolution
- **V1**: Full competitive resolution with price-based sales allocation

#### 7. **User Interface**
- **V0**: Basic forms with full page reloads
- **V1**: AJAX-enabled for production and sales (smoother UX)

#### 8. **Factory Costs**
- **V0**: Lower costs (USA $10k, China $5k, France $8k)
- **V1**: Balanced costs (USA $40k, China $25k, France $30k)

### What Stayed the Same
- Core architecture (engine/entities separation)
- Flask web framework
- Three-country system (USA, China, France)
- Three-product system (A, B, C)
- Factory capacity (20 lines)
- Production output (100 units/line × efficiency)

### Development Lessons V0 → V1

**V0 Achievement:**
- Validated web interface approach over terminal scripts
- Established modular architecture that scaled well
- Created foundation for entity classes

**V1 Challenges:**
- Designing fair AI behaviors that provide challenge without being unbeatable
- Implementing price-based sales resolution algorithm
- Balancing economic cycle parameters for interesting gameplay
- Managing state complexity with multiple simultaneous actors

**V1 Success:**
- AI system is modular and extensible (easy to add new personalities)
- MarketGenerator creates varied, engaging economic scenarios
- Turn resolution is deterministic and fair
- Competitive gameplay emerges naturally from pricing mechanics

## Why V1 Took Additional Development

### Web Development Learning Curve
The team had **no prior web development experience**, which made this version a significant learning process:
- Understanding Flask routing and templating
- Managing state between page requests
- Form handling and data validation
- CSS layout and responsive design

### New Systems Built
1. **AI Manager & Behaviors** (~300 lines) - Complete autonomous opponent system
2. **Market Generator** (~100 lines) - Procedural content generation with economic modeling
3. **Sales Resolution Engine** (~100 lines in World) - Complex competitive allocation logic
4. **Turn Overview Page** - New comprehensive results display
5. **AJAX Integration** - Client-side state management and async updates

### Complexity Increase
- **State Management**: Tracking 6 companies (player + 5 AI) vs 1
- **Testing**: Balancing AI personalities to be challenging but fair
- **Game Balance**: Adjusting costs, prices, and demand to create interesting decisions
- **Market Logic**: Ensuring fair price-based allocation without exploits

### Achievement
V1 transforms the project from a **proof-of-concept** to a **playable competitive game**:
- ✅ Complete gameplay loop (multiple turns with AI competition)
- ✅ Strategic depth (pricing decisions matter against AI)
- ✅ Dynamic content (economic cycles create variety)
- ✅ Performance tracking (rankings and detailed results)
- ✅ Replayability (random market events make each game different)

## Running the Project (V1)

### Prerequisites
- Python 3.x
- Flask

### Installation
```bash
pip install flask
```

### Launch
```bash
python main.py

The game initializes with:
- **10 turns** (configurable in `main.py`: `World(total_turns=10)`)
- **5 AI opponents** with different personalities
- Player starting with **$100,000**
```

Then navigate to `http://localhost:5000` in your browser.

### How to Play
1. **Turn 1**: Buy at least one factory, allocate production lines, set prices
2. Click **"End Turn"** to resolve
3. View **Turn Overview** to see:
  - Your sales performance
  - AI competitor actions
  - Updated rankings
4. Plan next turn based on:
  - Economic event indicator (Boom, Recession, etc.)
  - AI pricing from sales history
  - Your cash position vs competitors
5. Repeat until Turn 10
6. **Winner**: Highest cash at game end

## Next Steps (Future Versions)

### Planned Features
- **Transport costs**: Active cost for shipping between countries
- **Tax system**: Tariffs on international sales
- **Marketing budget**: Influence demand with advertising spend
- **Random events**: Market crashes, country-specific events, product recalls
- **Advanced AI**: Heuristic opponents
- **Multiplayer**: Human vs human competition
- **Save/Load**: Persistent game state
- **Analytics**: Charts showing performance over time

### Technical Improvements
- Separate business logic from Flask routes (service layer)
- Add unit tests for core game mechanics
- Database integration for game state persistence
- WebSocket for real-time updates
- Mobile-responsive UI

## Notes
- This is a **learning project** that evolved significantly from V0 to V1
- Focus was on creating **engaging competitive gameplay** with AI opponents
- The modular architecture proved successful - V1 additions fit cleanly into V0's structure
- **MarketGenerator** approach superior to static JSON - more flexible and maintainable
- AI system demonstrates that simple heuristic behaviors can create compelling challenge

---

**Version:** 1.0 (Competitive AI Edition)  
**Status:** Full multi-turn gameplay with AI opponents  
**Branch:** feature/V1_prof_commentee  
**Previous Version:** V0 (Single-player foundation) - branch: feature/V0_prof_commentee
