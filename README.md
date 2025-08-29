# X Affiliate Marketing Platform

An automated social media posting and affiliate marketing application for X (Twitter) with support for multiple NSFW niches.

## Features

- 🚀 **Automated Tweet Scheduling**: Schedule and post tweets automatically
- 📊 **Analytics Dashboard**: Track performance, clicks, and revenue
- 🔗 **Affiliate Link Tracking**: UTM parameter tracking and click analytics
- 🎯 **Multi-Niche Support**: MILF/Breeding, Teen, Trans/Femboy/Gay/Bisexual
- 🔄 **A/B Testing**: Test different content variations
- 🐳 **Docker Ready**: Easy deployment with Docker
- 🎨 **Modern UI**: React with TypeScript and Tailwind CSS

## Tech Stack

### Frontend
- React 18 with TypeScript
- Tailwind CSS for styling
- React Router for navigation
- Heroicons for icons
- Vite for build tooling

### Backend
- Flask (Python)
- SQLAlchemy for database ORM
- Tweepy for X API integration
- APScheduler for tweet scheduling
- Flask-CORS for cross-origin requests

### Infrastructure
- Docker for containerization
- SQLite for development (PostgreSQL for production)
- Environment-based configuration

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- Docker (optional)
- X Developer Account with API keys

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd x-plat-affmark
   ```

2. **Install frontend dependencies**
   ```bash
   npm install
   ```

3. **Install backend dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your X API credentials
   ```

5. **Run the application**
   
   **Option A: Development mode**
   ```bash
   # Terminal 1: Start backend
   cd backend
   python app.py
   
   # Terminal 2: Start frontend
   npm run dev
   ```
   
   **Option B: Docker**
   ```bash
   docker-compose up --build
   ```

### X API Setup

1. Create a X Developer account at [developer.twitter.com](https://developer.twitter.com)
2. Create a new app and generate API keys
3. Add the following to your `.env` file:
   ```
   X_API_KEY=your_api_key
   X_API_SECRET=your_api_secret
   X_ACCESS_TOKEN=your_access_token
   X_ACCESS_TOKEN_SECRET=your_access_token_secret
   X_BEARER_TOKEN=your_bearer_token
   ```

## Usage

### Dashboard
- View overall performance metrics
- Monitor recent tweet activity
- Track top-performing affiliate links

### Campaigns
- Create and manage marketing campaigns
- Set posting schedules and frequency
- Configure niche-specific content

### Content Management
- Create tweet templates for different niches
- Manage affiliate links and UTM tracking
- A/B test different content variations

### Analytics
- Track click-through rates and conversions
- Monitor revenue by niche and campaign
- Analyze posting time performance

### Settings
- Configure X API credentials
- Set posting schedules and time zones
- Manage user accounts and permissions

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout

### Campaigns
- `GET /api/campaigns` - List campaigns
- `POST /api/campaigns` - Create campaign
- `PUT /api/campaigns/:id` - Update campaign
- `DELETE /api/campaigns/:id` - Delete campaign

### Tweets
- `GET /api/tweets` - List tweets
- `POST /api/tweets` - Schedule tweet
- `PUT /api/tweets/:id` - Update tweet
- `DELETE /api/tweets/:id` - Delete tweet

### Analytics
- `GET /api/analytics` - Get analytics data
- `GET /api/analytics/campaigns/:id` - Campaign analytics

### Affiliate Links
- `GET /api/affiliate-links` - List affiliate links
- `POST /api/affiliate-links` - Create tracked link
- `GET /api/affiliate-links/:id/stats` - Link statistics

## Development

### Project Structure
```
x-plat-affmark/
├── src/                    # React frontend source
│   ├── components/         # Reusable components
│   ├── pages/             # Page components
│   └── ...
├── backend/               # Flask backend
│   ├── app.py            # Main application
│   ├── requirements.txt   # Python dependencies
│   └── ...
├── public/               # Static assets
├── Dockerfile            # Container configuration
├── docker-compose.yml    # Development environment
└── package.json          # Node.js dependencies
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Deployment

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build manually
docker build -t x-affiliate-platform .
docker run -p 5000:5000 x-affiliate-platform
```

### Production Considerations

- Use PostgreSQL instead of SQLite
- Set up proper environment variables
- Configure reverse proxy (nginx)
- Enable HTTPS
- Set up monitoring and logging
- Configure backup strategies

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue in the repository.