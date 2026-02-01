# Deployment Guide

This guide covers deploying your Neo4j NLP Query application to Streamlit Cloud.

## Prerequisites

- GitHub account
- Streamlit Cloud account (free at [share.streamlit.io](https://share.streamlit.io))
- Neo4j AuraDB instance (free tier available)
- Groq API key (free at [console.groq.com](https://console.groq.com))

## Step 1: Prepare Your Repository

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/neo4j-nlp-query.git
   git push -u origin main
   ```

2. **Ensure .gitignore is working**
   - Verify that `.env` is not committed
   - Check that sensitive data is excluded

## Step 2: Set Up Neo4j AuraDB

1. Go to [neo4j.com/cloud/aura](https://neo4j.com/cloud/aura/)
2. Create a free AuraDB instance
3. Note down:
   - Connection URI (e.g., `neo4j+s://xxxxx.databases.neo4j.io`)
   - Username (default: `neo4j`)
   - Password (save this securely!)

4. **Load sample data** (run in Neo4j Browser):
   ```cypher
   LOAD CSV WITH HEADERS FROM
   'https://raw.githubusercontent.com/tomasonjo/blog-datasets/main/movies/movies_small.csv' as row
   
   MERGE(m:Movie{id:row.movieId})
   SET m.released = date(row.released),
       m.title = row.title,
       m.imdbRating = toFloat(row.imdbRating)
   FOREACH (director in split(row.director, '|') | 
       MERGE (p:Person {name:trim(director)})
       MERGE (p)-[:DIRECTED]->(m))
   FOREACH (actor in split(row.actors, '|') | 
       MERGE (p:Person {name:trim(actor)})
       MERGE (p)-[:ACTED_IN]->(m))
   FOREACH (genre in split(row.genres, '|') | 
       MERGE (g:Genre {name:trim(genre)})
       MERGE (m)-[:IN_GENRE]->(g))
   ```

## Step 3: Get Groq API Key

1. Visit [console.groq.com](https://console.groq.com)
2. Sign up for a free account
3. Navigate to API Keys section
4. Create a new API key
5. Copy and save it securely

## Step 4: Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub

2. **Create New App**
   - Click "New app"
   - Select your repository: `yourusername/neo4j-nlp-query`
   - Branch: `main`
   - Main file path: `app.py`
   - App URL: Choose a custom URL (e.g., `neo4j-query-yourname`)

3. **Configure Secrets**
   Click "Advanced settings" → "Secrets"
   
   Add the following in TOML format:
   ```toml
   NEO4J_URI = "neo4j+s://xxxxx.databases.neo4j.io"
   NEO4J_USERNAME = "neo4j"
   NEO4J_PASSWORD = "your-password"
   GROQ_API_KEY = "your-groq-api-key"
   ```

4. **Deploy**
   - Click "Deploy!"
   - Wait for deployment (usually 2-3 minutes)
   - Your app will be live at `https://your-app-name.streamlit.app`

## Step 5: Verify Deployment

1. Visit your app URL
2. Click "Connect to Database"
3. Try example queries
4. Verify results are displaying correctly

## Step 6: Update README

Update your README.md with the live link:

```markdown
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-name.streamlit.app)

**[Try the Live App →](https://your-app-name.streamlit.app)**
```

## Troubleshooting

### App Won't Start

**Issue**: App fails to start
**Solution**: Check logs in Streamlit Cloud dashboard
- Verify all secrets are set correctly
- Ensure requirements.txt has all dependencies
- Check Python version compatibility

### Database Connection Failed

**Issue**: "Connection failed" error
**Solution**: 
- Verify Neo4j AuraDB is running
- Check URI format includes `neo4j+s://` prefix
- Confirm credentials are correct
- Check AuraDB firewall settings (should allow all IPs for Streamlit)

### Groq API Errors

**Issue**: "API key invalid" or rate limit errors
**Solution**:
- Verify API key is correct
- Check Groq dashboard for usage limits
- Ensure no extra spaces in the key

### Module Import Errors

**Issue**: `ModuleNotFoundError`
**Solution**:
- Add missing package to `requirements.txt`
- Verify package names are correct
- Check for version conflicts

## Alternative Deployment Options

### Option 1: Docker Container

```bash
docker build -t neo4j-nlp-query .
docker run -p 8501:8501 --env-file .env neo4j-nlp-query
```

### Option 2: Heroku

1. Create `Procfile`:
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. Deploy:
   ```bash
   heroku create your-app-name
   heroku config:set NEO4J_URI=your-uri
   heroku config:set NEO4J_USERNAME=neo4j
   heroku config:set NEO4J_PASSWORD=your-password
   heroku config:set GROQ_API_KEY=your-key
   git push heroku main
   ```

### Option 3: AWS/GCP/Azure

See individual platform documentation for deploying containerized applications.

## Maintenance

### Updating the App

1. Make changes locally
2. Test thoroughly
3. Commit and push:
   ```bash
   git add .
   git commit -m "Update: description of changes"
   git push origin main
   ```
4. Streamlit Cloud will auto-deploy

### Monitoring

- Check Streamlit Cloud dashboard for:
  - App uptime
  - Error logs
  - Resource usage
  - User analytics

### Security Best Practices

- ✅ Never commit `.env` file
- ✅ Use Streamlit Secrets for credentials
- ✅ Rotate API keys periodically
- ✅ Monitor API usage
- ✅ Keep dependencies updated

## Getting Help

- Streamlit Community: [discuss.streamlit.io](https://discuss.streamlit.io)
- Neo4j Community: [community.neo4j.com](https://community.neo4j.com)
- Groq Documentation: [console.groq.com/docs](https://console.groq.com/docs)

## Next Steps

1. Add custom domain (Streamlit Cloud paid plans)
2. Implement analytics
3. Add authentication
4. Create API endpoints
5. Add more example queries

---

**Congratulations!** 🎉 Your app is now live and ready to impress recruiters!