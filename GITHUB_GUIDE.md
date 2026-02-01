# How to Push GraphQuery AI to GitHub

Follow these steps to upload your project to GitHub.

## 1. Initialize a Git Repository
Open your terminal in the project folder (`graphdb`) and run:
max lines: 50
```bash
git init
```

## 2. Create a `.gitignore` File
Ensure you don't upload sensitive keys or large files. Your `.gitignore` should look like this (already created):
```
.env
__pycache__/
.DS_Store
venv/
.streamlit/secrets.toml
```

## 3. Stage and Commit Files
Add your files to the staging area and commit them:
```bash
git add .
git commit -m "Initial commit: GraphQuery AI with Neo4j & LangChain"
```

## 4. Create a Repository on GitHub
1. Go to [GitHub.com](https://github.com/new).
2. Create a new repository name (e.g., `graphquery-ai`).
3. Do **not** initialize with README/license (since you already have them locally).

## 5. Link and Push
Replace `<YOUR_USERNAME>` with your GitHub username:
```bash
# Add the remote repository
git remote add origin https://github.com/<YOUR_USERNAME>/graphquery-ai.git

# Push to the main branch
git branch -M main
git push -u origin main
```

## 6. (Optional) Requirements
Ensure your `requirements.txt` is up to date before pushing:
```bash
pip freeze > requirements.txt
```
