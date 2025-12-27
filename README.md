# Business Simulation Game

## Overview
A turn-based business simulation game where players compete against AI opponents to build factories, manage production, and sell products in a dynamic global market.

## Project Structure

### Core Files
- `main.py` - Flask web application with all routes and game logic
- `engine/` - Game engine components
  - `world.py` - Main game coordinator (turn resolution, sales, AI actions)
  - `market_generator.py` - Dynamic market conditions generator
  - `parameters.py` - Turn data manager with caching
  - `AI_manager.py` - AI behavior system (5 personality types)
  - `events.py` - Reserved for future random events
- `entities/` - Game entities
  - `company.py` - Company class (player and AI)
  - `factory.py` - Factory management with country configurations
  - `product.py` - Product configurations
- `templates/` - HTML pages
- `static/` - CSS styling

## Game Flow

### 1. Initialization (`start.html`)
- Configure company name, number of turns, and AI opponents (0-10)
- Initialize world with default cash ($10M per company)

### 2. Factory Phase (`factories.html`)
- Purchase factories in USA, China, or France
- Each country has unique characteristics:
  - **USA**: Expensive but highly efficient (×1.5 production)
  - **China**: Cheap with moderate efficiency (×0.9 production)
  - **France**: Balanced cost and efficiency (×1.2 production)

### 3. Production Phase (`production.html`)
- Allocate production lines across factories
- Each factory has 20-line capacity
- Three products available: A (low-cost), B (standard), C (luxury)
- Real-time cost and production calculations

### 4. Market Phase (`market.html`)
- Set selling prices for each product
- Choose target country for sales
- View demand forecasts per market
- Dynamic economic events affect prices and demand

### 5. Overview & End Turn (`turn_overview.html`)
- Review sales results and rankings
- See competitor sales performance
- Execute turn resolution (production → maintenance → sales)

### 6. Game Over (`game_over.html`)
- Final rankings by cash
- Option to restart

## Technical Features

### AI System
Five distinct AI personalities:
- **Aggressive**: High expansion, low prices, focuses on product A
- **Balanced**: Moderate strategy across all areas
- **Conservative**: Low expansion, high prices, focuses on luxury products
- **Premium**: Quality-focused, high-margin strategy
- **Volume**: Mass production, very low prices

### Market Dynamics
Four economic phases:
1. **Stability** (turns 1-2): Steady conditions
2. **Growth** (turns 3-60%): Expanding markets with random booms/dips
3. **Recession** (60-80%): Challenging conditions
4. **Recovery** (80-100%): Market stabilization

### AJAX Features
- Real-time production line adjustments
- Auto-save market decisions
- Dynamic cost calculations
- No page refreshes during gameplay

## Installation & Running

### Requirements
```bash
pip install flask
```

### Launch
```bash
python main.py
```

Then open browser to: `http://localhost:5000`

## Game Mechanics

### Sales Resolution
- Lowest price wins in each market
- Limited by available stock and market demand
- Multiple companies can sell if demand exceeds supply
- Unsold inventory carries to next turn

### Costs
- **Factory Setup**: $25K-$40K (country-dependent)
- **Production Lines**: $80-$130 per line (country-dependent)
- **Maintenance**: Per-line cost multiplied by active lines

### Victory Condition
Company with highest cash after all turns wins.

## Code Documentation
All functions and classes include English docstrings explaining their purpose. Key design patterns:
- **MVC Architecture**: Clear separation between routes (Controller), templates (View), and entities (Model)
- **Caching**: Turn data cached to avoid regeneration
- **Factory Pattern**: Country configurations and AI behaviors
- **Observer Pattern**: Real-time UI updates via AJAX

## Future Enhancements (Planned)
- Random events (pandemics, trade wars)
- Marketing campaigns
- Transport and tax cost calculations
- Product quality variations
