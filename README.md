# Campaign Management Tool
www.justndev.xyz <-- Available here
## Description
A Full Stack Campaign Management Tool built with:
- Backend: FastAPI (Python)
- Database: PostgreSQL
- Frontend: React with Next.js (TypeScript)
---
### Features
- User registration and authentication
- Create campaign
- View created campaigns
- View particular campaign data and related payouts
- Delete campaign
- Toggle campaign status
- Filter campaigns by search keyword or/and status
---
## Database
Below are illustrated tables defined using SQLAchemy and pedantic libraries in python backend, where "rel." stands for relationship with another table.
### User
- id
- username
- hashed_password
### Campaign
- id
- title
- url
- is_active
- user_id
- (rel.) user
### Provider
- id
- name
### Placement
- id 
- country
- imp_price_in_eur
- provider_id
- (rel.) provider
### Payout
- id
- total_imp
- to_pay_in_eur
- user_id
- campaign_id
- placement_id
- (rel.) user
- (rel.) campaign
- (rel.) placement
---
## Frontend
Frontend is developed with React, Next.js. States are operated by Redux. Moreover, management section is required authorization in order to be visited.
### Project structure
```
src/
├── app/               # Pages
├── components/        # Reusable UI components
├── api/               # Backend integration (Axios)
├── hooks/             # Theme setup for MUI
├── utils/             # Constants, helper functions, TypeScript types
└── config.ts          # Backend IP and app config
```
---
### Libraries
- Material UI - UI components library
- Redux - State management
- Axios - HTTP requests
- React Spring - Animations
- Next.js - Framework
---
### Routes
Public
- / - homepage
- /faq - FAQ page
- /contacts - decorative form to ask question
- /terms - decorative terms and conditions
- /privacy-policy - decorative privacy policy

Protected
- /management/my-campaigns - CMT main page with campaigns list
- /management/my-campaigns/start-new - To create new campaign
- /management/my-campaigns/campaign?id=[id] - To show particular campaign data, delete campaign or change its active status
- /management/my-statistics - Supposed to be displaying payouts data
---
### UX/UI
- Some parts of application were designed before frontend development as UI/UX guideline to simplify it
- [Figma Design Link](https://www.figma.com/design/p9qc1nAlK1nBw7z5j0v3ZQ/Campaign-Management-Tool-UI-Design?node-id=461-56&t=vxWZbqO3NRmNy3gT-0)
- The app use Material UI that provides ready to use UI components with customization
---
## Backend
### Libraries
- fastapi - Backend framework
- uvicorn - Server
- sqlalchemy - ORM
- psycopg2-binary - PostgreSQL driver
- python-jose[cryptography] - JWT
- passlib[bcrypt] - Password hashing
- pydantic- Data validation and serialization
- python-dotenv - Environmental variables
- pytest - Testing framework
---
### Project structure
```
.
├── app/
│   ├── api/
│   │   ├── routes/        # Authentication & campaign endpoints
│   │   └── deps.py        # Dependency: get current user
│   ├── config.py
│   ├── db/                # Database models and setup
│   ├── main.py            # App entrypoint
│   ├── schemas/           # Pydantic models (types/payloads)
│   └── services/          # CRUD logic
├── requirements.txt       # Python dependencies
├── run.py                 # App runner
└── tests/
    ├── conftest.py        # Test setup and fixtures
    ├── test_auth.py       # Authentication tests
    ├── test_crud.py       # Campaign-related tests
    └── test_security.py   # JWT & password hashing tests
```
---
### Endpoints
- /api/auth/register - Create user providing nickname and password, returns 200 or 400
- /api/auth/login - Login user, returns jwt token
---
### Tests
Test suit runs with python3 test.py command and will conduct 4 tests regarding the authorization and 5 tests for CMT functionality.
To run:
```bash
source ./venv/bin/activate
python3 test.py
```
---
### GitHub workflow
There is a script which will run tests and updates the server backend app, which will be triggered on commit and requires IP and secret key.
## Local launch
### Frontend
```bash
git clone https://github.com/justndev/cmt-frontend.git
cd cmt-frontend
npm install
npm run dev
```
### Backend
An empty databased required.
Below is a command to create providers and placements.
```bash
INSERT INTO providers (name, created_at) VALUES 
('Google Ads', NOW()),
('Facebook Ads', NOW()),
('Mega Ads', NOW()),
('YouTube Ads', NOW()),
('Telegram Ads', NOW());

INSERT INTO placements (country, imp_price_in_eur, provider_id, created_at) VALUES 
('United States', 750, 1, NOW()),        -- Google Ads, $0.75 equivalent
('Germany', 650, 1, NOW()),             -- Google Ads, $0.65 equivalent
('United Kingdom', 700, 2, NOW()),       -- Facebook Ads, $0.70 equivalent
('France', 600, 2, NOW()),              -- Facebook Ads, $0.60 equivalent
('Canada', 550, 3, NOW()),              -- Mega Ads, $0.55 equivalent
('Australia', 800, 3, NOW()),           -- Mega Ads, $0.80 equivalent
('Japan', 900, 4, NOW()),               -- YouTube Ads, $0.90 equivalent
('Brazil', 400, 4, NOW()),              -- YouTube Ads, $0.40 equivalent
('India', 300, 5, NOW());               -- Telegram Ads, $0.30 equivalent
```
Set up environmental variables:
```
DATABASE_URL=
SECRET_KEY=
```
```bash
git clone https://github.com/justndev/cmt-backend.git
cd cmt-backend
python -m venv venv
source venv/bin/activate # On Windows: venv/scripts/activate
pip install -r requirements.txt
python3 run.py
```
