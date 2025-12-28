# Market_py_project - Business Strategy Game (V0)

## Overview
This is the **first functional version (V0)** of a turn-based business strategy game where players manage factories, production, and sales across different countries. This version focuses on establishing the core architecture and basic gameplay mechanics for a single player without AI opponents.

## Project Status - V0
**What Works:**
- Basic game architecture with modular design
- Single player functionality (no AI opponents yet)
- Factory purchasing and management across 3 countries (USA, China, France)
- Production line allocation system
- Market interaction with pricing and sales decisions
- Turn-based progression
- Web-based user interface

**Not Yet Implemented:**
- AI opponents
- Game events system
- Turn progression beyond Turn 1 testing
- Advanced market dynamics

## Architecture

### Core Structure
The project follows a **modular, object-oriented architecture** separating game logic, entities, and presentation:

```
Market_py_project/
├── main.py                      # Flask application & routing
├── engine/                      # Game logic & mechanics
│   ├── parameters.py           # JSON configuration loader
│   ├── world.py                # Main game coordinator
│   └── events.py               # Events system (placeholder)
├── entities/                    # Game object classes
│   ├── company.py              # Company/player management
│   ├── factory.py              # Factory mechanics & config
│   └── product.py              # Product configuration
├── data/
│   └── parameters/             # Turn configuration files
│       ├── turn_1.json         # Market data, prices, demand
│       └── turn_2.json
├── templates/                   # HTML pages
│   ├── factories.html          # Factory management page
│   ├── production.html         # Production allocation page
│   ├── market.html             # Sales & pricing page
│   └── turn_overview.html      # Turn summary
└── static/
    └── style.css               # Styling
```

### Design Philosophy

#### 1. **Engine vs Entities Separation**
- **`engine/`**: Contains game mechanics, rules, and data loading
  - `parameters.py`: Loads and provides access to turn-specific configuration from JSON files
  - `world.py`: Coordinates the game simulation, manages turns, and orchestrates game flow
  - `events.py`: Reserved for future random events (currently empty)

- **`entities/`**: Contains pure object classes representing game elements
  - `company.py`: Player/company state (cash, factories, inventory, decisions)
  - `factory.py`: Factory objects with country-specific costs, efficiency, and capacity
  - `product.py`: Product definitions and configuration

This separation keeps business logic distinct from data structures, making the codebase more maintainable and testable.

#### 2. **Data-Driven Configuration**
Game parameters are stored in **JSON files** (`data/parameters/turn_X.json`) rather than hardcoded. Each turn can have different:
- Product pricing options
- Market demand per country
- Available products
- Economic conditions

This approach allows easy balancing and scenario creation without code changes.

#### 3. **Flask Web Interface**
Since the team was **new to web development**, we chose Flask for its simplicity:
- **`main.py`**: Contains all routes and request handlers
- **`templates/`**: HTML pages for each game screen
- **`static/style.css`**: Shared styling

The web interface was **time-consuming to develop** but provides a much better user experience than terminal-based interaction, especially given the complexity of managing multiple variables (factories, production lines, pricing, inventory, etc.).

## Game Mechanics (V0)

### Player Actions Per Turn

#### 1. **Factory Management** (`/factories`)
- Purchase factories in USA, China, or France
- Each country has different setup costs:
  - USA: $10,000 (high efficiency, expensive maintenance)
  - China: $5,000 (lower efficiency, cheap maintenance)
  - France: $8,000 (balanced)
- Each factory has 20 production line capacity

#### 2. **Production Planning** (`/production`)
- Allocate production lines across products (A, B, C)
- Each line produces 100 base units per turn
- Production affected by country efficiency multiplier:
  - USA: 1.5x
  - China: 0.9x
  - France: 1.2x
- Maintenance costs scale with active production lines

#### 3. **Market & Sales** (`/market`)
- Set selling prices for each product in each market
- Price options loaded from turn configuration
- Markets have different demand levels for each product
- Pricing decisions affect sales volume and revenue

#### 4. **Turn Overview** (`/turn_overview`)
- Summary of turn results
- Financial breakdown
- Production output
- Sales performance

### Game Flow
1. Player starts with $100,000 cash
2. Buy factories in desired countries
3. Allocate production lines to products
4. Set prices and marketing budget
5. Submit turn to see results
6. Repeat for next turn

## Technical Details

### Key Classes

**`World`** (engine/world.py)
- Manages game state and turn progression
- Loads parameters via `Parameters` class
- Coordinates all companies (currently just the player)

**`Company`** (entities/company.py)
- Tracks cash, inventory, factories
- Stores production and sales decisions
- Manages turn-specific metrics (revenue, costs)

**`Factories`** (entities/factory.py)
- Country-specific configuration
- Production line allocation
- Capacity and maintenance tracking

**`Parameters`** (engine/parameters.py)
- Loads all `turn_X.json` files at startup
- Provides turn data on demand
- Falls back to latest turn if requested turn doesn't exist

### Data Flow
1. Player interacts with HTML forms
2. Flask routes handle form submissions
3. Routes update `Company` objects
4. Turn processing applies game rules
5. Results displayed on turn overview page

## Why V0 Took Time

### Web Development Learning Curve
The team had **no prior web development experience**, which made this version a significant learning process:
- Understanding Flask routing and templating
- Managing state between page requests
- Form handling and data validation
- CSS layout and responsive design

### Complexity of Simulation
Managing the number of variables required for a complete game turn proved too complex for a simple terminal script:
- Multiple factories per country
- Production lines per product per factory
- Pricing per product per market
- Inventory tracking
- Cost calculations (maintenance, production, transport, taxes)

### Achievement
Despite the challenges, **V0 successfully allows testing** of the complete gameplay loop:
- ✅ Buy factories
- ✅ Allocate production
- ✅ Set prices and marketing
- ✅ Process turn and see results

## Running the Project

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
```

Then navigate to `http://localhost:5000` in your browser.

## Next Steps (Future Versions)
- Implement AI opponents with different strategies
- Enable turn progression system
- Add random events (market crashes, demand shifts, etc.)
- Implement transport costs between countries
- Add more sophisticated market dynamics
- Improve UI/UX based on playtesting

## Notes
- This is a **learning project** - code may not follow all best practices
- Focus was on **getting a working prototype** rather than perfect architecture
- The modular design sets a foundation for future expansion
- Web interface choice validated - much better than terminal interaction for this type of game

---

**Version:** 0.1 (First Playable)  
**Status:** Basic single-player functionality complete  
**Branch:** feature/V0_prof_commentee
