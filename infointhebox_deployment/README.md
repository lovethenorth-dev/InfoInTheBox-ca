# InfoInTheBox.ca - Replit Deployment

Business directory displaying company profiles from SharedAdvertising.ca

## Environment Variables Required

Set these in your Replit Secrets:

```
DATABASE_URL=postgresql://username:password@host:port/database
SESSION_SECRET=your-session-secret-key-here
```

## Features

- Company profile directory display
- Search functionality for profiles
- Clean, responsive design
- Integration with SharedAdvertising.ca database
- SEO-friendly profile pages

## File Structure

- `main.py` - Entry point
- `app.py` - Flask application with routes
- `models.py` - Database models (shared)
- `templates/` - Jinja2 templates
- `static/` - CSS, JS, and image assets

## Deployment Steps

1. Create new Python Repl named "infointhebox-ca"
2. Upload all files from this folder
3. Set environment variables in Secrets
4. Click Run to start the application
5. Use Deployments tab for custom domain setup

## Custom Domain Setup

After deployment:
1. Go to Deployments → Settings → Custom Domains
2. Add "infointhebox.ca"
3. Get A record and TXT record from Replit
4. Configure DNS in your domain provider

## Integration

This application displays company profiles created in SharedAdvertising.ca:
- Profiles are accessed via `/profile/{slug}` URLs
- Search functionality across company names and descriptions
- Real-time data sync through shared database